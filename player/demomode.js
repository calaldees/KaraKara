function choose(choices) {
	var index = Math.floor(Math.random() * choices.length);
	return choices[index];
}

function random_track() {
	return {
		"track": {
			"id": 2,
			"tags": {
				"title": choose(["Hello Song", "Let's Get To Burning", "Random Title #3", "The Song of My People"]),
				"from": choose(["Animu", "That Show with the Things", "Demo Game"])
			},
			"attachments": [
				{"type": "video", "location": "moo.mp4"},
				{"type": "preview", "location": "moo.mp4"},
				{"type": "thumbnail", "location": "moo.jpg"}
			]
		},
		"performer_name": choose(["Vanilla", "Chocola", "Mint", "Coconut", "Cinamon", "Azuki", "Maple"]),
		"total_duration": choose([90, 120, 180, 234])
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

var demo_queue = {"data": {
	"queue": [
		{
			"track": {
				"id": 1,
				"tags": {
					"title": "Hello Song with a really long title: The Song of the Lengthening Words",
					"from": "Animu with a stupendously long name: The sequelising, the subtitle"
				},
				"attachments": [
					{"type": "video", "location": "moo.mp4"},
					{"type": "preview", "location": "moo.mp4"},
					{"type": "thumbnail", "location": "moo.jpg"}
				]
			},
			"performer_name": "Shish of the quite silly con badge name what what? Is this enough.",
			"total_duration": 30
		},
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
				callback(demo_settings);
			}
			if(path == "/queue.json") {
				callback(demo_queue);
			}
		}

		var _orig_get_attachment = get_attachment;
		get_attachment = function(track, thing) {
			return "." + _orig_get_attachment(track, thing);
		}
	}
})();
