use crate::types::LintError;

/// Check for tracks that are unusually long (> 10 minutes)
pub fn lint_track_duration(track_id: &str, duration: f64) -> Vec<LintError> {
    let mut errors = Vec::new();

    if duration > 10.0 * 60.0 {
        errors.push(LintError::new(
            track_id.to_string(),
            format!("is very long ({}m)", (duration as i32) / 60),
        ));
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_short_track() {
        let errors = lint_track_duration("test_id", 180.0); // 3 minutes
        assert!(errors.is_empty());
    }

    #[test]
    fn test_exactly_ten_minutes() {
        let errors = lint_track_duration("test_id", 600.0); // exactly 10 minutes
        assert!(errors.is_empty());
    }

    #[test]
    fn test_long_track() {
        let errors = lint_track_duration("test_id", 720.0); // 12 minutes
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("is very long"));
        assert!(errors[0].message.contains("12m"));
    }
}
