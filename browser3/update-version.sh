#!/bin/sh
set -eux
cat >src/utils/build_info.ts <<EOF
export const COMMIT = '$(git rev-parse --short HEAD)';
export const BUILD_DATE = '$(date -u +"%Y-%m-%dT%H:%M:%SZ")';
EOF
