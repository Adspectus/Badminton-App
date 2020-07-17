#!/bin/bash

TOPDIR=$(git rev-parse --show-toplevel)

export VIRTUAL_ROOT="$TOPDIR"

exec "$TOPDIR/bin/CheckEnvironment.pl"

exit 0
