use crate::types::{LintError, Subtitle, Track, TracksData};
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::{Arc, Mutex};

mod library_capitalisation;
mod subtitles_brackets;
mod subtitles_characters;
mod subtitles_exists;
mod subtitles_newlines;
mod subtitles_random_topline;
mod subtitles_spacing;
mod tags_banned;
mod tags_duration;
mod tags_lowercase_keys;
mod tags_lowercase_values;
mod tags_required;
mod tags_source;
mod tags_use;
mod track_aspect_ratio;
mod track_duration;
mod track_hardsubs;
mod track_redundant_audio;
mod track_vocaltrack;

use library_capitalisation::lint_library_capitalisation;
use subtitles_brackets::lint_subtitles_brackets;
use subtitles_characters::lint_subtitles_characters;
use subtitles_exists::lint_subtitles_exists;
use subtitles_newlines::lint_subtitles_newlines;
use subtitles_random_topline::lint_subtitles_random_topline;
use subtitles_spacing::lint_subtitles_spacing;
use tags_banned::lint_tags_banned;
use tags_duration::lint_tags_duration;
use tags_lowercase_keys::lint_tags_lowercase_keys;
use tags_lowercase_values::lint_tags_lowercase_values;
use tags_required::lint_tags_required;
use tags_source::lint_tags_source;
use tags_use::lint_tags_use;
use track_aspect_ratio::lint_track_aspect_ratio;
use track_duration::lint_track_duration;
use track_hardsubs::lint_track_hardsubs;
use track_redundant_audio::lint_track_redundant_audio;
use track_vocaltrack::lint_track_vocaltrack;

pub fn lint_all_tracks(tracks_data: &TracksData, processed_dir: &Path) -> Vec<LintError> {
    lint_all_tracks_with_progress(tracks_data, processed_dir, None::<fn(usize, usize)>)
}

pub fn lint_all_tracks_with_progress<F>(
    tracks_data: &TracksData,
    processed_dir: &Path,
    progress_callback: Option<F>,
) -> Vec<LintError>
where
    F: FnMut(usize, usize) + Send,
{
    let total = tracks_data.tracks.len();

    // Wrap the progress callback in Arc<Mutex<>> for thread-safe access
    let progress = progress_callback.map(|cb| Arc::new(Mutex::new(cb)));
    let counter = Arc::new(Mutex::new(0usize));

    // Lint individual tracks in parallel using rayon.
    // Each track is independent, so we can check them concurrently across all CPU cores.
    // This provides significant speedup on multi-core systems with large track collections.
    let track_errors: Vec<LintError> = tracks_data
        .tracks
        .values()
        .par_bridge()
        .flat_map(|track| {
            let errors = lint_track(track, processed_dir);

            // Update progress if callback exists
            if let Some(ref progress) = progress {
                let mut count = counter.lock().unwrap();
                *count += 1;
                let current = *count;
                drop(count);

                if let Ok(mut callback) = progress.lock() {
                    callback(current, total);
                }
            }

            errors
        })
        .collect();

    // Lint library-wide issues
    let mut errors = track_errors;
    errors.extend(lint_library(&tracks_data.tracks));

    errors
}

fn lint_library(tracks: &HashMap<String, Track>) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Check for inconsistent capitalization of tags across multiple tracks
    // Start by gathering a map of <key>:<set of all values>
    let mut all_tags: HashMap<String, HashSet<String>> = HashMap::new();
    for track in tracks.values() {
        for (k, vs) in &track.tags {
            // Skip title and contact as they're expected to vary
            if k == "title" || k == "contact" {
                continue;
            }
            all_tags.entry(k.clone()).or_default().extend(vs.clone());
        }
    }

    errors.extend(lint_library_capitalisation(&all_tags));

    errors
}

fn lint_track(track: &Track, processed_dir: &Path) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Track-level linting
    errors.extend(lint_track_duration(&track.id, track.duration));
    errors.extend(lint_track_vocaltrack(
        &track.id,
        &track.attachments,
        &track.tags,
    ));
    errors.extend(lint_track_hardsubs(track));
    errors.extend(lint_track_redundant_audio(track));
    errors.extend(lint_track_aspect_ratio(
        &track.id,
        &track.tags,
        &track.attachments,
    ));

    // Tag linting
    errors.extend(lint_tags_required(&track.id, &track.tags));
    errors.extend(lint_tags_banned(&track.id, &track.tags));
    errors.extend(lint_tags_lowercase_keys(&track.id, &track.tags));
    errors.extend(lint_tags_lowercase_values(&track.id, &track.tags));
    errors.extend(lint_tags_use(&track.id, &track.tags));
    errors.extend(lint_tags_source(&track.id, &track.tags));
    errors.extend(lint_tags_duration(&track.id, &track.tags, track.duration));

    // Subtitle linting - load JSON subtitle files
    if let Some(subtitle_attachments) = track.attachments.get("subtitle") {
        for attachment in subtitle_attachments {
            if attachment.mime == "application/json" {
                let subtitle_path = processed_dir.join(&attachment.path);
                if let Ok(content) = std::fs::read_to_string(&subtitle_path) {
                    if let Ok(subtitles) = serde_json::from_str::<Vec<Subtitle>>(&content) {
                        errors.extend(lint_subtitles_exists(&track.id, &subtitles));
                        errors.extend(lint_subtitles_random_topline(&track.id, &subtitles));
                        errors.extend(lint_subtitles_spacing(&track.id, &subtitles));

                        // Only check line contents for non-Hiragana variants
                        if attachment.variant != "Hiragana" {
                            errors.extend(lint_subtitles_newlines(&track.id, &subtitles));
                            errors.extend(lint_subtitles_characters(&track.id, &subtitles));
                            errors.extend(lint_subtitles_brackets(&track.id, &subtitles));
                        }
                    }
                }
            }
        }
    }

    errors
}
