#!/bin/bash

TOPDIR=$(git rev-parse --show-toplevel)

export VIRTUAL_ROOT="$TOPDIR"

exec "$TOPDIR/bin/SendStatus.pl"

exit 0
