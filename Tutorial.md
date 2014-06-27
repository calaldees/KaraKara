Tutorial
========

This documenation is designed to inform a user how to setup a karaoke event
system from scratch. Technical developer documentation about each component
can be found with each component.

The goals KaraKara:
 * Provide users with an accessible web interface to:
   * Prepare/encode video/subtitles/images (refered to as 'datasets')
   * Run a karaoke event.
 * Support a comunity of video contibutors.


Machine setup
-------------

This project is built on top of linux based open source tools.
Windows operating systems users can run an automated virtual linux machine after
installing a few tools.

*Windows and Mac can be used for `localhost` trials but would not be suitable for a live deployment*

### Linux Setup ###


Preparing a Dataset
-------------------

This section describes how to subtilte a track and prepare it for use with the
system. These instructions provide links to pre constructed videos and subtile
files to get you started.


Event Setup
-----------

* Server setup
* Router setup


System Operation
----------------

### Settings ###


#### Event ####
* `karakara.event.end` (datetime)
	* Will prevent tracks being queued past the stated endtime. 
	* This prevent 20+ tracks being in the queue when an organiser turns off the projector and says 'Shows over' and thus leaving many disapointed attendees.
	* Strongly recomended this is always set for each event.

#### Features ####
* `karakara.faves.enabled` (bool)
	* Allow a 'favorate' button on each track.
	* Once a user has favorated at least one track, a new option becomes avalable on the main menu. A list of the favorated tracks.
	* By default this is `False` as this is an additional complication for the users with no real long term benefit for a short event.

#### Projector Interface (player) #####
* `karakara.player.title`
	* The title displayed on the projector interface
* `karakara.player.video.preview_volume` (float)
	* The volume the projector previews track when displaying the queue screen.
* `karakara.player.video.skip.seconds` (int)
	* When using the skip buttons on the remote control or keyboard will jump this many seconds.
* `karakara.player.queue.update_time` (timedelta)
	* The time between poll refreshs. 
	* Not used in normal operation as the projector will have a websocket connection.
* `karakara.player.help.timeout` (int)
	* Time in seconds for the popup help to display when the mouse is moved
* `karakara.websocket.disconnected_retry_interval` (int)
	* Number of seconds to attempt a websocket reconnect if the connection fails

#### Queue Management ####
* `karakara.queue.group.split_markers` (list of timedelta)
	* An array of timedeltas to split/obscure tracks
	* Currently only 2 markers are supported
		+ Queue order obfusacation
			* The queue length that will start to randomise the order of tracks
		+ Queue Limit
			* The maximum length of queueable tracks (note that users can still be given priority tokens beyond this, see karakara.???)
	* Examples
		* `[0:15:00, 0:30:00]`
			* Queue items after 15 minuets obfuscate the order of tracks on both the mobile client and projector. 
			* Queue items after 30 minuets are never displayed. (NEED TO CHECK THIS BEHAVIOUR)
* `karakara.queue.track.padding` (timedelta)
	* When a performer finishs singing, the next track dosnt start immediatly. There needs to be some time for the new perform to take the mic and be ready.
	* This time is added to the end of any track played to predict a possible start time for the next track. This gives a more accurate aproximation of queue length.
	* If your attendees are organised and the next performing is always there ready, you may want to set this to 15 seconds. If there is lots of faffing, confustion, or regular cases where performers need to be found, you may want this to be increased to 3 minuets.
* `karakara.queue.add.limit` (timedelta)
	* A queue length limit that users queueing new tracks will be rejected.
	* Administrators are never limted by this. This has to be understoon by admins as attendees may cotton on and regulary bypass the mobile queue to sing song quicker.
	* If priority tokens are allowed then rather than being outright rejected, mobile clients may be added a priority token.
* `karakara.queue.add.limit.priority_token` (timedelta)
	* The queue length limit where no more priority tokens will be given. This is under heavy demand where we dont want hours of tracks queued.
	* A sensible value for this may be 1 hour. Most people are willing to wait 1 hour for a chance to sing, but 2 hours? 3 hours? is probably not worth the wait.
* `karakara.queue.add.limit.priority_window` (timedelta)
	* The time allocated for each priority token slot. 
	* This should be estimated as the average track length + padding time to change performers.
	* For example: If lots of 80's cartoon short intro's are being sung, then a window of 2mins will give time for the track and time for the change. If lots of epic progressive metal tracks are being sung then maybe 8min is appropriate on average.
	* Because the system can hold a huge number of tracks from differtn generes with differnt lengths, this is a human configurable setting and should be at the administrators judgement. Failire to set this correctly will result in the priority token system becoming unfair and unnesable. e.g
		* Too long, means only a few priority tokens are issued and other attendees  find that if they keep franticly requesting tracks that they eventually get through in a gap.
		* Too short, a huge number of priority tokens are issued and used, leading to the queue length swelling byond the maximum queue length.
	* It is also worth noting that not all users actually follow through with using there priority token. This may be due to users not understanding the concept, seeing the long wait time and just wondering off. The priority_window should be set to consider this possibility and frequency.
* `karakara.queue.add.duplicate.count_limit` (int)
	* The number of duplicate tracks to allow in a time period (see below)
* `karakara.queue.add.duplicate.time_limit` (timedelta)
	* The time period to enforce the duplication count
	* E.g count_limit = 2 and time_limit = 1:00:00 means 'Pokemon' can only be queued twice per hour.
	* The calculation is done on the time since the tracks were last played
	* E.g if Pokemon was queued at 7:00 and then again at 7:30, the next time the track could be added would be 8:00
	* (Feature note: it is in the todo list to inform users of the time it will be addable again)
* `karakara.queue.add.duplicate.performer_limit` (int)
	* The number of times a perfomer can queue a track in the time_limit
	* This is linked to badge name. If the admins have not setup a known 'known_performer_name_list' then users will just add names like 'MyName2' or even worse 'I can put whatever I like as my name and you cant stop me queing 1 million tracks bwarahahahahah'.

#### Mobile Interface ####
* `karakara.system.user.readonly` (bool)
	* Mobile clients can browse but not queue tracks.
	* Useful for if the audience are abusing the queue options and the organisers want to accept face to face submissions.
* `karakara.template.input.performer_name`
	* The text to display in the 'performer name' input box.
	* E.g. `Performer name`, `Enter Badge name`, `Enter performer code`
* `karakara.template.title`
	* The title at the top of every mobile screen
* `karakara.template.menu.disable`
	* If present, will disable the mobile client interface and replace it with this message for all users.
	* This is used to still have the admin/projector functionally accessible via the wireless but do not permit any more user access.

#### Search ####

* `karakara.search.view.config` (json_filename)
 	* A felxible system to customise how tags are browsed
	* A json file containing details of tags to show for differnt search paths
	* `%(here)s/search_config.json`
	* E.g looking at the example below
		* The first search browse screen shows a list of all `category`, `vocalstyle`, `vocaltrack` and `lang` as separate titled menus with counts on each of the items. e.g. `lang` might look like:
			* en (52)
			* jp (12)
			* fr (5)
		* Once `anime`, `jdrama`, etc is selected the next menu will only list the `from` tag (again in alphabetical order with totals by each item)
		* `jpop` shows an `artist` list (with totals) and a `from` list with totals.
		* If another item is selected e.g. `en` from the language category; the system displays the `root` list of tags again but the totals will be adjusted to filter only tracks with `en`
	* Alternate example
		* We may want our `root` config to show `genre` and `year`. If the approriate tags are in place this would give us a menu of `rock`, `pop`, `jazz`, etc with totals, as well as `70's`, `80's`, `90's`, etc. `lang` might not be relevent for some events. Thats why the browse flow is customiable.

-
		
	{
	    "root"            : ["category","vocalstyle","vocaltrack","lang"],
	    "category:anime"  : ["from"],
	    "category:jdrama" : ["from"],
	    "category:game"   : ["from"],
	    "category:cartoon": ["from"],
	    "category:jpop"   : ["artist","from"]
	}


	
* `karakara.search.tag.silent_forced` (list)
	* Force a tag to always be silently added to any browse query.
	* e.g. this could be set to `retro` to only allow a specific subset of retro tracks. 
	* `[retro, year:80s]`
* `karakara.search.tag.silent_hidden` (list)
	* Tags to hide in tag browser.
	* e.g. hide all tracks tags with `broken`
	* `[broken, incomplete]`
* `karakara.search.list.threshold` (int)
	* If a linear list of tracks is encountered that is over this value, the system will swich to the tag browser.
	* e.g performing a keyword search for the word `the` could result in 100's of entries and return a list of 600 tracks to the mobile client. This would totally overload lower powered devices. Instead, in these circumstances, the system will degrade back to the `root` tag browser to allow the search to be refined until it is a useable value
* `karakara.search.template.button.list_tracks.threshold` (int)
	* a button to 'show all tracks currently in search' is visible for search counts lower than this value. This is again to protect users from on the first screen seeing 'show all' and crashing there tiny device.
* `karakara.search.list.alphabetical.tags`
	* Some tags when viewed should be browsed in an segmented alphabetical list
	* e.g. a list of `a`, `b`, `c`, that when tapped reveal the items beggining with `a`, etc.
	* `[from, artist]`
* `karakara.search.list.alphabetical.threshold` (int)
	* If viewing an alphabetical list (`from` or `artist` if using the previous example), if the list is small enough, we could just show all of them in alphabetical order. It would be odd if there were 20 items and most of the letters has zero counts.
	* e.g a value of `90` would provide a list that isnt too big for most devices, before swiching to the segmented letter list. 

#### Print ####

* `karakara.print_tracks.fields` (list)
	* A list of fields to display when printing the tracklist
	* `[category, from, use, title, artist]`


#### System ####
* `karakara.websocket.port` (int)
	* For sysadmins and server setup