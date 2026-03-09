use crate::types::LintError;
use phf::{phf_set, Set};
use std::collections::HashMap;

static KNOWN_USES: Set<&'static str> = phf_set! {
    "opening", "ending", "insert", "character", "doujin", "trailer"
};

pub fn lint_tags_use(track_id: &str, tags: &HashMap<String, Vec<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    if let Some(uses) = tags.get("use") {
        let mut op_tag = None;
        let mut ed_tag = None;

        for use_val in uses {
            // if use_val starts with op or ed followed by a number, set op_tag or ed_tag to that value
            if use_val.starts_with("op") && use_val[2..].chars().all(|c| c.is_digit(10)) {
                op_tag = Some(use_val.clone());
            } else if use_val.starts_with("ed") && use_val[2..].chars().all(|c| c.is_digit(10)) {
                ed_tag = Some(use_val.clone());
            } else if !KNOWN_USES.contains(use_val.as_str()) {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("weird use:{} tag", use_val),
                ));
            }
        }

        if let Some(op_tag) = op_tag {
            if !uses.contains(&"opening".to_string()) {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("use:{} but no use:opening tag", op_tag),
                ));
            }
        }

        if let Some(ed_tag) = ed_tag {
            if !uses.contains(&"ending".to_string()) {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("use:{} but no use:ending tag", ed_tag),
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

        // Test with op tag but no opening tag
        let mut tags = HashMap::new();
        tags.insert("use".to_string(), vec!["op1".to_string()]);
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("use:op1 but no use:opening"));

        // Test with ed tag but no ending tag
        let mut tags = HashMap::new();
        tags.insert("use".to_string(), vec!["ed2".to_string()]);
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("use:ed2 but no use:ending"));

        // Test with op tag WITH opening tag (should pass)
        let mut tags = HashMap::new();
        tags.insert(
            "use".to_string(),
            vec!["op1".to_string(), "opening".to_string()],
        );
        let errors = lint_tags_use(track_id, &tags);
        assert_eq!(errors.len(), 0);
    }
}
