#!/bin/bash
set +x

KARAKARA_PROCESSMEDIA2_CONFIG=${KARAKARA_PROCESSMEDIA2_CONFIG:-config.docker.json}

while [ "${KARAKARA_PROCESSMEDIA2_ENABLED:-true}" == "true" ]; do
    echo "process test"
    #python3 scan_media.py    --config ${KARAKARA_PROCESSMEDIA2_CONFIG}
    #python3 encode_media.py  --config ${KARAKARA_PROCESSMEDIA2_CONFIG} --process_order_function random
    #python3 import_media.py  --config ${KARAKARA_PROCESSMEDIA2_CONFIG} --force
    if [ "${KARAKARA_PROCESSMEDIA2_CLEANUP:-false}" == "true" ]; then
    echo "cleanup"
    #python3 cleanup_media.py --config ${KARAKARA_PROCESSMEDIA2_CONFIG}
    fi
    sleep ${KARAKARA_RESCAN_INTERVAL_SECONDS:-600}
done
