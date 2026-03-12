use crate::types::{LintError, Subtitle};

pub fn lint_subtitles_chronological(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Check that start times are in chronological order
    for i in 0..subs.len().saturating_sub(1) {
        let l1 = &subs[i];
        let l2 = &subs[i + 1];

        if l2.start < l1.start {
            errors.push(LintError::new(
                track_id.to_string(),
                format!(
                    "subtitles not in chronological order: '{}' (start={:.2}s) comes after '{}' (start={:.2}s)",
                    l1.text, l1.start, l2.text, l2.start
                ),
            ));
        }
    }

    // Check that end times don't come before start times
    for sub in subs {
        if sub.end < sub.start {
            errors.push(LintError::new(
                track_id.to_string(),
                format!(
                    "subtitle end time ({:.2}s) is before start time ({:.2}s): {}",
                    sub.end, sub.start, sub.text
                ),
            ));
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_subtitles_chronological() {
        let track_id = "test_track";

        // Test with proper chronological order (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Line 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.5,
                end: 2.5,
                text: "Line 2".to_string(),
                top: false,
            },
            Subtitle {
                start: 3.0,
                end: 4.0,
                text: "Line 3".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_chronological(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with out of order subtitles (should fail)
        let subs = vec![
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Line 2".to_string(),
                top: false,
            },
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Line 1".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_chronological(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("not in chronological order"));
        assert!(errors[0].message.contains("Line 2"));
        assert!(errors[0].message.contains("Line 1"));

        // Test with end time before start time (should fail)
        let subs = vec![Subtitle {
            start: 2.0,
            end: 1.0,
            text: "Invalid".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_chronological(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("end time"));
        assert!(errors[0].message.contains("before start time"));
    }
}
