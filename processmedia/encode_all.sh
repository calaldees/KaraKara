#!/bin/sh

for SONG_DIR in files/* ; do
	if [ -d "$SONG_DIR" ] ; then
		ORIGINAL_VIDEO=`ls $SONG_DIR/original.* | grep -E "original.(flv|mp4|avi|mkv)"`
		if [ "x$ORIGINAL_VIDEO" = "x" ] ; then
			echo "No original video found; looking for original audio / image"
			IMAGE=`ls $SONG_DIR/original.* | grep -E "original.(jpg|png)"`
			AUDIO=`ls $SONG_DIR/original.* | grep -E "original.(mp3|ogg)"`
			AUDIO_LEN=`avconv -i $AUDIO 2>&1 | grep -oE "Duration: [0-9:\.]+" | cut -d " " -f 2` #[\d:\.]+"`
			ORIGINAL_VIDEO=$SONG_DIR/generated.mkv
			if [ "x$IMAGE" = "x"  -o "x$AUDIO" = "x" ] ; then
				echo "ERROR: $SONG_DIR doesn't contain an original video, nor original audio + image"
			else
				avconv -i $AUDIO -loop 1 -r 5 -i $IMAGE -t $AUDIO_LEN -vf scale=640:-1 -acodec copy $ORIGINAL_VIDEO
			fi
		fi
		#echo Original: $ORIGINAL_VIDEO
		./encode.sh $ORIGINAL_VIDEO
	fi
done
