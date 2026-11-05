#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
BUILD_DIR=${DIR}/../build/snap

${BUILD_DIR}/bin/cli --help
for hook in install configure pre-refresh post-refresh; do
  ${BUILD_DIR}/meta/hooks/${hook} --help
done
