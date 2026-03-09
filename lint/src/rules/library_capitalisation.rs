use crate::types::LintError;
use std::collections::{HashMap, HashSet};

pub fn lint_library_capitalisation(all_tags: &HashMap<String, HashSet<String>>) -> Vec<LintError> {
    let mut errors = Vec::new();

    for (k, vs) in all_tags.iter() {
        let mut v_by_lower: HashMap<String, String> = HashMap::new();
        for v in vs {
            let vl = v.to_lowercase();
            // BoA and Boa are different, Bis, bis, and BiS are different bands
            if k == "artist" && (vl == "boa" || vl == "bis") {
                continue;
            }

            if let Some(existing) = v_by_lower.get(&vl) {
                if existing != v {
                    errors.push(LintError::new(
                        "library".to_string(),
                        format!("Tag {}:{} has inconsistent capitalization", k, v),
                    ));
                }
            } else {
                v_by_lower.insert(vl, v.clone());
            }
        }
    }

    errors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lint_library_capitalisation_consistent() {
        let mut all_tags = HashMap::new();
        let mut values = HashSet::new();
        values.insert("Rock".to_string());
        values.insert("Pop".to_string());
        all_tags.insert("genre".to_string(), values);

        let errors = lint_library_capitalisation(&all_tags);
        assert_eq!(errors.len(), 0);
    }

    #[test]
    fn test_lint_library_capitalisation_inconsistent() {
        let mut all_tags = HashMap::new();
        let mut values = HashSet::new();
        values.insert("Rock".to_string());
        values.insert("rock".to_string());
        all_tags.insert("genre".to_string(), values);

        let errors = lint_library_capitalisation(&all_tags);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("genre:"));
        assert!(errors[0].message.contains("inconsistent capitalization"));
    }

    #[test]
    fn test_lint_library_capitalisation_boa_exception() {
        let mut all_tags = HashMap::new();
        let mut values = HashSet::new();
        values.insert("BoA".to_string());
        values.insert("Boa".to_string());
        all_tags.insert("artist".to_string(), values);

        let errors = lint_library_capitalisation(&all_tags);
        assert_eq!(
            errors.len(),
            0,
            "BoA and Boa should be treated as different artists"
        );
    }

    #[test]
    fn test_lint_library_capitalisation_bis_exception() {
        let mut all_tags = HashMap::new();
        let mut values = HashSet::new();
        values.insert("BiS".to_string());
        values.insert("bis".to_string());
        values.insert("Bis".to_string());
        all_tags.insert("artist".to_string(), values);

        let errors = lint_library_capitalisation(&all_tags);
        assert_eq!(
            errors.len(),
            0,
            "BiS, bis, and Bis should be treated as different artists"
        );
    }

    #[test]
    fn test_lint_library_capitalisation_non_artist() {
        let mut all_tags = HashMap::new();
        let mut values = HashSet::new();
        values.insert("Anime".to_string());
        values.insert("anime".to_string());
        all_tags.insert("category".to_string(), values);

        let errors = lint_library_capitalisation(&all_tags);
        assert_eq!(
            errors.len(),
            1,
            "Non-artist tags should not have exceptions"
        );
    }
}
