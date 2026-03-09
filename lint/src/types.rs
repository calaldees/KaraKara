use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TracksData {
    #[serde(flatten)]
    pub tracks: HashMap<String, Track>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Track {
    pub id: String,
    pub duration: f64,
    pub attachments: HashMap<String, Vec<Attachment>>,
    pub tags: HashMap<String, Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attachment {
    pub variant: String,
    pub mime: String,
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subtitle {
    pub start: f64,
    pub end: f64,
    pub text: String,
    #[serde(default)]
    pub top: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LintError {
    pub track_id: String,
    pub file: Option<String>,
    pub message: String,
}

impl LintError {
    pub fn new(track_id: String, message: String) -> Self {
        Self {
            track_id,
            file: None,
            message,
        }
    }

    pub fn with_file(track_id: String, file: String, message: String) -> Self {
        Self {
            track_id,
            file: Some(file),
            message,
        }
    }
}
