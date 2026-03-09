use crate::types::{LintError, Subtitle};

pub fn lint_subtitles_random_topline(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    let top_count = subs.iter().filter(|s| s.top).count();
    let bot_count = subs.len() - top_count;

    if bot_count > top_count && top_count > 0 && top_count < 3 {
        let top_texts: Vec<_> = subs
            .iter()
            .filter(|s| s.top)
            .map(|s| format!("{:?}", s.text))
            .collect();
        errors.push(LintError::new(
            track_id.to_string(),
            format!("random topline: {}", top_texts.join(", ")),
        ));
    }

    if top_count > bot_count && bot_count > 0 && bot_count < 3 {
        let bot_texts: Vec<_> = subs
            .iter()
            .filter(|s| !s.top)
            .map(|s| format!("{:?}", s.text))
            .collect();
        errors.push(LintError::new(
            track_id.to_string(),
            format!("random bottomline: {}", bot_texts.join(", ")),
        ));
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_subtitles_random_topline() {
        let track_id = "test_track";

        // Test with all bottom lines (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Line 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Line 2".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_random_topline(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with random topline (1-2 top lines among many bottom lines)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Bottom 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Top 1".to_string(),
                top: true,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Bottom 2".to_string(),
                top: false,
            },
            Subtitle {
                start: 3.0,
                end: 4.0,
                text: "Bottom 3".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_random_topline(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("random topline"));

        // Test with random bottomline (1-2 bottom lines among many top lines)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Top 1".to_string(),
                top: true,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Bottom 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Top 2".to_string(),
                top: true,
            },
            Subtitle {
                start: 3.0,
                end: 4.0,
                text: "Top 3".to_string(),
                top: true,
            },
        ];
        let errors = lint_subtitles_random_topline(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("random bottomline"));

        // Test with balanced lines (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Top 1".to_string(),
                top: true,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Bottom 1".to_string(),
                top: false,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Top 2".to_string(),
                top: true,
            },
            Subtitle {
                start: 3.0,
                end: 4.0,
                text: "Bottom 2".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_random_topline(track_id, &subs);
        assert_eq!(errors.len(), 0);
    }
}
