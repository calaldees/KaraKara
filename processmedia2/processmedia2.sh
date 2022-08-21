#!/bin/bash
#set -x
set -e

KARAKARA_PROCESSMEDIA2_CONFIG=${KARAKARA_PROCESSMEDIA2_CONFIG:-config.docker.json}

function run() {
    echo "processmedia2 - $(date)"
    # scan will terminate with `exit 1` if no files have changed
    # Attempt to make function exit on failed command - https://stackoverflow.com/a/51913013/3356840
    python3 scan_media.py && \
    python3 encode_media.py && \
    python3 export_track_data.py && \
    python3 cleanup_media.py
}

while true ; do
    run || true
    sleep ${KARAKARA_RESCAN_INTERVAL_SECONDS:-600}  # 600 = 10min
    test $? -gt 128 && exit 0  # https://unix.stackexchange.com/questions/42287/terminating-an-infinite-loop
done
