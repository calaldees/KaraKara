Process Media 2
===============

The original processmedia was a very important peice of code. It has facilitated the entire Karaoke system. Without it, the project would not exisit. 

The processing the original does is stable and does what we need. However; since using the system for a period of time, some deficncys in it's use have become apparent. With the new use cases now 'known' we can sketch out the concepts for the next iteration of processmedia.


Current Deficiencies
--------------------

* The souce files are intertwined with the processed media. This makes the entire dataset quite cumbersome. Most users require one or the other, but seldom booth.
* It is difficult to rsync/share/distribute the data because the source files actually move between 3 places during the processing (root, folder, folder/source)
* There is no hashing of source files. Often videos are reprocessed because the mtime has changed but the content has not. We also want the ability to move files based on hash (should they not be in the correct location in all remote places)
* Processing was designed arond one single machine managing the encoding. What if multiple queues/machines/threads could process the data? Reprocessing 1500 videos could do with some muscule.
* Temp and lock files are part of every video. These should be in a global temp space to not contaminate the source data.
* The system should not place automatic tiltes onto the video (first line of an srt file). This title/artist data can be overlayed by the player in realtime.
* Consideration should be made to ensure the source dataset is normalised for fat32 use. This ensures that the lowest common demoninator is catered for. (this was why some of the mtimes of files triggered re-processing).
* When processing is taking palce we want to be able to query it's status. Pending, Processing, ETA's?, Process Log?
* The output data should not need filenames, it can be hashed and treated as one massive blob.
* More global options need to be surfaced and editable. Like subtitle size, font, colours.
* We want the ability to have new mp3 tracks that reference/overdub a video. This will facilitate more vocalless versions of songs without duplicating the source video.
* If source files are simply renamed/moved we should not need to process/unlink the derived files. We should be able to identify them and update our metadata as needed.
* As the derived data will be hashed, we need tooling to:
    * Delete any unneeded files should they not be cateloged
    * Segment the dataset (if a user just want the category:cartoon derived data and not the rest)


Proposed implementation
-----------------------

### Folder structure ###

* Source videos will be in a single folder
    * This makes syncing easyer as we cant have the same files in multiple paths
    * Items are grouped by filename e.g
       * My Name.avi
       * My Name.srt
       * My Name.txt (the tags)
       * My Name.lock (containing timestamp processing was started) [maybe, still        considering simple tracking api to co-ordinate multiple external processors]
       * My Name.yml? (optional additional processing instuctions, maybe linking to another source video)
* Derived meta
    * will be stored as `My Name.json|yml` in a meta folder.
    * Structure
        * Source Files
            * name, mtime, size and hash of each file
        * Source Meta
            * res, aspect, format, length
        * Destinations
            * hash location of thumbnails, hi-res and previews
        * Lyrics
            * Extracted lyrics
        * Tags
* Derived files
    * Hashed filenames (still retaining the file extension of original)
    * Placed in folder names of the first two characters of the hash

source
meta
derived


### Processing ###

1. Source Scan
    * In the event that the mtime has changed, we can perform a deeper hash check to see if reprocessing needs to be done and update our mtime as approritate.
    * We can also use the hash concept to flag missing files from a group or new files to a group. This could help in renaming/moving/deleting as required.
2. Derived Meta
3. Derived Data
    * Delete
    * Slice 

    
* The current concept is to have the video identifyable by it's source video/image hash. That then will have children associated with it (tags, subtiles, overdub). This becomes tickyer when the source video/image is replaced but the child relationship still needs to be upheld.

#### Advanced Optional Features ####
* From logs determin average processing time
* API
    * query queued/pending + why pending (manual, subs changed), processing