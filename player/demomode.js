function choose(choices) {
	var index = Math.floor(Math.random() * choices.length);
	return choices[index];
}

function random_track() {
	return {
		"track": {
			"id": 2,
			"tags": {
				"title": choose(["Hello Song", "Let's Get To Burning", "Random Title #3", "The Song of My People", "Hello Song with a really long title: The Song of the Lengthening Words"]),
				"from": choose(["Animu", "That Show with the Things", "Demo Game", "Animu with a stupendously long name: The sequelising, the subtitle"])
			},
			"attachments": [
				{"type": "video", "location": "moo.webm"},
				{"type": "preview", "location": "moo.webm"},
				{"type": "thumbnail", "location": "moo.jpg"}
			]
		},
		"performer_name": choose(["Vanilla", "Chocola", "Mint", "Coconut", "Cinamon", "Azuki", "Maple", "ReallyLongBadgeNameGuy"]),
		"total_duration": choose([90, 120, 180, 234]),
		"time_touched": ""+Math.random()
	};
}

var demo_settings = {
	"data": {
		"settings": {
			"karakara.player.title": "KaraKara Player Test",
			"karakara.event.end": "2020-01-01 00:00:00",
			"karakara.player.queue.update_time": 60,
			"karakara.websocket.port": 8001,
			"karakara.websocket.disconnected_retry_interval": 10,
			"karakara.player.video.preview_volume": 10,
			"karakara.player.video.skip.seconds": 10,
			"karakara.player.help.timeout": 5
		}
	},
	"identity": {
		"admin": true
	}
};

var demo_queue_empty = {"data": {
	"queue": [],
	"queue_split_indexs": [5]
}}
var demo_queue = {"data": {
	"queue": [
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
		random_track(),
	],
	"queue_split_indexs": [5]
}};

(function() {
	if(window.location.protocol == "file:") {
		console.log("In demo mode - monkey-patching jQuery");
		
		var _orig_getJSON = $.getJSON;
		$.getJSON = function(path, vars, callback) {
			if(path == "/settings.json") {
				callback(JSON.parse(JSON.stringify(demo_settings)));
			}
			if(path == "/queue.json") {
				callback(JSON.parse(JSON.stringify(demo_queue)));
			}
		}

		var _orig_get_attachment = get_attachment;
		get_attachment = function(track, thing) {
			return "." + _orig_get_attachment(track, thing);
		}

		var _orig_song_finished = song_finished;
		song_finished = function(status) {
			demo_queue.data.queue.shift();
			return _orig_song_finished(status);
		}
	}
})();
