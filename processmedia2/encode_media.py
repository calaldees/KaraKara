"""

    consume for
     - update tags
     - extract lyrics
     - encode media


    ENCODE (queue consumer)
        listen to queue
        -Encode-
        Update meta destination hashs
        -CLEANUP-
        prune unneeded files from destination
        trigger importer

choose encode type
 - video
 - video + sub
 - video + audio
 - image + sub + audio

input hashs cmp output hash

encode hi-res
 - normalize audio
 - normalize subtitles
   - srt to ssa
   - rewrite playres
   - remove dupes
   - add next line


preview encode
gen thumbnail images
extract subs


"""