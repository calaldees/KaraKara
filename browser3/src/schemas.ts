/**
 * This file was auto-generated from openapi.yaml
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
      "anyOf": [
        {
          "type": "number",
          "format": "float"
        },
        {
          "type": "null"
        }
      ],
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
  "properties": {
    "title": {
      "type": "string",
      "description": "Room title",
      "default": "KaraKara"
    },
    "track_space": {
      "type": "number",
      "format": "float",
      "description": "Gap between tracks (seconds)",
      "default": 15
    },
    "hidden_tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Tags to hide from display",
      "default": [
        "red:duplicate"
      ]
    },
    "forced_tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Tags that must be present",
      "default": []
    },
    "preview_volume": {
      "type": "number",
      "format": "float",
      "minimum": 0,
      "maximum": 1,
      "description": "Preview playback volume (0.0 - 1.0)",
      "default": 0.1
    },
    "coming_soon_track_count": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9,
      "description": "Number of upcoming tracks to show publicly",
      "default": 5
    },
    "validation_event_start_datetime": {
      "anyOf": [
        {
          "type": "string",
          "format": "date-time"
        },
        {
          "type": "null"
        }
      ],
      "description": "Event start time"
    },
    "validation_event_end_datetime": {
      "anyOf": [
        {
          "type": "string",
          "format": "date-time"
        },
        {
          "type": "null"
        }
      ],
      "description": "Event end time"
    },
    "auto_reorder_queue": {
      "type": "boolean",
      "description": "Whether to automatically reorder the queue",
      "default": false
    }
  }
} as const;

export const schemas = {
  Track: TrackSchema,
  Attachment: AttachmentSchema,
  Subtitle: SubtitleSchema,
  QueueItem: QueueItemSchema,
  Settings: SettingsSchema,
} as const;
