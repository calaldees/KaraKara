# Get Started Adding Tracks

## tl;dr

* If you just want to request or upload a track and have somebody else quality-check / approve it, use https://karakara.uk/upload/

## Overview

- The track database is a collection of files stored in a pair of shared folders (One for work-in-progress tracks, one for finished tracks), currently using Syncthing to synchronise between contributors and the server (Conceptually similar to Dropbox or Google Drive - syncthing is a little fiddlier to set up but gives us a lot more control)
- https://karakara.uk/upload/ will write files into the work-in-progress folder
  - "requests" are uploaded as just a tag file (`.txt`) containing track metadata like title and artist, supplied by the person requesting the track
  - "submissions" are uploaded as a complete set of files for a track (eg `.txt` + `.mp4` + `.srt`)
- A moderator reviews the requests and submissions, edits them if needed, deletes any spam or inappropriate uploads, and moves finished tracks from the "work in progress" folder to the "source" folder (from where the system will automatically pick it up, encode into various formats, and add it to the live database)

## Syncthing Setup

- First, make sure you have a hard drive with enouch space
  - The "Work in Progress" folder rarely goes over 1-2GB, as any finished tracks get moved to Source
  - The "Source" folder is currently around 250GB and growing
- Download and install Syncthing: https://syncthing.net/downloads/
  - The bare tool is fairly minimal and technical, I'd advise using one of the integrations (eg syncthing-macos or syncthing-windows) from the top of the page for a happier experience
- Open syncthing, get the ID for your device from the menu -> "Actions" -> "Show ID"
- Send your device ID to somebody with server access (eg Shish, Calaldees)
- (Person with server access: Go to https://karakara.uk/syncthing/ , add this person's device, and share the `KaraKara - Work in Progress` folder with them)
- At some point soon you should get a notification in the syncthing GUI saying something like "KaraKara wants to share a folder with you: KaraKara-Source [Accept / Reject]" -- if you click accept and choose a folder on your computer, syncthing will start synchronising the files between the server and that folder.

## The Goal

Each track in the database is built from a set of files:

* `Track Name.txt` - a text file containing a set of tags (required)
* `Track Name.srt` - a subtitle file containing the lyrics (optional for hard-subbed videos)
* `Track Name.mkv` - a video + audio file (optional if there's an image + audio)
* `Track Name.ogg` - an audio-only file (optional if there's a video + audio)
* `Track Name.jpg` - an image to show while playing audio-only files (optional if there's a video)

### Variants

If you have multiple versions of a track, eg different languages or vocal styles, you can add variants by adding a descriptor in square brackets to the filename, eg:

* `Track Name.txt`
* `Track Name [Vocal].webm`
* `Track Name [Instrumental].mkv`
* `Track Name [Romaji].srt`
* `Track Name [Kanji].srt`

Note that the different versions need to be compatible (eg, the different audios need to be the same length, don't mix tv-size and full-length edits). If you have multiple incompatible versions of a track, please add them as separate tracks using round brackets, eg:

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
```yaml
category: game
title: Herald of Darkness
from: Alan Wake 2
```

Keys can be repeated, eg for multiple languages:
```yaml
from: Bokusatsu Tenshi Dokuro-chan
from: Bludgeoning Angel Dokuro-chan
```

Keys can be nested, eg for video game franchises:
```yaml
from: Sonic the Hedgehog: Sonic Forces
```

If a value needs to contain a colon, it can be quoted, eg:
```yaml
source: "https://www.example.com/lyrics/song?id=1234"
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
* `added` - the date the track was added to the database, in YYYY-MM-DD format
* `genre` - eg `rock`, `pop`, `electronic`
* `id` - a reference to an external database, eg a MyAnimeList ID for an anime song
  * `id: "mal:12345"` - anime
  * `id: "rawg:1234"` - video game
  * `id: "imdb:tt1234567"` - movie

### Examples
```yaml
category: game
title: Herald of Darkness (Part 1)
from: Alan Wake 2
artist: Old Gods of Asgard
use: insert
lang: en
vocalstyle: male
vocaltrack: on
contributor: Shish
length: short
source: "https://www.youtube.com/watch?v=uxs_HYw_mLk"
date: 2023-11-27
added: 2025-06-06
genre: rock
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
* Try to avoid ambiguous punctuation, eg instead of `Me + You` use `Me and You` (Or `Me plus You` if that's what the singer _actually_ sings)
* Background singer parts can generally be left out, but if it's particularly relevant (eg for an audience sing-along) use round brackets, eg `Let me hear you say Motto Motto! (Motto Motto!)`
* While the subs should generally only contain things to be sung and remove all other information, _sometimes_ it can be useful to add extra bits, eg a fast-paced duet might benefit from having the character names at the start of each line, we use square brackets for this, eg `[Pentious] Egg Boiz, kill that vandal!` / `[Cherri] Hope you like your minions scrambled!`

## Video Files
* Should avoid having baked-in subtitles
* Should avoid having watermarks
* DVD / Bluray "special features" often include creditless OPs/EDs - these are ideal

## Audio Files
* Should be clean (ie if the track comes from a TV show, we don't want to have the voice acting or sound effects in the background)

## Image Files
* If there's no video file, an image file is required to show while playing audio-only tracks
* If there's a video file, an image file is optional - if provided, it will be used as a thumbnail in the track browser, which is useful if the "automatically generate a thumbnail by picking a random frame from the video" algorithm selects a bad frame
