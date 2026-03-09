use crate::types::{Attachment, LintError};
use std::collections::{HashMap, HashSet};

pub fn lint_track_vocaltrack(
    track_id: &str,
    attachments: &HashMap<String, Vec<Attachment>>,
    tags: &HashMap<String, Vec<String>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Get all variants from attachments
    let variants: HashSet<String> = attachments
        .values()
        .flat_map(|atts| atts.iter().map(|a| a.variant.clone()))
        .collect();

    let vocaltrack = tags.get("vocaltrack").cloned().unwrap_or_default();

    if variants.contains("Vocal") && !vocaltrack.contains(&"on".to_string()) {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Vocal variant but no vocaltrack:on tag".to_string(),
        ));
    }

    if variants.contains("Instrumental") && !vocaltrack.contains(&"off".to_string()) {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Instrumental variant but no vocaltrack:off tag".to_string(),
        ));
    }

    errors
}
