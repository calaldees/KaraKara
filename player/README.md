An HTML5/Javascript full screen player for the queued items

Design for low res projector of 1024x768
800x600 would be useful but not necessary

Spec:
- After track completed playing
  - if http://pyramid_server/ avalable
    - track complete - trackid
    - que.json to update local queue
    -
  - if unavalable
    - remove track from local queue (need some way to sync when pyramid resumes)
    - proceed with track order
- display info screen
  - Next track      + name + previews (audio off) or just images
  - current state of next 5 in queue with time estimates
  - highlight expireing tracks
  - 'name' let us know your still want to sing 'track'
  - screen should advance on admin click (longer term we could have auto timeout)
- play video fullscreen

Items in queue may not be video items - concept is to queue notices or other custom types to display/handle in future
  
  
Suggestion:
Player should be developed for compatability initially on one cross platform browser type e.g chrome, firefox, opera


symlinks:
 - lib.js
 - jquery.min.js
