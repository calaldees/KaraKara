# KaraKara Linter

Automatically spot issues with the karakara database.

## Usage

```bash
cargo run -- check --processed /path/to/processed
```

```bash
cargo run -- serve --port 8080 --host 0.0.0.0
```

## API Endpoints

When running as a web service:

- `GET /lint` - Returns JSON array of lint errors
- `GET /health` - Health check endpoint


## Development

- tests: `cargo test`
- lint: `cargo clippy`
- format: `cargo fmt`
