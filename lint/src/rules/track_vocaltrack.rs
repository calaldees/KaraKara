use crate::types::{Attachment, LintError};
use std::collections::HashMap;

pub fn lint_track_vocaltrack(
    track_id: &str,
    attachments: &HashMap<String, Vec<Attachment>>,
    tags: &HashMap<String, Vec<String>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    let video_variants = attachments
        .get("video")
        .unwrap_or(&vec![])
        .iter()
        .map(|a| a.variant.clone())
        .collect::<Vec<String>>();
    let vocaltrack = tags.get("vocaltrack").cloned().unwrap_or_default();

    // If we have a Vocal variant, we should have vocaltrack:on
    let has_vocal = video_variants.contains(&"Vocal".to_string());
    let has_vocaltrack_on = vocaltrack.contains(&"on".to_string());

    if has_vocal && !has_vocaltrack_on {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Vocal variant but no vocaltrack:on tag".to_string(),
        ));
    }

    // If we have an Instrumental variant, we should have vocaltrack:off
    let has_instrumental = video_variants.contains(&"Instrumental".to_string());
    let has_vocaltrack_off = vocaltrack.contains(&"off".to_string());

    if has_instrumental && !has_vocaltrack_off {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Instrumental variant but no vocaltrack:off tag".to_string(),
        ));
    }

    // vocaltrack:on can have Vocal or Default variants
    // vocaltrack:off can have Instrumental or Default variants
    // If we have both vocaltrack:on AND vocaltrack:off, we should have both Vocal and Instrumental variants
    if has_vocaltrack_on && has_vocaltrack_off && (!has_vocal || !has_instrumental) {
        errors.push(LintError::new(
            track_id.to_string(),
            "has both vocaltrack:on and vocaltrack:off tags, but does not have Vocal and Instrumental variants"
                .to_string(),
        ));
    }

    errors
}
