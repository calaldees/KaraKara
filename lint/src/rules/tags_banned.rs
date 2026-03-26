use crate::types::LintError;
use std::collections::HashMap;

pub fn lint_tags_banned(track_id: &str, tags: &HashMap<String, Vec<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    if tags.contains_key("red") {
        errors.push(LintError::new(
            track_id.to_string(),
            "Put track in WorkInProgress folder instead of using 'red' tag".to_string(),
        ));
    }
    if tags.contains_key("date") {
        errors.push(LintError::new(
            track_id.to_string(),
            "Use 'released' instead of 'date' tag".to_string(),
        ));
    }
    if tags.contains_key("") {
        errors.push(LintError::new(
            track_id.to_string(),
            "Avoid empty tag keys. retro->category:retro, hardsubs->subs:hard".to_string(),
        ));
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_tags_banned() {
        let track_id = "test_track";

        // Test with no banned tags
        let mut tags = HashMap::new();
        tags.insert("title".to_string(), vec!["Test Title".to_string()]);
        let errors = lint_tags_banned(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with banned "red" tag
        tags.insert("red".to_string(), vec!["true".to_string()]);
        let errors = lint_tags_banned(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("WorkInProgress"));
    }
}
