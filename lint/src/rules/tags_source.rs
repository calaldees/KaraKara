use crate::types::LintError;
use std::collections::HashMap;

pub fn lint_tags_source(track_id: &str, tags: &HashMap<String, Vec<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    if let Some(sources) = tags.get("source") {
        if sources.contains(&"http".to_string()) || sources.contains(&"https".to_string()) {
            errors.push(LintError::new(
                track_id.to_string(),
                "appears to have an unquoted URL in the source tag".to_string(),
            ));
        }
    }

    if let Some(ids) = tags.get("id") {
        for id_value in ids {
            if !id_value.contains(':') {
                errors.push(LintError::new(
                    track_id.to_string(),
                    "appears to have an unquoted ID in the id tag".to_string(),
                ));
            }
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_tags_source() {
        let track_id = "test_track";

        // Test with no source tags
        let tags = HashMap::new();
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with valid source tags
        let mut tags = HashMap::new();
        tags.insert(
            "source".to_string(),
            vec!["\"https://example.com\"".to_string()],
        );
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with unquoted URL in source tag
        tags.insert("source".to_string(), vec!["http".to_string()]);
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("unquoted URL"));

        // Test with unquoted https URL in source tag
        let mut tags = HashMap::new();
        tags.insert("source".to_string(), vec!["https".to_string()]);
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("unquoted URL"));

        // Test with valid id tags (with colon)
        let mut tags = HashMap::new();
        tags.insert("id".to_string(), vec!["youtube:abc123".to_string()]);
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with unquoted ID (no colon)
        tags.insert("id".to_string(), vec!["abc123".to_string()]);
        let errors = lint_tags_source(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("unquoted ID"));
    }
}
