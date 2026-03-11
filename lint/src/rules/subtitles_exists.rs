use crate::types::{LintError, Subtitle};

pub fn lint_subtitles_exists(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    if subs.is_empty() {
        errors.push(LintError::new(
            track_id.to_string(),
            "no subtitles".to_string(),
        ));
    } else if subs.len() == 1 {
        errors.push(LintError::new(
            track_id.to_string(),
            format!("only one subtitle: {}", subs[0].text),
        ));
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_subtitles_exists() {
        let track_id = "test_track";

        // Test with empty subtitles
        let subs: Vec<Subtitle> = vec![];
        let errors = lint_subtitles_exists(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("no subtitles"));

        // Test with only one subtitle
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Single line".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_exists(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("only one subtitle"));
        assert!(errors[0].message.contains("Single line"));

        // Test with multiple subtitles (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "First line".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Second line".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_exists(track_id, &subs);
        assert_eq!(errors.len(), 0);
    }
}
