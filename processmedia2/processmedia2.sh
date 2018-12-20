#!/bin/bash
set +x
#set -m

KARAKARA_PROCESSMEDIA2_CONFIG=${KARAKARA_PROCESSMEDIA2_CONFIG:-config.docker.json}

function run() {
    echo "process test"
    python3 scan_media.py    --config ${KARAKARA_PROCESSMEDIA2_CONFIG}
    # scan will terminate with `exit 1` if no files have changed
    python3 encode_media.py  --config ${KARAKARA_PROCESSMEDIA2_CONFIG}
    python3 import_media.py  --config ${KARAKARA_PROCESSMEDIA2_CONFIG} --force
    if [ "${KARAKARA_PROCESSMEDIA2_CLEANUP:-false}" == "true" ]; then
        echo "cleanup"
        python3 cleanup_media.py --config ${KARAKARA_PROCESSMEDIA2_CONFIG}
    fi
}

while [ "${KARAKARA_PROCESSMEDIA2_ENABLED:-true}" == "true" ]; do
    run && touch .heartbeat || true
    echo "sleep ..."
    sleep ${KARAKARA_RESCAN_INTERVAL_SECONDS:-600}
    test $? -gt 128 && exit 0  # https://unix.stackexchange.com/questions/42287/terminating-an-infinite-loop
done
