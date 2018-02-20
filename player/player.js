/**
 *
 * KaraKara Player Interface
 *
 *
 *
 */
var SETTINGS_DEFAULT = {
	"karakara.player.title"               : "KaraKara",
	"karakara.player.video.preview_volume":  0.2,
	"karakara.player.video.skip.seconds"  : 20,
	"karakara.player.queue.update_time"   :  3 , //Seconds to poll server
	"karakara.player.help.timeout"        :  2,
	"karakara.websocket.port"             : null,
	"karakara.websocket.disconnected_retry_interval": 5, // Seconds to retry websocket in the event of disconnection
	"karakara.event.end": null,
}
if (!getUrlParameter('queue_id')) {
	var msg = 'Required query_string param queue_id missing';
	console.error(msg);
	alert(msg);
}
var URLS = {
	'settings': "/queue/" + getUrlParameter('queue_id') + "/settings.json",
	'queue_items': "/queue/" + getUrlParameter('queue_id') + "/queue_items.json",
	'random_images': "/queue/" + getUrlParameter('queue_id') + "/random_images.json",
}


// Constants ------------------------------------------------------------------

KEYCODE = {
	BACKSPACE: 8,
	ENTER    :13,
	ESCAPE   :27,
	LEFT     :37,
	RIGHT    :39,
	SPACE    :32,
	S        :83,
};


// Variables ------------------------------------------------------------------

// Data
var playlist = [];
var split_indexs = [];

// Timers
var mousemove_timeout;
var interval_queue_refresh;

// Settings Management --------------------------------------------------------
var settings = {};
function init_settings(new_settings) {
	if (!new_settings) {new_settings = {};}
	// Copy relevent new settings into current 'settings' object
	for (setting_key in SETTINGS_DEFAULT) {
		if (setting_key in new_settings) {settings[setting_key] = new_settings[setting_key];}
		else                             {settings[setting_key] = SETTINGS_DEFAULT[setting_key];}
	}
	// Update dom elements based on settings
	$('h1').text(settings["karakara.player.title"]);
	$('#event_end').text(settings["karakara.event.end"]);  // TODO: parse iso datetime correctly
}
init_settings({});
function update_settings(on_updated) {
	$.getJSON(URLS.settings, {}, function(data) {
		console.log(URLS.settings);
		init_settings(data.data.settings);
		if (typeof(on_updated) == "function") {on_updated(data);}
	});
}

// Utils ----------------------------------------------------------------------

function get_chrome_version() {
	try      {return parseInt(window.navigator.appVersion.match(/Chrome\/(\d+)\./)[1], 10);}
	catch(e) {return 0;}
}

function get_attachment(track, type) {
	for(var i=0; i<track.attachments.length; i++) {
		if(track.attachments[i].type == type) {
			return "/files/"+track.attachments[i].location;
		}
	}
	return "";
}

// Queue Updating

function start_queue_poll() {
	if (!interval_queue_refresh) {
		interval_queue_refresh = setInterval(update_playlist, settings["karakara.player.queue.update_time"] * 1000);
		console.log('queue poll time = '+settings["karakara.player.queue.update_time"]);
	}
}
function stop_queue_poll() {
	if (interval_queue_refresh) {
		clearInterval(interval_queue_refresh);
		interval_queue_refresh = null;
	}
}

// Websocket ------------------------------------------------------------------
var socket;
var socket_retry_interval = null;
function setup_websocket() {
	if (!settings['karakara.websocket.port']) {
		console.error("setup_websocket", "Websocket port not specified - remote control disabled");
		return;
	}
	//var websocket_url = "ws://"+location.hostname+":"+settings['karakara.websocket.port']+"/";  // The Shish saves the day ... again ... :)
	var websocket_url = ('https:' == document.location.protocol ? 'wss://' : 'ws://')+location.hostname+":"+settings['karakara.websocket.port']+"/";
	console.log("setup_websocket", websocket_url);
	socket = new WebSocket(websocket_url);
	socket.onopen = function(){ // Authenicate client with session key on socket connect
		var session_key = document.cookie.match(/karakara_session=([^;\s]+)/)[1];  // TODO - replace with use of settings['session_key'] or server could just use the actual http-header
		socket.send(session_key);
		$('body').removeClass('websocket_disconnected');
		console.log("Websocket: Connected");
		if (socket_retry_interval) {
			clearInterval(socket_retry_interval);
			socket_retry_interval = null;
		}
		stop_queue_poll();
		if (screens.current == 'video') {
			console.log("auto play video on websocket reconnection");
			get_video().play();
			// TODO: play is not quite perfect as the video resets
		}
		else {
			update_playlist();
		}
		
	};
	socket.onclose  = function() {
		socket = null;
		$('body').addClass('websocket_disconnected');
		console.log("Websocket: Disconnected");
		if (!socket_retry_interval) {
			socket_retry_interval = setInterval(setup_websocket,settings["karakara.websocket.disconnected_retry_interval"]*1000);
		}
		start_queue_poll();
	}
	socket.onmessage = function(msg) {
		var cmd = $.trim(msg.data);
		console.log('Websocket: Remote command: '+cmd);
		if (cmd in commands) {commands[cmd]();}
	};
}

// Screen Managment -----------------------------------------------------------

function show_screen(screen) {
	if (screen == screens.current) {return false;}  // Abort if no screen change required
	console.log('show_screen '+screen)
	
	// Remove 'screen_active' from existing active screen
	var element = $('.screen_active');
	var screen_active = element.attr('data-screen');
	element.removeClass('screen_active');
	if (screen_active in screens.events.on_hide) {
		screens.events.on_hide[screen_active](); // fire on_hide event
	}
	
	// Set 'screen_active' on screen
	screens.current = screen;
	$('.screen.screen_'+screen).addClass('screen_active');
	if (screen in screens.events.on_show) {
		screens.events.on_show[screen](); // Fire on_show event
	}
	
	return true;
}
var screens = {
	events: {
		on_show: {},
		on_hide: {},
	},
	current: null,
}

// Fullscreen Video -----------------------------------------------------------

screens.events.on_show['video'] = function() {
	if (playlist.length == 0) {
		show_screen('preview');
		return;
	}
	stop_queue_poll();  // Prevent Queue updates while playing a video
	set_video_fullscreen(get_attachment(playlist[0].track, "video"));
}

screens.events.on_hide['video'] = function() {
	console.log("on_hide video");
	set_video_fullscreen(null);
}


// Preview Screen ------------------------------------------------------------

screens.events.on_show['preview'] = function() {
	console.log("on_show preview");
	
	if (!socket) {
		start_queue_poll(); // Set queue poll update interval
	}
	
	if(playlist.length == 0) {
		console.log("Queue empty - returning to title screen");
		show_screen('title');
	}
	else {
		// Update preview video src if next preview is differnt
		var preview_src = get_attachment(playlist[0].track, "preview");
		if (preview_src != get_video_preview().__original_src) {
			var title = playlist[0].track.title;
			//console.log("Preparing next song - "+title);
			//$('title').html(title);
			//$('#title').html("<a href='"+"/files/" + get_attachment(playlist[0].track, "video")+"'>"+title+"</a>");
			set_video_preview(preview_src);
		}
	}
}

screens.events.on_hide['preview'] = function() {
	console.log("on_hide preview");
	set_video_preview(null);
}


// Video Management -----------------------------------------------------------

function get_video(create, selector_holder) {
	if (!selector_holder) {selector_holder = '.screen_video';}
	var selector_video = selector_holder+' video';
	var video = $(selector_video).get(0);
	if (!video && create) {
		//$(selector_video).remove();
		$(selector_holder).append('<video></video>');
		video = $(selector_video).get(0);
	}
	return video || {};
}
function get_video_preview(create) {return get_video(create, '#previewVideoHolder');}

function set_video_preview(src) {
	console.log("set_video_preview", src);
	$('.screen_preview video').remove();
	if (src) {
		var video = get_video_preview(true);
		video.__original_src = src;
		video.src = src;
		video.loop = true;
		video.volume = settings["karakara.player.video.preview_volume"];
		video.load();
		video.play();
	}
}
function set_video_fullscreen(src) {
	console.log("set_video_fullscreen", src);
	$('.screen_video video').remove();
	if (src) {
		var video = get_video(true);
		
		//video.bind("ended", commands.ended);
		video.addEventListener("ended", commands.ended);
		video.addEventListener("timeupdate", function() {
			var video = get_video();
			$('#seekbar').val((video.currentTime / video.duration) * 100);
		});
		
		video.loop = false;
		video.volume = 1.0;
		video.src = src;
		video.load();
		video.play();
	}
}


// Commands -------------------------------------------------------------------

var commands = {
	'play': function(e) {
		console.log('play');
		show_screen('video');
	},
	'pause': function(e) {
		console.log('pause');
		var video = get_video();
		if (video.paused) {video.play();}
		else              {video.pause();}
	},
	'stop': function(e) {
		console.log('stop');
		show_screen('preview')
	},
	'seek_forwards': function(e) {
		console.log('seek_forwards');
		var video = get_video();
		if (!video.src) {return;}
		if (video.currentTime +  settings["karakara.player.video.skip.seconds"] < video.duration) {
			video.currentTime += settings["karakara.player.video.skip.seconds"];
			console.log(video.currentTime, video.duration);
		}
		else {
			commands.ended();
		}
	},
	'seek_backwards': function(e) {
		console.log('seek_backwards');
		var video = get_video();
		if (!video.src) {return;}
		if (video.currentTime -  settings["karakara.player.video.skip.seconds"] >= 0) {
			video.currentTime -= settings["karakara.player.video.skip.seconds"];
			console.log(video.currentTime, video.duration);
		}
		else {
			video.currentTime = 0
		}
		
	},
	'skip': function(e) {
		console.log('skip');
		song_finished("skipped");
	},
	'ended': function(e) {
		console.log('ended');
		song_finished("played");
	},
	'queue_updated': function(e) {
		// Only update the quque when a video is not playing.
		// At the end of the playing video the quque will be updated anyway.
		if (screens.current!='video') {
			update_playlist();
		}
	},
	'settings': function(e) {
		update_settings();
	}
};


// Playlist Managment ---------------------------------------------------------


function song_finished(status) {
	console.log("song_finished");
	var id = playlist[0].id;
	
	// TODO - make this a .ajax request similar to the form in queue.mako
	$.getJSON(
		URLS.queue_items, {
			"method": "put",
			"queue_item.id": id,
			"status": status,
			"uncache": new Date().getTime()
		},
		function(data) {
			update_playlist();  // On operation complete
		}
	);
}

function update_playlist() {
	//console.log("update_playlist");
	function _sig(list) {
		var sig = "";
		for(var i=0; i<list.length; i++) {
			var t = list[i];
			sig = sig + t.time_touched;
		}
		return sig;
	}

	$.getJSON(URLS.queue_items, {}, function(data) {
		console.log("update_playlist getJSON response");
		if(_sig(playlist) != _sig(data.data.queue)) {
			console.log("update_playlist:updated");
			playlist     = data.data.queue;
			split_indexs = data.data.queue_split_indexs;
			render_playlist();
			if (!show_screen('preview')){
				// if we didnt need to swich screens because we are already on 'preview'
				// run the on_show method anyway -
				// this will setup the correct video preview or show titlescreen if needed
				screens.events.on_show.preview(); 
			}
		}
	});
}

function render_playlist() {
	console.log("render_playlist");
	
	// Split playlist with split_index (if one is provided)
	var playlist_ordered;
	var playlist_obscured;
	if (split_indexs.length && playlist.length) {
		// TODO split_indexs[0] is short term until we can support multiple groups in template
		playlist_ordered  = playlist.slice(0,split_indexs[0]);
		playlist_obscured = playlist.slice(split_indexs[0]);
		randomize(playlist_obscured);
	}
	else {
		playlist_ordered  = playlist
		playlist_obscured = [];
	}
	
	// Render queue_item scaffold
	function render_queue_items($element_destination, queue, renderer_queue_item) {
		$element_destination.empty();
		for(var i=0; i<queue.length; i++) {
			var queue_item = queue[i];
			var track = queue_item['track'];
			track.tags.get = function(tag){
				if (tag in this) {return this[tag];}
				return ""
			};
			var li_contents = renderer_queue_item(queue_item, track);
			if (li_contents) {
				$element_destination.append("<li>"+li_contents+"</li>");
			}
		}
	}
	
	// Render Playlist Ordered
	var queue_html = render_queue_items($('#playlist ol'), playlist_ordered, function(queue_item, track) {
		/**
		 * TODO: Use Flexbox - When the comment below was written flexbox didnt exisit. Maybe it can solve this problem.
		 *
		 * crap crap crap
		 * Tried to rewrite the whole way items are adding to the queue to be able to detect when the
		 * last li is rendered off the bottom of the screen so overflow could be rendered in the
		 * obscured list.
		 * Because the li elements are not made visible when when this code runs, we cant get the offsetHeight
		 * Other options include checking when the page is visible, using data elements and additional class selectors
		 * that is WAY to much effort.
		 * Because the items height is scaled with the height we can just say
		 * if there are > KNOWN_NUMBER add to other this.
		 * Be warned this magic number will need updating when the styles are adjusted.
		 * crap
		// If last element was off the bottom of the screen, add the element to the obscured list
		var li_last_top    = 0;
		var li_last_height = 0;
		try {
			var $last_element = $('#playlist ol li:last');
			li_last_top    = $last_element.get(0).offsetTop; //offset().top;
			li_last_height = $last_element.height();
			console.log($last_element, li_last_top);
		} catch (e) {}
		if (li_last_top && li_last_top > window.innerHeight - li_last_height) {
		*/
		if ($('#playlist ol li').size()>6) {
			playlist_obscured.unshift(queue_item);
			return null;
		}
		
		return "" +
			"<img src='"+get_attachment(track,'thumbnail')+"'>\n" +
			"<p class='title'>"     + track.tags.get("title")   + "</p>\n" +
			"<p class='from'>"      + track.tags.get("from")    + "</p>\n" +
			"<p class='performer'>" + queue_item.performer_name + "</p>\n" +
			"<p class='time'><span>" + timedelta_str(queue_item.total_duration*1000) + "</span></p>\n";
	});
	
	var queue_html = render_queue_items($('#playlist_obscured ul'), playlist_obscured, function(queue_item, track) {
		return queue_item.performer_name;
	});
}



// Title screen (logic and animation) -----------------------------------------
function init_titlescreen(titlescreen_images) {
	console.log("init_titlescreen");
	var titlescreen = {
		images: titlescreen_images,
		frames_per_sec: 20,
		num_images: 25, // num images should be constant, the size is changing, Math.floor(window.innerWidth/30);
		max_image_scale_factor: 3,
		min_image_scale_factor: 10
	};
	// Resize events - adjust image sizes
	function resize(e) {
		titlescreen.max_image_size = window.innerWidth / titlescreen.max_image_scale_factor;
		titlescreen.min_image_size = window.innerWidth / titlescreen.min_image_scale_factor;
		titlescreen.width = window.innerWidth;
		titlescreen.height = window.innerHeight;
		titlescreen.max_speed = (6 / (titlescreen.frames_per_sec/10)) * (window.innerHeight / 600);
		//console.log(titlescreen.width, titlescreen.height, titlescreen.max_image_size, titlescreen.min_image_size);
	}
	$(window).on('resize', resize);
	resize();
	
	function addImage(image, x, y, size, rotation, speed) {
		if (!image)    {image    = titlescreen.images[Math.floor(Math.random()*titlescreen.images.length)];}
		if (!x)        {x        = Math.random()*titlescreen.width -(titlescreen.max_image_size/2);}
		if (!y)        {y        = (Math.random()*(titlescreen.height+titlescreen.max_image_size))-titlescreen.max_image_size;}
		if (!size)     {size     = Math.random()*(titlescreen.max_image_size-titlescreen.min_image_size)+titlescreen.min_image_size;}
		if (!rotation) {rotation = Math.random()*Math.PI;}
		if (!speed)    {speed    = Math.random()*titlescreen.max_speed;}

		var img = $("<img>");
		img.attr("src", "/files/"+image);
		img.attr("style", "left: "+x+"px; top:"+y+"px; width: "+size+"px; -webkit-transform: rotate("+rotation+"rad);");
		img.attr("data-speed", speed+1);
		img.attr("data-rotation", rotation);
		$('.screen_title').append(img);
	}
	// Init images
	for (i=0 ; i<titlescreen.num_images ; i++) {addImage();}
	// Animation 'Thumbnail Rain'
	function animate_titlescreen() {
		//console.log("animate");
		$('.screen_title img').each(function(){
			element = $(this);
			function get_css(property_name, unit) {
				return parseFloat(element.css(property_name));
			};
			function set_css(property_name, value, unit) {
				element.css(property_name, ""+value+unit);
			}
			var x        = get_css('left'             ,'px' );
			var y        = get_css('top'              ,'px' );
			var rotation = parseFloat(element.attr('data-rotation'));
			var speed    = parseFloat(element.attr('data-speed'));
			if (y > titlescreen.height + titlescreen.max_image_size) {element.remove(); addImage(null,null,-titlescreen.max_image_size);}
			set_css('left', x       , 'px');
			set_css('top' , y+speed , 'px');
			rotation += (speed - (titlescreen.max_speed/2))/300;
			element.css('-webkit-transform', "rotate("+rotation+"rad)"); element.attr("data-rotation",""+rotation);
		});
	};
	screens.events.on_show.title = function() {
		console.log("on_show title");
		titlescreen.interval_animation = setInterval(animate_titlescreen, 1000/titlescreen.frames_per_sec);
	};
	screens.events.on_hide.title = function() {
		console.log("on_hide title");
		clearInterval(titlescreen.interval_animation);
	};

}

// Init -----------------------------------------------------------------------

function attach_events() {
	// Button Events
	$("#play").click(commands.play);
	$("#skip").click(commands.skip);
	
	// Keyboard Shortcuts
	$(document).on('keydown', function(e) {
		switch (e.which) {
			case KEYCODE.S        : commands.skip(); break;
			case KEYCODE.ENTER    : commands.play(); break;
			case KEYCODE.ESCAPE   : commands.stop(); break;
			case KEYCODE.LEFT     : commands.seek_backwards();break;
			case KEYCODE.RIGHT    : commands.seek_forwards(); break;
			case KEYCODE.SPACE    : commands.pause(); break;
		}
		if (e.which in KEYCODE) {
			e.preventDefault();
		}
	});
	// Help Popup
	$(document).on('mousemove', function(e) {
		if (!settings["karakara.player.help.timeout"]) {return;}
		if (mousemove_timeout) {
			clearTimeout(mousemove_timeout);
			mousemove_timeout = null;
		}
		mousemove_timeout = setTimeout(function(){$('body').removeClass('show_help');}, settings["karakara.player.help.timeout"]*1000);
		$('body').addClass('show_help');
	});
}

function init() {
	// Once settings Loaded & admin mode set -> setup final bits
	
	setup_websocket();
	
	// Removed oppressive version check - Firefox can handle this fine now
	//if (!get_chrome_version()) {
	//	//$('body').addClass('browser_unsupported');  // This is intrusive
	//	var msg = "Browser is unsupported. This player is currently only designed and tested to work with Google Chrome. It may behave unexpectedly.";
	//	console.warn(msg);
	//	alert(msg);
	//}
	
	// Load showcase images for titlescreen
	$.getJSON(URLS.random_images + "?count=200", {}, function(data) {
		console.log(URLS.random_images);
		init_titlescreen(data.data.images);
		show_screen('preview');
	});
}

$(document).ready(function() {
	attach_events();
	update_playlist();
	
	update_settings(function(data) {
		// Identify player.js as admin with admin cookie
		if (data.identity.admin) {init();}
		else {
			alert("User is not admin. Unable to get settings");
			//console.log('upgrading to admin mode')
			//$.getJSON("/admin.json", {"uncache": new Date().getTime()}, function(data) {
			//	if (data.identity.admin) {init();}
			//	else {
			//		console.error("Unable to set player as admin. The player may not function correctly. Check that admin mode is not locked");
			//		alert("Unable to set Admin mode for player interface");
			//	}
			//});
		}
	});
	
});
