use crate::types::{LintError, Subtitle};
use phf::{phf_set, Set};

// Valid characters in subtitles (in addition to a-z, A-Z, 0-9, and space,
// which are so common that they are hard-coded for speed)
static OK_SUBTITLE_CHARS: Set<char> = phf_set! {
    ',', '.', '!', '?', '\'', '"',
    '[', ']',
    '(', ')',
    '~', '-', '—', '–',
    ':', //';', '/', '+', '*', '&',
    '¿',
    'á', 'ā', 'à',
    'è', 'é',
    'ī', 'í',
    'ō', 'ò', 'ô', 'ó',
    'Ū', 'ú',
    'ñ',
    '\u{2018}', '\u{2019}',
    '\n', // newline isn't allowed, but we have a dedicated rule for that
};

pub fn lint_subtitles_characters(track_id: &str, subs: &[Subtitle]) -> Vec<LintError> {
    let mut errors = Vec::new();

    for (idx, sub) in subs.iter().enumerate() {
        for ch in sub.text.chars() {
            if ch == ' ' || ch.is_ascii_alphanumeric() {
                continue; // Alphanumeric is always fine
            }
            if !OK_SUBTITLE_CHARS.contains(&ch) {
                errors.push(LintError::new(
                    track_id.to_string(),
                    format!(
                        "{}: contains non-alphanumeric: {:?}: {:?} (\\u{:04x})",
                        idx + 1,
                        sub.text,
                        ch,
                        ch as u32
                    ),
                ));
                break; // Only report first bad char per line
            }
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_subtitles_characters() {
        let track_id = "test_track";

        // Test with valid characters (should pass)
        let subs = vec![
            Subtitle {
                start: 0.0,
                end: 1.0,
                text: "Hello world 123".to_string(),
                top: false,
            },
            Subtitle {
                start: 1.0,
                end: 2.0,
                text: "It's okay! (really?)".to_string(),
                top: false,
            },
        ];
        let errors = lint_subtitles_characters(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with valid special characters
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Test: yes, no—maybe? [yeah]".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_characters(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test with invalid character (should fail)
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Test with emoji 😀".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_characters(track_id, &subs);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("non-alphanumeric"));
        assert!(errors[0].message.contains("\\u"));

        // Test with valid accented characters
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Café résumé español".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_characters(track_id, &subs);
        assert_eq!(errors.len(), 0);

        // Test that only first bad character is reported per line
        let subs = vec![Subtitle {
            start: 0.0,
            end: 1.0,
            text: "Bad 😀 and 😎 chars".to_string(),
            top: false,
        }];
        let errors = lint_subtitles_characters(track_id, &subs);
        assert_eq!(errors.len(), 1); // Only reports first bad char
    }
}
