Media will be in all manner of formats and needs to be normalized

(Video + subtitle files) or (audio + image + subtitle files) are diceted into
-Image previews
-Video previews (at low res and in a multitute of formats for differing mobile devices)
-Full video (with subtitles hardcoded, usual at a fixed high res)
-subtitle file (avalable to be processed by pyramid server to present lyrics to mobile users)

Each processed video could be in it's own folder and contain the following JSON for import by the pyramid server. Import will crawl folders recursivly for all JSON files.

(draft)
{
    id       : 'unique_string',
    source   : 'path/filename of origninal',
    duration : seconds,

    previews: [
        {
            url: 'from root',
            target: 'platform target, maybe codec',
            filesize: bytes,
        }
    ],
    
    images: [
        {
            url: ''
            width: int,
            height: int,
            timestamp: seconds,
        }
    ],
    
    subtitles: [
        {
            url: '',
            language: '?',
        }
    ]
    
    processed: [
        {
            url: '',
            width: int,
            height: int,
        }
    ]

}