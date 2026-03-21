use crate::types::LintError;
use phf::{phf_set, Set};
use std::collections::HashMap;

static KNOWN_USES: Set<&'static str> = phf_set! {
    "opening", "ending", "insert", "character", "doujin", "trailer"
};

pub fn lint_tags_use(track_id: &str, tags: &HashMap<String, Vec<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    if let Some(uses) = tags.get("use") {
        for use_val in uses {
            if !KNOWN_USES.contains(use_val.as_str()) {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("weird use:{} tag", use_val),
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
    fn test_lint_tags_use() {
        let track_id = "test_track";

        // Test with no use tags
        let tags = HashMap::new();
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with valid known uses
        let mut tags = HashMap::new();
        tags.insert(
            "use".to_string(),
            vec!["opening".to_string(), "ending".to_string()],
        );
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 0);

        // Test with unknown use value
        tags.insert("use".to_string(), vec!["unknown_use".to_string()]);
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("weird use:unknown_use"));
    }
}
