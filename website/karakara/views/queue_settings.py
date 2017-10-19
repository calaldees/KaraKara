"""
Settings to migrate from registry

karakara.system.user.readonly = False -> bool

karakara.event.end                       = -> datetime

karakara.player.title                          = KaraKara (dev player)
karakara.player.video.preview_volume           =  0.10   -> float
karakara.player.video.skip.seconds             = 20      -> int
karakara.player.queue.update_time              = 0:00:03 -> timedelta
karakara.player.help.timeout                   =  2      -> int

karakara.queue.group.split_markers = [0:10:00, 0:20:00] -> timedelta
karakara.queue.track.padding       = 0:00:60 -> timedelta

karakara.queue.add.limit                     = 0:10:00 -> timedelta
karakara.queue.add.limit.priority_token      = 0:00:00 -> timedelta
karakara.queue.add.limit.priority_window     = 0:01:00 -> timedelta
karakara.queue.add.duplicate.track_limit     = 2       -> int
karakara.queue.add.duplicate.time_limit      = 1:00:00 -> timedelta
karakara.queue.add.duplicate.performer_limit = 1       -> int
karakara.queue.add.valid_performer_names = [] -> list

karakara.template.input.performer_name = 
karakara.template.title                = KaraKara (dev)
karakara.template.menu.disable =

karakara.search.view.config = data/config/search_config.json
karakara.search.tag.silent_forced = []
karakara.search.tag.silent_hidden = []
karakara.search.template.button.list_tracks.threshold = 100 -> int
karakara.search.list.threshold = 25 -> int
karakara.search.list.alphabetical.threshold = 90 -> int
karakara.search.list.alphabetical.tags = [from, artist]

"""