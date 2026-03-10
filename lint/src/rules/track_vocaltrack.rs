use crate::types::{Attachment, LintError};
use std::collections::HashMap;

pub fn lint_track_vocaltrack(
    track_id: &str,
    attachments: &HashMap<String, Vec<Attachment>>,
    tags: &HashMap<String, Vec<String>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    let vocaltrack = tags.get("vocaltrack").cloned().unwrap_or_default();

    // Check for Vocal variant (small number of variants, iterator is more efficient than HashSet)
    let has_vocal = attachments
        .values()
        .flat_map(|atts| atts.iter())
        .any(|a| a.variant == "Vocal");

    if has_vocal && !vocaltrack.contains(&"on".to_string()) {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Vocal variant but no vocaltrack:on tag".to_string(),
        ));
    }

    // Check for Instrumental variant
    let has_instrumental = attachments
        .values()
        .flat_map(|atts| atts.iter())
        .any(|a| a.variant == "Instrumental");

    if has_instrumental && !vocaltrack.contains(&"off".to_string()) {
        errors.push(LintError::new(
            track_id.to_string(),
            "has Instrumental variant but no vocaltrack:off tag".to_string(),
        ));
    }

    errors
}
