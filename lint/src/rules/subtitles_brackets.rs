use crate::types::{LintError, Subtitle};
use phf::phf_map;

static BRACKET_OPEN_TO_CLOSE: phf::Map<char, char> = phf_map! {
    '(' => ')',
    '[' => ']',
    '{' => '}',
    '«' => '»',
};

static BRACKET_OPEN: [char; 4] = ['(', '[', '{', '«'];
static BRACKET_CLOSE: [char; 4] = [')', ']', '}', '»'];

pub fn lint_subtitles_brackets(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    for (idx, sub) in subs.iter().enumerate() {
        let mut stack = Vec::new();
        for ch in sub.text.chars() {
            if BRACKET_OPEN.contains(&ch) {
                stack.push(ch);
            } else if BRACKET_CLOSE.contains(&ch) {
                if let Some(open) = stack.pop() {
                    if BRACKET_OPEN_TO_CLOSE[&open] != ch {
                        errors.push(LintError::new(
                            track_id.to_string(),
                            format!(
                                "{}: mismatched brackets: {:?}: {:?} / {:?}",
                                idx + 1,
                                sub.text,
                                open,
                                ch
                            ),
                        ));
                    }
                } else {
                    errors.push(LintError::new(
                        track_id.to_string(),
                        format!(
                            "{}: unmatched closing bracket: {:?}: {:?}",
                            idx + 1,
                            sub.text,
                            ch
                        ),
                    ));
                }
            }
        }

        if !stack.is_empty() {
            errors.push(LintError::new(
                track_id.to_string(),
                format!(
                    "{}: unmatched opening bracket: {:?}: {:?}",
                    idx + 1,
                    sub.text,
                    stack
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
    fn test_lint_subtitles_brackets() {
        let track_id = "test_track";

        // Test with matching brackets (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Normal line".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "Line with (parentheses)".to_string(),
                top: false,
            },
            Subtitle {
                start: 2.0,
                end: 3.0,
                text: "Line with [brackets]".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with unmatched opening bracket
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Line with (unclosed".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("unmatched opening bracket"));

        // Test with unmatched closing bracket
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Line with extra)".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("unmatched closing bracket"));

        // Test with mismatched bracket types
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Line with (wrong]".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("mismatched brackets"));

        // Test with nested matching brackets (should pass)
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Line with (nested [brackets])".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with multiple bracket types (should pass)
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Test (round) [square] {curly} «angle»".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_brackets(track_id, &subs);
        assert_eq!(errors.len(), 0);
    }
}
