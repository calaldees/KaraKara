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
 

New Feature Suggestions
-----------------------

* Multiple subtitles for single media source (may already be supported?)
  * Japanise symbols and phonetics (forget the names of their 3 alphabets)
  * Instrumental tracks could have english and japanise versions
* Multiple images cycling video generation
* WebM output support


Refactor Considerations
-----------------------

Keep existing script untouched as reference
Build up new refactor from scratch in segments
Each processing step should have automated tests operating on actual media files. This will assert external tools are installed and functional

The output data and videos from the refactor should match the existing reference output as close as possible

Interface with externl tools should be part of separate wrapper module

* argparse


Automated testing

One video consisting of 5 frames of differnt colours. at 1 frame per second
Should be under 512k (this will need to be part of the repo). Maybe once one input format is tested, create others, e.g avi, mkv, rm, mp4 
Subtitle file to go with video
subtitles on frame 1 3 and 5

Tests should run segments of the actual processing engine.
 - json file output can be asserted.
 - video file output can be asserted
It should be possible to run the entire processing suite through with the example media files
When we have a known output from these automated tests, we could actually run it
through the importer script at KaraKara/website/karakara/scripts/import_tracks.py
(which is currently without automated tests because we have no known lightweight inputs)

Media tests
 - extrat meta data from video
   - running time
   - codec
 - render video with subtitles
   - use histogram to ensure frame has colours other than background colour
 - extract images from required positions
   - ensure images are correct size and histogram colour
 - extract audio from video and assert is not null
   - in future we could assert sound compression and normalisation.
 - subtitles should contain unicode characters

named arguments to functions can be passed to aid testing
 examples
 libs/python3/lib/misc.py#491
 KaraKara/website/karakara/views/comunity.py#220
 KaraKara/website/karakara/tests/unit/test_comunity_track.py#81
 KaraKara/website/karakara/views/comunity.py#109
 KaraKara/website/karakara/tests/integration/test_comunity.py#84
 KaraKara/website/karakara/views/comunity.py#60
 libs/python3/lib/test.py#4
 
Assume py.test is installed at the systems level for now
We will create build of python env later
 
Module ideas:
 up to you

