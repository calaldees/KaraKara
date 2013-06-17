var DEFAULT_PLAYLIST_UPDATE_TIME = 3; //Seconds to poll server
var DEFAULT_VIDEO_BACKGROUND_VOLUME = 0.2;

var settings = {};
var playlist = [];
var split_indexs = [];
var socket;

function setup_remote() {
	var socket = new WebSocket("ws://"+location.hostname+":"+settings['karakara.websocket.port']+"/");
	function receive(msg) {
		var cmd = $.trim(msg.data);
		console.log('remote control: '+cmd);
		if (cmd in commands) {commands[cmd]();}
	};
	socket.onmessage = receive;
}

var commands = {
	'play': function(e) {
		console.log('#play');
		var video = $('#player').get(0);
		video.loop = false;
		video.volume = 1.0;
		video.src = "/files/" + get_attachment(playlist[0].track, "video");
		video.webkitRequestFullScreen();
		video.load();
		video.play();
	},
	'skip': function(e) {
		console.log('#skip');
		//e.preventDefault();
		song_finished("skipped");
	},
	'ended': function(e) {
		console.log('#player:ended');
		var video = $('#player').get(0);
		video.webkitExitFullScreen();
		song_finished("played");
	}
};

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
	$.getJSON(
		"/queue", {
			"method": "put",
			"queue_item.id": playlist[0].id,
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
		//console.log("update_playlist getJSON response");
		if(_sig(playlist) != _sig(data.data.queue)) {
			//console.log("update_playlist:updated");
			playlist     = data.data.queue;
			split_indexs = data.data.queue_split_indexs;
			render_playlist();
			prepare_next_song();
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
	
	// Playlist Ordered
	var h = "<ol>";
	for(var i=0; i<playlist_ordered.length; i++) {
		var t = playlist_ordered[i];
		h += "<li><p id='addTitle'>" + t['track']['tags']['title'] + " </p><p id=addFrom>" + t['track']['tags']['from'] + "</p><p id='addPerformer'> " + t['performer_name'] + " </p><p id='addTime'> " + timedelta_str(t['total_duration']*1000) + "</p>";
	}
	h += "</ol>";
	$('#playlist').html(h);
	
	// Playlist Obscured
	var h = "<ul>";
	for(var i=0; i<playlist_obscured.length; i++) {
		var t = playlist_obscured[i];
		h += "<li>" + t['track']['tags']['title'] + " (" + t['track']['tags']['from'] + ")" + " - " + t['performer_name'];
	}
	h += "</ul>";
	$('#playlist_obscured').html(h);
	
}


function prepare_next_song() {
	if(playlist.length == 0) {
		$('title').html("Waiting for Songs");
		$('#title').html("Waiting for Songs");
	}
	else {
		var title = playlist[0].track.title;
		if($('title').html() != title) {
			console.log("Preparing next song");
			$('title').html(title);
			$('#title').html("<a style='color: white; text-decoration: none;' href='"+"/files/" + get_attachment(playlist[0].track, "video")+"'>"+title+"</a>");
			var video = $('#player').get(0);
			video.src = "/files/" + get_attachment(playlist[0].track, "preview");
			video.loop = true;
			video.volume = settings["karakara.player.video.preview_volume"];
			video.load();
			video.play();
		}
	}
}

$(document).ready(function() {
	update_playlist();
	
	$("#play").click(commands.play);
	$("#skip").click(commands.skip);
	$("#player").bind("ended", commands.ended);
	
	$.getJSON("/settings", {}, function(data) {
		console.log("/settings");
		settings = data.data.settings;
		
		// Identify player.js as admin with admin cookie
		if (!data.identity.admin) {
			$.getJSON("/admin", {}, function(data) {
				if (!data.identity.admin) {
					console.error("Unable to set player as admin. The player may not function correctly. Check that admin mode is not locked");
					alert("Unable to set Admin mode for player interface");
				}
			})
		}
		
		// Set update interval
		settings["karakara.player.queue.update_time"] = settings["karakara.player.queue.update_time"] || DEFAULT_PLAYLIST_UPDATE_TIME;
		settings['interval'] = setInterval(update_playlist, settings["karakara.player.queue.update_time"] * 1000);
		console.log('update_interval='+settings["karakara.player.queue.update_time"]);
		
		settings["karakara.player.video.preview_volume"] = settings["karakara.player.video.preview_volume"] || DEFAULT_VIDEO_BACKGROUND_VOLUME;
		
		setup_remote();
	});
	
});
