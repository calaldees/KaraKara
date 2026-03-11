use crate::types::LintError;
use std::collections::HashMap;

/**
 * Base keys should be lowercase, subkeys can be any case
 */
pub fn lint_tags_lowercase_keys(
    track_id: &str,
    tags: &HashMap<String, Vec<String>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    let mixed_case_values: Vec<String> = tags
        .values()
        .flat_map(|vs| vs.iter().cloned())
        .filter(|v| v != &v.to_lowercase())
        .collect();

    for key in tags.keys() {
        let lower_key = key.to_lowercase();
        if key != &lower_key && !mixed_case_values.contains(key) {
            errors.push(LintError::new(
                track_id.to_string(),
                format!("{} key which is not lowercase", key),
            ));
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_tags_lowercase_keys() {
        let track_id = "test_track";

        // Test with all lowercase keys
        let mut tags = HashMap::new();
        tags.insert("title".to_string(), vec!["Test Title".to_string()]);
        tags.insert("artist".to_string(), vec!["Test Artist".to_string()]);
        let errors = lint_tags_lowercase_keys(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with uppercase key that is not a mixed-case value
        tags.insert("Category".to_string(), vec!["anime".to_string()]);
        let errors = lint_tags_lowercase_keys(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Category"));
        assert!(errors[0].message.contains("not lowercase"));

        // Test with uppercase key that IS a mixed-case value (should be allowed)
        let mut tags2 = HashMap::new();
        tags2.insert("title".to_string(), vec!["Test Title".to_string()]);
        tags2.insert("Test Title".to_string(), vec!["value".to_string()]);
        let errors = lint_tags_lowercase_keys(track_id, &tags2);
        assert_eq!(errors.len(), 0);
    }
}
