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

"""