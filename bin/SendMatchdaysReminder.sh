#!/bin/bash

TOPDIR=$(git rev-parse --show-toplevel)

export VIRTUAL_ROOT="$TOPDIR"

exec "$TOPDIR/bin/SendMatchdaysReminder.pl"

exit 0
