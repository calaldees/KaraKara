// Constants ------------------------------------------------------------------
KEYCODE = {
	BACKSPACE: 8,
	ENTER    :13,
	ESCAPE   :27,
	LEFT     :37,
	RIGHT    :39,
	SPACE    :32,
};

// Settings Management --------------------------------------------------------
var settings = {};
var SETTINGS_DEFAULT = {
	"karakara.player.title"               : "KaraKara",
	"karakara.player.video.preview_volume":  0.2,
	"karakara.player.video.skip.seconds"  : 20,
	"karakara.player.queue.update_time"   :  3 , //Seconds to poll server
	"karakara.player.help.timeout"        :  2,
	"karakara.websocket.port"             : null,
	"karakara.websocket.disconnected_retry_interval": 5, // Seconds to retry websocket in the event of disconnection
}
function init_settings(new_settings) {
	if (!new_settings) {new_settings = {};}
	for (setting_key in SETTINGS_DEFAULT) {
		if (setting_key in new_settings) {settings[setting_key] = new_settings[setting_key];}
		else                             {settings[setting_key] = SETTINGS_DEFAULT[setting_key];}
	}
}

// Variables ------------------------------------------------------------------
var playlist = [];
var split_indexs = [];
var mousemove_timeout;
var interval_animation_titlescreen;
var interval_queue_refresh;

// Utils ----------------------------------------------------------------------

function get_chrome_version() {
	try      {return parseInt(window.navigator.appVersion.match(/Chrome\/(\d+)\./)[1], 10);}
	catch(e) {return 0;}
}


// Websocket ------------------------------------------------------------------
var socket;
var socket_retry_interval = null;
function setup_websocket() {
	console.log("setup_websocket");
	if (!settings['karakara.websocket.port']) {
		console.error("Websocket port not specifyed - remote control disabled");
		return;
	}
	socket = new WebSocket("ws://"+location.hostname+":"+settings['karakara.websocket.port']+"/");
	socket.onopen = function(){ // Authenicate client with session key on socket connect
		socket.send(document.cookie.match(/karakara_session=(.+?)(\;|\b)/)[1]);  // TODO - replace with use of settings['session_key'] or server could just use the actual http-header
		$('body').removeClass('websocket_disconnected');
		console.log("Websocket: Connected");
		if (socket_retry_interval) {
			clearInterval(socket_retry_interval);
			socket_retry_interval = null;
		}
	};
	socket.onclose  = function() {
		socket = null;
		$('body').addClass('websocket_disconnected');
		console.log("Websocket: Disconnected");
		if (!socket_retry_interval) {
			socket_retry_interval = setInterval(setup_websocket,settings["karakara.websocket.disconnected_retry_interval"]*1000);
		}
	}
	socket.onmessage = function(msg) {
		var cmd = $.trim(msg.data);
		console.log('Websocket: Remote command: '+cmd);
		if (cmd in commands) {commands[cmd]();}
	};
}

// Screen Managment -----------------------------------------------------------

function show_screen(screen) {
	console.log('show_screen '+screen)
	var element = $('.screen_active');
	var screen_active = element.attr('data-screen');
	if (screen_active == screen) {return;}
	element.removeClass('screen_active');
	if (screen_active in screens.events.on_hide) {
		screens.events.on_hide[screen_active](); // fire on_hide event
	}
	
	$('.screen.screen_'+screen).addClass('screen_active');
	if (screen in screens.events.on_show) {
		screens.events.on_show[screen](); // Fire on_show event
	}
}
var screens = {
	events: {
		on_show: {},
		on_hide: {},
	}
}

// Video ----------------------------------------------------------------------


function get_video()         {return $('.screen_video video'  ).get(0) || {};}
function get_video_preview() {return $('.screen_preview video').get(0) || {};}

screens.events.on_show['video'] = function() {
	if (interval_queue_refresh) {
		clearInterval(interval_queue_refresh);
		interval_queue_refresh = null;
	}
}

screens.events.on_hide['video'] = function() {
	console.log("on_hide video");
	var video = get_video();
	video.scr="";
	video.load();
}


function set_video_preview(src) {
	var video = get_video_preview();
	video.src = "/files/" + src;
	video.loop = true;
	video.volume = settings["karakara.player.video.preview_volume"];
	video.load();
	//show_screen('preview');
	video.play();
}
function set_video_fullscreen(src) {
	var video = get_video();
	video.loop = false;
	video.volume = 1.0;
	video.src = "/files/" + src;
	video.load();
	video.play();
}

var commands = {
	'play': function(e) {
		console.log('play');
		set_video_fullscreen(get_attachment(playlist[0].track, "video"));
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
		set_video_preview(get_attachment(playlist[0].track, "preview"));
		show_screen('preview')
	},
	'seek_forwards': function(e) {
		console.log('seek_forwards');
		var video = get_video();
		if (video.currentTime +  settings["karakara.player.video.skip.seconds"] < video.duration) {
			video.currentTime += settings["karakara.player.video.skip.seconds"];
		}
		else {
			commands.ended();
		}
	},
	'seek_backwards': function(e) {
		console.log('seek_backwards');
		var video = get_video();
		if (video.currentTime -  settings["karakara.player.video.skip.seconds"] >= 0) {
			video.currentTime -= settings["karakara.player.video.skip.seconds"];
		}
		else {
			video.currentTime = 0
		}
		
	},
	'skip': function(e) {
		console.log('skip');
		song_finished("skipped");
		commands.stop();
	},
	'ended': function(e) {
		console.log('ended');
		song_finished("played");
		commands.stop();
	}
};

// Preview Screen ------------------------------------------------------------

screens.events.on_show['preview'] = function() {
	console.log("on_show preview");
	
	// Set queue poll update interval
	if (!interval_queue_refresh) {
		interval_queue_refresh = setInterval(update_playlist, settings["karakara.player.queue.update_time"] * 1000);
		console.log('update_interval='+settings["karakara.player.queue.update_time"]);
	}
	
	if(playlist.length == 0) {
		console.log("Queue empty - returning to title screen");
		set_video_preview(null);
		show_screen('title');
	}
	else {
		var title = playlist[0].track.title;
		console.log("Preparing next song - "+title);
		$('title').html(title);
		$('#title').html("<a href='"+"/files/" + get_attachment(playlist[0].track, "video")+"'>"+title+"</a>");
		set_video_preview(get_attachment(playlist[0].track, "preview"));
	}
}

screens.events.on_hide['preview'] = function() {
	console.log("on_hide preview");
	var video = get_video_preview();
	video.scr="";
	video.load();
}


// Playlist Managment ---------------------------------------------------------

function get_attachment(track, type) {
	for(var i=0; i<track.attachments.length; i++) {
		if(track.attachments[i].type == type) {
			return track.attachments[i].location;
		}
	}
	return "";
}

function song_finished(status) {
	console.log("song_finished");
	var id = playlist[0].id;
	playlist.shift();
	$.getJSON(
		"/queue", {
			"method": "put",
			"queue_item.id": id,
			"status": status,
			"uncache": new Date().getTime()
		},
		function(data) {
			update_playlist();
		}
	);
}

function update_playlist() {
	//console.log("update_playlist");
	function _sig(list) {
		var sig = "";
		for(var i=0; i<list.length; i++) {
			sig = sig + list[i].time_touched;
		}
		return sig;
	}

	$.getJSON("/queue", {}, function(data) {
		console.log("update_playlist getJSON response");
		if(_sig(playlist) != _sig(data.data.queue)) {
			//console.log("update_playlist:updated");
			playlist     = data.data.queue;
			split_indexs = data.data.queue_split_indexs;
			render_playlist();
			show_screen('preview');
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
	function render_queue_items(queue, renderer_queue_item) {
		var output_buffer = "";
		for(var i=0; i<queue.length; i++) {
			var queue_item = queue[i];
			var track = queue_item['track'];
			track.tags.get = function(tag){
				if (tag in this) {return this[tag];}
				return ""
			};
			output_buffer += "<li>\n"+renderer_queue_item(queue_item, track)+"</li>\n";
		}
		return output_buffer;
	}
	
	// Render Playlist Ordered
	var queue_html = render_queue_items(playlist_ordered, function(queue_item, track) {
		return "" +
			"<p class='title'>"     + track.tags.get("title")   + "</p>\n" +
			"<p class='from'>"      + track.tags.get("from")    + "</p>\n" +
			"<p class='performer'>" + queue_item.performer_name + "</p>\n" +
			"<p class='time'> "     + timedelta_str(queue_item.total_duration*1000) + "</p>\n";
	});
	$('#playlist').html("<ol>"+queue_html+"</ol>\n");
	
	// Render Playlist Obscured
	if (playlist_obscured.length) {
		$('#upLater').html('<h2>Later On</h2>');
	}
	var queue_html = render_queue_items(playlist_obscured, function(queue_item, track) {
		var buffer = "";
		buffer += track.tags.get("title");
		track.tags.get("from") ? buffer += " ("+track.tags.get("from")+")" : null;
		buffer += " - "+queue_item.performer_name+"\n";
		return buffer;
	});
	$('#playlist_obscured').html("<ul>"+queue_html+"</ul>");
}



// Title screen (logic and animation) -----------------------------------------

function init_titlescreen(titlescreen_images) {
	console.log("init_titlescreen");
	var frames_per_sec = 20;
	var num_images = Math.floor(screen.width/30);
	var max_image_size = 250;
	var min_image_size =  50;
	var max_speed = 6 / (frames_per_sec/10);
	function addImage(image, x, y, size, rotation, speed) {
		if (!image)    {image    = titlescreen_images[Math.floor(Math.random()*titlescreen_images.length)];}
		if (!x)        {x        = Math.random()*screen.width -max_image_size;}
		if (!y)        {y        = Math.random()*screen.height-max_image_size;}
		if (!size)     {size     = Math.random()*(max_image_size-min_image_size)+min_image_size;}
		if (!rotation) {rotation = Math.random()*Math.PI;}
		if (!speed)    {speed    = Math.random()*max_speed;}
		$('.screen_title').append("<img src='/files/"+image+"' style='left: "+x+"px; top:"+y+"px; width: "+size+"px; -webkit-transform: rotate("+rotation+"rad);' data-speed='"+(speed+1)+"' data-rotation='"+rotation+"'>");
	}
	// Init images
	for (i=0 ; i<num_images ; i++) {addImage();}
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
			if (y > screen.height) {element.remove(); addImage(null,null,-max_image_size);}
			set_css('left', x       , 'px');
			set_css('top' , y+speed , 'px');
			rotation += (speed - (max_speed/2))/300;
			element.css('-webkit-transform', "rotate("+rotation+"rad)"); element.attr("data-rotation",""+rotation);
		});
	}
	screens.events.on_show.title = function() {
		console.log("on_show title");
		interval_animation_titlescreen = setInterval(animate_titlescreen, 1000/frames_per_sec);
	};
	screens.events.on_hide.title = function() {
		console.log("on_hide title");
		clearInterval(interval_animation_titlescreen);
	};

	show_screen('preview');
}

// Init -----------------------------------------------------------------------

function attach_events() {
	// Button Events
	$("#play").click(commands.play);
	$("#skip").click(commands.skip);
	$(".screen_video video").bind("ended", commands.ended);
	// Keyboard Shortcuts
	$(document).on('keydown', function(e) {
		switch (e.which) {
			case KEYCODE.BACKSPACE: commands.skip(); break;
			case KEYCODE.ENTER    : commands.play(); break;
			case KEYCODE.ESCAPE   : commands.stop(); break;
			case KEYCODE.LEFT     : commands.seek_backwards();break;
			case KEYCODE.RIGHT    : commands.seek_forwards(); break;
			case KEYCODE.SPACE    : commands.pause(); break;
		}
	});
	// Help Popup
	$(document).on('mousemove', function(e) {
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
	
	
	$('h1').text(settings["karakara.player.title"]);
	
	setup_websocket();
	
	if (!get_chrome_version()) {
		$('body').addClass('browser_unsupported');
		var msg = "Browser is unsupported. This player is currently only designed and tested to work with Google Chrome. It may behave unexpectedly.";
		console.warn(msg);
		alert(msg);
	}
	
	show_screen('preview');
}

$(document).ready(function() {
	init_settings({}); // TODO: fix better!! ..Prevents bug where initial update time is undefined .... preview screen is shown before settings are loaded ...
	attach_events();
	update_playlist();
	
	// Load showcase images for titlescreen
	$.getJSON("/random_images.json?count=200", {}, function(data) {
		console.log("/random_images");
		init_titlescreen(data.data.thumbnails);
	});
	
	// Load settings from server
	$.getJSON("/settings.json", {}, function(data) {
		console.log("/settings");
		init_settings(data.data.settings);
		// Identify player.js as admin with admin cookie
		if (!data.identity.admin) {
			$.getJSON("/admin", {}, function(data) {
				if (!data.identity.admin) {
					console.error("Unable to set player as admin. The player may not function correctly. Check that admin mode is not locked");
					alert("Unable to set Admin mode for player interface");
				}
			});
		}
		
		init();
	});
	
});
