use crate::types::{LintError, Subtitle};

pub fn lint_subtitles_spacing(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Separate top and bottom lines
    let toplines: Vec<_> = subs.iter().filter(|s| s.top).collect();
    let botlines: Vec<_> = subs.iter().filter(|s| !s.top).collect();

    for lines in [toplines, botlines] {
        // Check for overlapping lines
        for i in 0..lines.len().saturating_sub(1) {
            let l1 = lines[i];
            let l2 = lines[i + 1];

            if l2.start < l1.end {
                let gap_ms = ((l1.end - l2.start) * 1000.0) as i32;
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!("{}ms overlapping lines: {} / {}", gap_ms, l1.text, l2.text),
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
    fn test_lint_subtitles_spacing() {
        let track_id = "test_track";

        // Test with proper spacing (should pass)
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
        ];
        let errors = lint_subtitles_spacing(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with overlapping lines (should fail)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 2.0,
                text: "Line 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 3.0,
                text: "Line 2".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_spacing(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("overlapping lines"));
        assert!(errors[0].message.contains("1000ms"));

        // Test with 3+ repeats without gap (should fail)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Repeat".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Repeat".to_string(),
                top: false,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Repeat".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_spacing(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("no gap between 3+ repeats"));

        // Test with 2 repeats without gap (should pass - only 3+ triggers error)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Repeat".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Repeat".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_spacing(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with top and bottom lines separately checked
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Top 1".to_string(),
                top: true,
            },
            Subtitle {
                start: 0.5,
                end: 1.5,
                text: "Top 2".to_string(),
                top: true,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Bottom 1".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_spacing(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("overlapping"));
        assert!(errors[0].message.contains("Top"));
    }
}
