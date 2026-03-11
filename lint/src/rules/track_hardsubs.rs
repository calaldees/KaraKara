use crate::types::{LintError, Track};

pub fn lint_track_hardsubs(track: &Track) -> Vec<LintError> {
    let mut errors = Vec::new();

    let has_video = track.attachments.contains_key("video");
    let empty_tags = track.tags.get("").cloned().unwrap_or_default();
    let has_hardsubs = empty_tags.contains(&"hardsubs".to_string());
    let has_subtitles = track.attachments.contains_key("subtitle");

    if has_hardsubs && !has_video {
        errors.push(LintError::new(
            track.id.clone(),
            "has hardsubs tag but no video source".to_string(),
        ));
    }

    if !has_subtitles && !has_hardsubs {
        errors.push(LintError::new(
            track.id.clone(),
            "has no subtitles source but also no hardsubs tag".to_string(),
        ));
    }

    errors
}
