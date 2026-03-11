use crate::types::LintError;
use std::collections::HashMap;

// Helper function to parse aspect ratio string (e.g., "16:9" -> (16.0, 9.0))
fn parse_aspect_ratio(ar_str: &str) -> Option<(f64, f64)> {
    let parts: Vec<&str> = ar_str.split(':').collect();
    if parts.len() != 2 {
        return None;
    }

    let width: f64 = parts[0].parse().ok()?;
    let height: f64 = parts[1].parse().ok()?;

    if height == 0.0 {
        return None;
    }

    Some((width, height))
}

pub fn lint_track_aspect_ratio(
    track_id: &str,
    tags: &HashMap<String, Vec<String>>,
    attachments: &HashMap<String, Vec<crate::types::Attachment>>,
) -> Vec<LintError> {
    let mut errors = Vec::new();

    // Check aspect ratio for video/image tracks
    // Allow square-ish (>= 0.95) but flag anything taller (portrait)
    if attachments.contains_key("video") || attachments.contains_key("image") {
        if let Some(aspect_ratios) = tags.get("aspect_ratio") {
            for ar_str in aspect_ratios {
                if let Some((width, height)) = parse_aspect_ratio(ar_str) {
                    let ratio = width / height;
                    // Flag if aspect ratio < 0.95 (taller than square-ish)
                    if ratio < 0.95 {
                        errors.push(LintError::new(
                            track_id.to_string(),
                            format!("has weird aspect ratio {} ({:.2})", ar_str, ratio),
                        ));
                    }
                }
            }
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_aspect_ratio() {
        // Valid aspect ratios
        assert_eq!(parse_aspect_ratio("16:9"), Some((16.0, 9.0)));
        assert_eq!(parse_aspect_ratio("4:3"), Some((4.0, 3.0)));
        assert_eq!(parse_aspect_ratio("1:1"), Some((1.0, 1.0)));
        assert_eq!(parse_aspect_ratio("9:16"), Some((9.0, 16.0)));
        assert_eq!(parse_aspect_ratio("589:330"), Some((589.0, 330.0)));

        // Invalid aspect ratios
        assert_eq!(parse_aspect_ratio("16"), None);
        assert_eq!(parse_aspect_ratio("16:9:10"), None);
        assert_eq!(parse_aspect_ratio("abc:def"), None);
        assert_eq!(parse_aspect_ratio("16:0"), None); // Division by zero
        assert_eq!(parse_aspect_ratio(""), None);
    }

    #[test]
    fn test_aspect_ratio_validation() {
        // Test the ratio calculation
        let (w, h) = parse_aspect_ratio("16:9").unwrap();
        assert!((w / h) > 0.95); // Should pass

        let (w, h) = parse_aspect_ratio("9:16").unwrap();
        assert!((w / h) < 0.95); // Should fail (portrait)

        let (w, h) = parse_aspect_ratio("1:1").unwrap();
        assert!((w / h) >= 0.95); // Should pass (square)

        let (w, h) = parse_aspect_ratio("589:330").unwrap();
        assert!((w / h) > 0.95); // Should pass (widescreen)
    }
}
