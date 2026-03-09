use crate::types::{LintError, Subtitle};

pub fn lint_subtitles_newlines(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    for (idx, sub) in subs.iter().enumerate() {
        if sub.text.contains('\n') {
            errors.push(LintError::new(
                track_id.to_string(),
                format!("{}: contains newline: {}", idx + 1, sub.text),
            ));
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_subtitles_newlines() {
        let track_id = "test_track";

        // Test with no newlines (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Line without newline".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Another line".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_newlines(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with newline in subtitle (should fail)
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Line with\nnewline".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_newlines(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("contains newline"));
        assert!(errors[0].message.contains("Line with"));

        // Test with multiple subtitles with newlines
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "First\nline".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Second\nline".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_newlines(track_id, &subs);
        assert_eq!(errors.len(), 2);
    }
}
