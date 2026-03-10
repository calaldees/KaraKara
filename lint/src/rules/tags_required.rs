use crate::types::LintError;
use phf::{phf_ordered_set, OrderedSet};
use std::collections::HashMap;

static REQUIRED_TAG_KEYS: OrderedSet<&'static str> = phf_ordered_set! {
    "title", "category", "vocaltrack", "lang", "vocalstyle"
};

pub fn lint_tags_required(track_id: &str, tags: &HashMap<String, Vec<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    for key in REQUIRED_TAG_KEYS.iter() {
        if tags.get(*key).is_none_or(|v| v.is_empty()) {
            errors.push(LintError::new(
                track_id.to_string(),
                format!("no {} tag", key),
            ));
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Assert that the errors vector contains at least one error with a message containing the given substring
    macro_rules! assert_err {
        ($errors:expr, $msg:expr) => {
            assert!(
                $errors.iter().any(|e| e.message.contains($msg)),
                "Expected error containing '{}' not found in errors: {:?}",
                $msg,
                $errors.iter().map(|e| &e.message).collect::<Vec<_>>()
            );
        };
    }

    #[test]
    fn test_lint_tags_required() {
        let track_id = "test_track";
        let tags = HashMap::new();

        // Test missing required tags
        let errors = lint_tags_required(track_id, &tags);
        assert_eq!(errors.len(), 5);
        assert_err!(errors, "no title tag");
        assert_err!(errors, "no category tag");
        assert_err!(errors, "no vocaltrack tag");
        assert_err!(errors, "no lang tag");
    }
}
