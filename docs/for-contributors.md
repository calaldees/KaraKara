# Get Started Adding Tracks

## The Goal

Each track in the database is built from a set of files:

* `Track Name.txt` - a text file containing a set of tags (required)
* `Track Name.srt` - a subtitle file containing the lyrics (optional for hard-subbed videos)
* `Track Name.mkv` - a video + audio file (optional if there's an image + audio)
* `Track Name.ogg` - an audio-only file (optional if there's a video + audio)
* `Track Name.jpg` - an image to show while playing audio-only files (optional if there's a video)

The files are generally named `(category)/(source or artist) - (use) - (title)`, eg:

* `Anime/Your Name - OP - Yume Tourou.txt`
* `JPop/YUI - Rolling Star.txt`

### Variants

If you have multiple versions of a track, eg different languages or vocal styles, you can add variants by adding a descriptor in square brackets to the filename, eg:

* `Track Name.txt`
* `Track Name [Vocal].webm`
* `Track Name [Instrumental].mkv`
* `Track Name [Romaji].srt`
* `Track Name [Kanji].srt`

Note that the different versions need to be compatible (eg, the different audios need to be the same length, don't mix tv-size and full-length edits). If you have multiple incompatible versions of a track, please add them as separate tracks, eg:

* `Track Name (TV-Size).txt`
* `Track Name (TV-Size).mkv`
* `Track Name (TV-Size).srt`
* `Track Name (Full).txt`
* `Track Name (Full).mkv`
* `Track Name (Full).srt`

### Examples

The majority of tracks have a tags file, a video, and a subtitle file

* `Sonic Forces - Fist Bump.txt`
* `Sonic Forces - Fist Bump.mp4`
* `Sonic Forces - Fist Bump.srt`

## Tag Files

Mostly key:value pairs, eg:
```
category:game
title:Herald of Darkness
from:Alan Wake 2
```

Keys can be repeated, eg for multiple languages:
```
from:Bokusatsu Tenshi Dokuro-chan
from:Bludgeoning Angel Dokuro-chan
```

Can be nested if we want to group eg all the Sonic games together:
```
from:Sonic the Hedgehog:Sonic Forces
```
which is equivalent to
```
from:Sonic the Hedgehog
Sonic the Hedgehog:Sonic Forces
```

If a value needs to contain a colon, it can be quoted, eg:
```
source:"https://www.example.com/lyrics/song?id=1234"
```

Keys and Values should generally both be lowercase, except for proper nouns like titles and artist names.

### Required Tags
* `category` - eg `anime`, `game`, `jpop`, `oddballs`. Try to use existing categories if possible, if there's no suitable category, stick it in `oddballs` for now, and then we can create a new category later if there are multiple tracks within `oddballs` with the same theme.
* `title` - the name of the track
* `vocaltrack` - whether the audio track has vocals (as opposed to being an instrumental karaoke-edit): `on`, `off`

### Recommended Tags
* `from` - where the track is known from, eg the anime or game it appears in
* `artist` - the performer of the track
* `use` - how the track is intended to be used, eg `insert`, `opening`, `ending`
* `lang` - the language of the track, using two-character codes, eg `en`, `jp`
* `vocalstyle` - the vocal style of the track, eg `male`, `female`, `group`, `duet`
* `contributor` - your name or nickname, so we can credit you for adding the track
* `length` - the version of the track, eg most anime openings or endings are 1m30s, but full versions are often 4m or longer, so we can use `short` for the TV-size version, and `full` for the full-length version
* `source` - a URL where the track can be found, eg a YouTube link
* `date` - the date the track was released, in YYYY-MM-DD format
* `added` - the date the track was added to the database, in YYYY-MM-DD
* `genre` - eg `rock`, `pop`, `electronic`

### Examples
```
category:game
title:Herald of Darkness (Part 1)
from:Alan Wake 2
artist:Old Gods of Asgard
use:insert
lang:en
vocalstyle:male
vocaltrack:on
contributor:Shish
length:short
source:"https://www.youtube.com/watch?v=uxs_HYw_mLk"
date:2023-11-27
added:2025-06-06
genre:rock
```

## Subtitle Files
* SRT files, personally I'm a fan of [Aegisub](https://aegisub.org/) for editing subtitles but anything which creates SRT files is fine
* Don't do anything fancy - no formatting, no animation, no mid-line timings, no "[instrumental break]" markers, no preview of the next line -- the input `.srt` file should _only_ contain the timings for the lyrics at the moment that they are being sung, and the system will take care of the rest automatically
* Every track should have at-least western characters (eg, English or Romaji text), if you have other languages (eg. Japanese hiragana / katakana / kanji, Korean hangul), add those as a variant, eg:
```
My Track.txt
My Track [Romaji].srt
My Track [Kanji].srt
```
* Currently supported formats: `.srt` is strongly recommended, `.ssa` and `.ass` are supported but often contain extra formatting which will break things

## Video Files
* Should avoid having baked-in subtitles
* Should avoid having watermarks
* DVD / Bluray "special features" often include creditless OPs/EDs - these are ideal
* Currently supported formats: `.mp4`, `.mkv`, `.avi`, `.mpg`, `.webm`
  * Adding new formats is easy - if you have a file in a different format, please ask us to add that format to the list rather than converting it

## Audio Files
* Currently supported formats: `.mp3`, `.flac`, `.ogg`, `.aac`
  * Adding new formats is easy - if you have a file in a different format, please ask us to add that format to the list rather than converting it

## Image Files
* If there's no video file, an image file is required to show while playing audio-only tracks
* If there's a video file, an image file is optional - if provided, it will be used as a thumbnail in the track browser, which is useful if the "automatically generate a thumbnail by picking a random frame from the video" algorithm selects a bad frame
* Currently supported formats: `.jpg`, `.png`, `.webp`, `.avif`
