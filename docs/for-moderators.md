# Get Started Moderating the Track Database

## Overview

- The track database is a collection of files stored in a shared folder, currently using Syncthing to synchronise between contributors and the server (Conceptually similar to Dropbox or Google Drive - syncthing is a little fiddlier to set up but gives us a lot more control)
- https://karakara.uk/upload/ will write files into the shared folder
  - "requests" are uploaded as just a tag file (`.txt`) containing track metadata like title and artist, supplied by the person requesting the track - these will go into `KaraKara-Source/WorkInProgress/Requests`
  - "submissions" are uploaded as a complete set of files for a track (eg `.txt` + `.mp4` + `.srt`) - these will go into `KaraKara-Source/WorkInProgress/Submissions`
- A moderator reviews the requests and submissions, edits them if needed, deletes any spam or inappropriate uploads, and moves finished tracks into the main database (eg anime tracks get moved into `KaraKara-Source/Anime/`)
- As a moderator you also have the power to skip the whole "upload" system and write files directly into the shared folder, but it can still be useful to get a second pair of eyes to check for typos and such


## Syncthing Setup

- First, make sure you have a hard drive with enouch space (200GB and counting)
- Download and install Syncthing: https://syncthing.net/downloads/
  - The bare tool is fairly minimal and technical, I'd advise using one of the integrations (eg syncthing-macos or syncthing-windows) from the top of the page for a happier experience
- Open syncthing, get the ID for your device from the menu -> "Actions" -> "Show ID"
- Send your device ID to somebody with server access (eg Shish, Calaldees)
- (Person with server access: Go to https://karakara.uk/syncthing/ , add this person's device, and share the `KaraKara-Source` folder with them)
- At some point soon you should get a notification in the syncthing GUI saying something like "KaraKara wants to share a folder with you: KaraKara-Source [Accept / Reject]" -- if you click accept and choose a folder location on your computer, syncthing will start synchronising the files between the server and that folder.
