"""
New static track format
"""

# from config.docker.json - `path_static`
#output to `tracks.json`` ?
test = {
    'BASE64_HASH': {
        'source_filename': '',  # For debugging
        'attachments': [
            {
                'url': 'PATH/BASE64_HASH.mp4',
                'use': 'preview',
                'mime': 'video/mp4',
            },
            ## if you want consistant image order then sort by url-string to get consistent order
        ],
        'duration': 300.0,
        'srt': 'SRT_TEXT',
        'tags': 'TAG_TEXT',  # provide js for translating tag.txt into parent/childs - this is reasonably trivial
    }
}

