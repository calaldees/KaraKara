/**
 * This file was auto-generated from components.yaml
 * Do not make direct changes to the file.
 */

export const TrackSchema = {
  "type": "object",
  "required": [
    "id",
    "duration",
    "tags",
    "attachments"
  ],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique track identifier"
    },
    "duration": {
      "type": "number",
      "format": "float",
      "description": "Track duration in seconds"
    },
    "tags": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "description": "Key-value tags for the track"
    },
    "attachments": {
      "type": "object",
      "required": [
        "video",
        "image",
        "subtitle"
      ],
      "properties": {
        "video": {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/Attachment"
          }
        },
        "image": {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/Attachment"
          }
        },
        "subtitle": {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/Attachment"
          }
        }
      }
    }
  }
} as const;

export const AttachmentSchema = {
  "type": "object",
  "required": [
    "variant",
    "mime",
    "path"
  ],
  "properties": {
    "variant": {
      "type": "string",
      "description": "Attachment variant name"
    },
    "mime": {
      "type": "string",
      "description": "MIME type of the attachment"
    },
    "path": {
      "type": "string",
      "description": "Path to the attachment file"
    }
  }
} as const;

export const SubtitleSchema = {
  "type": "object",
  "required": [
    "start",
    "end",
    "text",
    "top"
  ],
  "properties": {
    "start": {
      "type": "number",
      "format": "float",
      "description": "Start time in seconds"
    },
    "end": {
      "type": "number",
      "format": "float",
      "description": "End time in seconds"
    },
    "text": {
      "type": "string",
      "description": "Subtitle text content"
    },
    "top": {
      "type": "boolean",
      "description": "Whether subtitle appears at top of screen",
      "default": false
    }
  }
} as const;

export const QueueItemSchema = {
  "type": "object",
  "required": [
    "id",
    "track_id",
    "start_time",
    "track_duration",
    "session_id",
    "performer_name",
    "video_variant",
    "subtitle_variant"
  ],
  "properties": {
    "id": {
      "type": "integer",
      "description": "Unique queue item identifier"
    },
    "track_id": {
      "type": "string",
      "description": "ID of the track in the queue"
    },
    "track_duration": {
      "type": "number",
      "format": "float",
      "description": "Track duration in seconds"
    },
    "session_id": {
      "type": "string",
      "description": "Session ID of the user who added this item"
    },
    "performer_name": {
      "type": "string",
      "description": "Name of the performer"
    },
    "start_time": {
      "type": [
        "number",
        "null"
      ],
      "format": "float",
      "description": "Unix timestamp when the track starts playing (null if not yet scheduled)"
    },
    "video_variant": {
      "type": "string",
      "description": "Selected video variant"
    },
    "subtitle_variant": {
      "type": "string",
      "description": "Selected subtitle variant"
    }
  }
} as const;

export const SettingsSchema = {
  "type": "object",
  "required": [
    "title",
    "track_space",
    "hidden_tags",
    "forced_tags",
    "preview_volume",
    "coming_soon_track_count",
    "validation_event_start_datetime",
    "validation_event_end_datetime",
    "auto_reorder_queue"
  ],
  "properties": {
    "title": {
      "title": "Room title",
      "type": "string",
      "default": "KaraKara",
      "minLength": 1,
      "maxLength": 16
    },
    "track_space": {
      "title": "Gap between tracks (seconds)",
      "type": "number",
      "format": "float",
      "default": 15,
      "minimum": 0,
      "maximum": 60
    },
    "hidden_tags": {
      "title": "Tags to hide from display",
      "type": "array",
      "items": {
        "type": "string"
      },
      "default": [
        "red:duplicate"
      ]
    },
    "forced_tags": {
      "title": "Tags that must be present",
      "type": "array",
      "items": {
        "type": "string"
      },
      "default": []
    },
    "preview_volume": {
      "title": "Preview playback volume",
      "type": "number",
      "format": "float",
      "minimum": 0,
      "maximum": 1,
      "multipleOf": 0.01,
      "default": 0.1
    },
    "coming_soon_track_count": {
      "title": "Number of upcoming tracks to show publicly",
      "type": "integer",
      "minimum": 0,
      "default": 5,
      "maximum": 9
    },
    "validation_event_start_datetime": {
      "title": "Event start time",
      "type": [
        "string",
        "null"
      ],
      "format": "date-time",
      "default": null
    },
    "validation_event_end_datetime": {
      "title": "Event end time",
      "type": [
        "string",
        "null"
      ],
      "format": "date-time",
      "default": null
    },
    "auto_reorder_queue": {
      "title": "Auto-Reorder Queue",
      "type": "boolean",
      "default": false
    }
  }
} as const;

export const LintErrorSchema = {
  "type": "object",
  "required": [
    "track_id",
    "message"
  ],
  "properties": {
    "track_id": {
      "type": "string",
      "description": "ID of the track with an error"
    },
    "file": {
      "type": [
        "string",
        "null"
      ],
      "description": "File path related to the error"
    },
    "message": {
      "type": "string",
      "description": "Error message"
    }
  }
} as const;

export const schemas = {
  Track: TrackSchema,
  Attachment: AttachmentSchema,
  Subtitle: SubtitleSchema,
  QueueItem: QueueItemSchema,
  Settings: SettingsSchema,
  LintError: LintErrorSchema,
} as const;
