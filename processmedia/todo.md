Known Bugs
----------

* prepare
  * sanitise input filenames to remove harful characters
    * convert unicode characters to a format windows/fat32/linux/mac are consistent with (for syncing and url retreval)
* process
  * subtitles
    * ssa sizing inconsistent with size of video (higher res videos = tiny subs)
    * Non ascii characters in srt files should be handled gracefully
  * preview
    * preview audio is stereo? (to be verifyed) is inefficent and poor quality (some tracks previews are significantly distorted)
  * flac/m4a audio support (think it's done, just needs testing)
 

Refactor Considerations
-----------------------

* argparse
* modules
* python3 (for consistency - nicity and not not required)


Features
--------

* Multiple subtitles for single media source (may already be supported?)
  * Japanise symbols and phonetics (forget the names of their 3 alphabets)
  * Instrumental tracks could have english and japanise versions
* Multiple images cycling video generation
