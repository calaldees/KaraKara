
var playlist = [];
var playlist_pos = -1;

function render_playlist() {
	var h = "<ul>";
	for(var i=0; i<playlist.length; i++) {
		if(i < playlist_pos) {
			// we've played it, hide it
			continue;
		}
		else if(i == playlist_pos) {
			h += "<li class='current_song'>";
		}
		else if(i == playlist_pos + 1) {
			h += "<li class='up_next'>";
		}
		else {
			h += "<li>";
		}
		h += "<a href='#' onclick='set_playlist_pos("+i+")'>" + playlist[i]['title'] + " - " + playlist[i]['singer'] + "</a>";
	}
	h += "</ul>";
	$('#playlist').html(h);
}

function set_playlist_pos(n) {
	playlist_pos = n;
	var video = $('#player').get(0);

	if(playlist_pos < 0) {
		$('title').html("Waiting for Songs");
		$('#title').html("Waiting for Songs");
		video.pause();
	}
	else if(playlist_pos >= playlist.length) {
		$('title').html("End of Playlist");
		$('#title').html("End of Playlist");
		video.pause();
	}
	else {
		$('title').html(playlist[n]['title']);
		$('#title').html(playlist[n]['title']);
		video.src = "../" + playlist[n]['preview'];
		video.loop = true;
		video.volume = 0.05;
		video.load();
		video.play();
	}
}

$(function() {
	setInterval(function() {
		var seconds = new Date().getTime() / 1000;
		$.getJSON("../api/get_playlist.json", {"uncache": seconds}, function(data) {
			var waiting = (playlist_pos < 0 || playlist_pos >= playlist.length);
			var current_end = playlist.length;
			playlist = data;
			if(waiting) {
				if(playlist_pos < 0) {
					set_playlist_pos(0);
				}
				else {
					set_playlist_pos(current_end);
				}
			}
		});
		render_playlist();
	}, 1000);
	$("#next").click(function(e) {
		e.preventDefault();
		set_playlist_pos(playlist_pos + 1);
	});
	$("#prev").click(function(e) {
		e.preventDefault();
		set_playlist_pos(playlist_pos - 1);
	});
	$("#play").click(function(e) {
		var video = $('#player').get(0);
		video.loop = false;
		video.volume = 1.0;
		video.src = "../" + playlist[playlist_pos]['video'];
		video.webkitEnterFullScreen();
		video.load();
		video.play();
	});
	$("#player").bind("ended", function(e) {
		var video = $('#player').get(0);
		video.webkitExitFullScreen();
		set_playlist_pos(playlist_pos + 1);
	});
});
