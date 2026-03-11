use crate::types::LintError;
use std::collections::HashMap;

pub fn lint_tags_duration(
    track_id: &str,
    tags: &HashMap<String, Vec<String>>,
    duration: f64,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    if duration > 5.0 * 60.0
        && !tags
            .get("length")
            .is_some_and(|v| v.contains(&"full".to_string()))
    {
        errors.push(LintError::new(
            track_id.to_string(),
            format!("is {}s but has no length:full tag", duration as i32),
        ));
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_tags_duration() {
        let track_id = "test_track";
        let tags = HashMap::new();

        // Test short track (under 5 minutes) - should pass
        let errors = lint_tags_duration(track_id, &tags, 240.0);
        assert_eq!(errors.len(), 0);

        // Test long track (over 5 minutes) without length:full tag - should fail
        let errors = lint_tags_duration(track_id, &tags, 360.0);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("360s"));
        assert!(errors[0].message.contains("no length:full tag"));

        // Test long track WITH length:full tag - should pass
        let mut tags = HashMap::new();
        tags.insert("length".to_string(), vec!["full".to_string()]);
        let errors = lint_tags_duration(track_id, &tags, 360.0);
        assert_eq!(errors.len(), 0);

        // Test exactly 5 minutes boundary case
        let tags = HashMap::new();
        let errors = lint_tags_duration(track_id, &tags, 300.0);
        assert_eq!(errors.len(), 0);

        // Test just over 5 minutes boundary
        let errors = lint_tags_duration(track_id, &tags, 301.0);
        assert_eq!(errors.len(), 1);
    }
}
