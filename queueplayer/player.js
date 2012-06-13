
var playlist = [];

function song_finished() {
	console.log("Song finished");
	$.get(
		"/queue", {
			//http://localhost:8000/queue?method=delete&format=redirect&queue_item.id=3
			"method": "delete",
			"format": "redirect",
			"queue_item.id": playlist[0].id,
			//"status": "completed",
			//"uncache": new Date().getTime()
		},
		function(data) {
			update_playlist();
		}
	);
}

function update_playlist() {
	console.log("Updating playlist");

	function _sig(list) {
		if(list.length == 0) return "";
		return list[0].touched + list[list.length-1].touched;
	}

	$.getJSON("/queue.json", {"uncache": new Date().getTime()}, function(data) {
		if(_sig(playlist) != _sig(data.data.list)) {
			playlist = data.data.list;
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
			$('#title').html(title);
			var video = $('#player').get(0);
			video.src = "/files/" + playlist[0].track.attachments[1].location;
			video.loop = true;
			video.volume = 0.05;
			video.load();
			video.play();
		}
	}
}

$(function() {
	update_playlist();
	setInterval(function() {
		update_playlist();
	}, 3000);

	$("#play").click(function(e) {
		var video = $('#player').get(0);
		video.loop = false;
		video.volume = 1.0;
		video.src = "/files/" + playlist[0].track.attachments[0].location;
		video.webkitEnterFullScreen();
		video.load();
		video.play();
	});
	$("#skip").click(function(e) {
		e.preventDefault();
		song_finished();
	});
	$("#player").bind("ended", function(e) {
		var video = $('#player').get(0);
		video.webkitExitFullScreen();
		song_finished();
	});
});
