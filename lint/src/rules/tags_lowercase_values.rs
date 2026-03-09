use crate::types::LintError;
use phf::{phf_set, Set};
use std::collections::HashMap;

static SKIP_LOWERCASE_KEYS: Set<&'static str> = phf_set! {
    "title", "artist", "from", "contributor", "source", "contact", "info", "status"
};

pub fn lint_tags_lowercase_values(
    track_id: &str,
    tags: &HashMap<String, Vec<String>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    let all_values: Vec<String> = tags.values().flat_map(|vs| vs.iter().cloned()).collect();

    for (key, values) in tags {
        if all_values.contains(key) || SKIP_LOWERCASE_KEYS.contains(key.as_str()) {
            continue;
        }

        for value in values {
            let lower_value = value.to_lowercase();
            if value != &lower_value {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("{}:{} should be lowercase", key, value),
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
    fn test_lint_tags_lowercase_values() {
        let track_id = "test_track";

        // Test with all lowercase values (should pass)
        let mut tags = HashMap::new();
        tags.insert("category".to_string(), vec!["anime".to_string()]);
        tags.insert("lang".to_string(), vec!["eng".to_string()]);
        let errors = lint_tags_lowercase_values(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with uppercase value in non-skipped key (should fail)
        tags.insert("category".to_string(), vec!["Anime".to_string()]);
        let errors = lint_tags_lowercase_values(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("category:Anime"));
        assert!(errors[0].message.contains("should be lowercase"));

        // Test with uppercase value in skipped key (should pass)
        let mut tags2 = HashMap::new();
        tags2.insert("title".to_string(), vec!["My Song Title".to_string()]);
        tags2.insert("artist".to_string(), vec!["Artist Name".to_string()]);
        let errors = lint_tags_lowercase_values(track_id, &tags2);
        assert_eq!(errors.len(), 0);

        // Test where value is used as a key (should pass)
        let mut tags3 = HashMap::new();
        tags3.insert("category".to_string(), vec!["anime".to_string()]);
        tags3.insert("anime".to_string(), vec!["value".to_string()]);
        let errors = lint_tags_lowercase_values(track_id, &tags3);
        assert_eq!(errors.len(), 0);
    }
}
