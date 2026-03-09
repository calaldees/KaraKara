use crate::types::{LintError, Track};
use std::collections::HashSet;

pub fn lint_track_redundant_audio(track: &Track) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Check for redundant audio sources when video exists
    let video_variants: HashSet<String> = track
        .attachments
        .get("video")
        .map(|atts| atts.iter().map(|a| a.variant.clone()).collect())
        .unwrap_or_default();

    let audio_variants: HashSet<String> = track
        .attachments
        .get("audio")
        .map(|atts| atts.iter().map(|a| a.variant.clone()).collect())
        .unwrap_or_default();

    let redundant: Vec<_> = video_variants.intersection(&audio_variants).collect();
    if !redundant.is_empty() {
        for variant in redundant {
            errors.push(LintError::new(
                track.id.clone(),
                format!(
                    "has redundant audio source for variant '{}' (video already contains audio)",
                    variant
                ),
            ));
        }
    }

    errors
}
