var DEFAULT_PLAYLIST_UPDATE_TIME = 3; //Seconds to poll server

var settings = {};
var playlist = [];

function song_finished(status) {
	console.log("Song finished");
	$.getJSON(
		"/queue", {
			//http://localhost:8000/queue?method=delete&format=redirect&queue_item.id=3
			"method": "put",
			//"format": "json",
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
	console.log("Updating playlist");

	function _sig(list) {
		var sig = "";
		for(var i=0; i<list.length; i++) {
			sig = sig + list[i].time_touched;
		}
		return sig;
	}

	$.getJSON("/queue", {}, function(data) { //AllanC - removed unique URL to facilitate eTag - "uncache": new Date().getTime()
		if(_sig(playlist) != _sig(data.data.queue)) {
			playlist = data.data.queue;
			render_playlist();
			prepare_next_song();
		}
	});
}

function render_playlist() {
	console.log("Rendering playlist");
	var h = "<ul>";
	for(var i=0; i<playlist.length; i++) {
		if(i == 0) {
			h += "<li class='current_song'>";
		}
		else if(i == 1) {
			h += "<li class='up_next'>";
		}
		else {
			h += "<li>";
		}
		h += playlist[i]['track']['title'] + " - " + playlist[i]['performer_name'];
	}
	h += "</ul>";
	$('#playlist').html(h);
}

function get_attachment(track, type) {
	for(var i=0; i<track.attachments.length; i++) {
		if(track.attachments[i].type == type) {
			return track.attachments[i].location;
		}
	}
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
			$('#title').html("<a href='"+"/files/" + get_attachment(playlist[0].track, "video")+"'>"+title+"</a>");
			var video = $('#player').get(0);
			video.src = "/files/" + get_attachment(playlist[0].track, "preview");
			video.loop = true;
			video.volume = 0.05;
			video.load();
			video.play();
		}
	}
}

$(document).ready(function() {
	update_playlist();

	$("#play").click(function(e) {
		var video = $('#player').get(0);
		video.loop = false;
		video.volume = 1.0;
		video.src = "/files/" + get_attachment(playlist[0].track, "video");
		video.webkitEnterFullScreen();
		video.load();
		video.play();
	});
	$("#skip").click(function(e) {
		e.preventDefault();
		song_finished("skipped");
	});
	$("#player").bind("ended", function(e) {
		var video = $('#player').get(0);
		video.webkitExitFullScreen();
		song_finished("played");
	});
	
	$.getJSON("/settings", {}, function(data) {
		settings = data.data.settings;
		
		// Identify player.js as admin with admin cookie
		if (!data.identity.admin) {
			$.getJSON("/admin", {}, function(data) {
				if (!data.identity.admin) {
					console.error("Unable to set player as admin. The player may not function correctly");
				}
			})
		}
		
		// Set update interval
		var update_inverval = parseInt(settings["karakara.player.update_time"]) * 1000;
		if (!update_inverval) {update_inverval = DEFAULT_PLAYLIST_UPDATE_TIME*1000;}
		settings['interval'] = setInterval(update_playlist, update_inverval);
		console.log('update_interval='+update_inverval);
	});
	
});
