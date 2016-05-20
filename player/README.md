An HTML5/Javascript full screen player for the queued items

Design for low res projector of 1024x768
800x600 would be useful but not nessisary

Spec:
- After track completed playing
  - if http://pyramid_server/ avalable
    - track complete - trackid
    - que.json to update local que
    -
  - if unavalable
    - remove track from local que (need some way to sync when pyramid resumes)
    - proceed with track order
- display info screen
  - Next track      + name + previews (audio off) or just images
  - current state of next 5 in que with time estimates
  - highlight expireing tracks
  - 'name' let us know your still want to sing 'track'
  - screen should advance on admin click (longer term we could have auto timeout)
- play video fullscreen

Items in que may not be video items - concept is to que notices or other custom types to display/handle in future
  
  
Suggest:
Player should be developed for compatability initially on one cross platform browser type e.g chrome, firefox, opera


sim links:
 - lib.js
 - jquery.min.js
 

acknolege source of images 
 http://findicons.com/icon/552528/connect_icon
 http://findicons.com/icon/552540/message_attention_icon
 
 images encoded with
import base64
with open("icon_disconnected.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    print(encoded_string)
