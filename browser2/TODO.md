One user add two tracks to queue back to back, "error adding to queue" - what error??

identify own tracks properly (by session instead of by name?)

remove own tracks from browser2

if API says "this event is over", notify "this event has finished" + set `queue_id` to null

prompt to install PWA

search by track id

save some state
- `performer_name` (localStorage)
- `version` / `track_list` (localStorage?)
- `bookmarks` (localStorage)

```
karakara.system.user.readonly
karakara.template.menu.disable
karakara.search.list.threshold
karakara.search.template.button.list_tracks.threshold
karakara.search.list.alphabetical.tags (redundant?)
karakara.search.list.alphabetical.threshold
```
notify / block when tracks are already played / already in queue

New features:
- enter room password in GUI instead of via cookie?
- broadcast message
- notify user via app when their song is up now / next
