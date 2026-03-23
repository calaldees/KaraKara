pub mod rules;
pub mod types;

use clap::{Parser, Subcommand, ValueEnum};
use std::path::{Path, PathBuf};

use types::{LintError, TracksData};

#[derive(Debug, Clone, Copy, ValueEnum)]
enum OutputFormat {
    Text,
    Json,
}

#[derive(Parser)]
#[command(name = "kk-lint")]
#[command(about = "Linter for KaraKara processed media files", long_about = None)]
struct Cli {
    /// Path to processed media directory (containing tracks.json)
    #[arg(short, long, default_value = "../media/processed")]
    processed: PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run linter once and output results
    Check {
        /// Output format
        #[arg(short, long, default_value = "text")]
        format: OutputFormat,

        /// Re-run N times
        #[arg(short, long, default_value = "1")]
        bench: usize,
    },
    /// Run as web server
    #[cfg(feature = "server")]
    Serve {
        /// Port to listen on
        #[arg(short = 'P', long, default_value = "3000")]
        port: u16,

        /// Host to bind to
        #[arg(long, default_value = "127.0.0.1")]
        host: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Check { format, bench } => {
            for i in 0..bench {
                if bench > 1 {
                    println!("Run {}/{}:", i + 1, bench);
                }
                run_check(&cli.processed, format);
            }
        }
        #[cfg(feature = "server")]
        Commands::Serve { port, host } => {
            run_server(cli.processed, port, host);
        }
    }
}

fn run_check(processed_dir: &Path, format: OutputFormat) {
    let tracks_path = processed_dir.join("tracks.json");

    let start_time = std::time::Instant::now();
    match load_and_lint(&tracks_path, processed_dir, format) {
        Ok(errors) => {
            let duration = start_time.elapsed();

            if matches!(format, OutputFormat::Json) {
                println!("{}", serde_json::to_string_pretty(&errors).unwrap());
            } else {
                for error in &errors {
                    if let Some(file) = &error.file {
                        println!("{}: {}", file, error.message);
                    } else {
                        println!("{}: {}", error.track_id, error.message);
                    }
                }
                println!("\nTotal errors: {}", errors.len());
                println!("Total runtime: {:.3}s", duration.as_secs_f64());
            }

            //if !errors.is_empty() {
            //    std::process::exit(1);
            //}
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}

fn load_and_lint(
    tracks_path: &Path,
    processed_dir: &Path,
    format: OutputFormat,
) -> Result<Vec<LintError>, String> {
    let content = std::fs::read_to_string(tracks_path)
        .map_err(|e| format!("Failed to read tracks.json: {}", e))?;

    let tracks_data: TracksData = serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse tracks.json: {}", e))?;

    // Use progress bar only in text mode
    if matches!(format, OutputFormat::Text) {
        use indicatif::{ProgressBar, ProgressStyle};

        let start_time = std::time::Instant::now();
        let total = tracks_data.tracks.len() as u64;
        let pb = ProgressBar::new(total);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("[{elapsed_precise}] {bar:40.cyan/blue} {pos}/{len} {msg}")
                .unwrap()
                .progress_chars("=>-"),
        );
        pb.set_message("Scanning tracks...");

        let errors = rules::lint_all_tracks_with_progress(
            &tracks_data,
            processed_dir,
            Some(|current, _total| {
                pb.set_position(current as u64);
            }),
        );

        let duration = start_time.elapsed();
        pb.finish_with_message(format!("Done in {:.3}s", duration.as_secs_f64()));
        Ok(errors)
    } else {
        Ok(rules::lint_all_tracks(&tracks_data, processed_dir))
    }
}

#[cfg(feature = "server")]
fn run_server(processed_dir: PathBuf, port: u16, host: String) {
    use axum::{extract::State, routing::get, Json, Router};
    use tower_http::cors::CorsLayer;

    #[derive(Clone)]
    struct AppState {
        processed_dir: PathBuf,
    }

    let state = AppState { processed_dir };

    let app = Router::new()
        .route("/api/lint/lint", get(get_lint))
        .route("/api/lint/lint/:trackId", get(get_lint_for_track))
        .route("/api/lint/health", get(health_check))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let addr = format!("{}:{}", host, port);
    println!("Server listening on http://{}", addr);

    let runtime = tokio::runtime::Runtime::new().unwrap();
    runtime.block_on(async {
        let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
        axum::serve(listener, app).await.unwrap();
    });

    async fn get_lint(State(state): State<AppState>) -> Json<Vec<LintError>> {
        let tracks_path = state.processed_dir.join("tracks.json");
        let errors = load_and_lint(&tracks_path, &state.processed_dir, OutputFormat::Json)
            .unwrap_or_else(|e| {
                eprintln!("Error loading and linting: {}", e);
                Vec::new()
            });
        Json(errors)
    }

    async fn get_lint_for_track(
        State(state): State<AppState>,
        axum::extract::Path(track_id): axum::extract::Path<String>,
    ) -> Json<Vec<LintError>> {
        let tracks_path = state.processed_dir.join("tracks.json");

        // Load tracks data
        let content = match std::fs::read_to_string(&tracks_path) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("Error reading tracks.json: {}", e);
                return Json(Vec::new());
            }
        };

        let tracks_data: TracksData = match serde_json::from_str(&content) {
            Ok(t) => t,
            Err(e) => {
                eprintln!("Error parsing tracks.json: {}", e);
                return Json(Vec::new());
            }
        };

        // Find the specific track
        let track = match tracks_data.tracks.get(&track_id) {
            Some(t) => t,
            None => {
                // Track not found, return empty array
                return Json(Vec::new());
            }
        };

        // Lint just this track
        let errors = rules::lint_track(track, &state.processed_dir);
        Json(errors)
    }

    async fn health_check() -> &'static str {
        "OK"
    }
}
