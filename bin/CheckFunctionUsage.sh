#!/bin/bash

TOPDIR=$(git rev-parse --show-toplevel)

FUNCTIONS=`grep -e ^sub.*#$ $TOPDIR/perl-lib/Badminton/Functions.pm | cut -d" " -f2`
DB_FUNCTIONS=`grep -e ^sub.*#$ $TOPDIR/perl-lib/Badminton/DB.pm | cut -d" " -f2`

FILES="$TOPDIR/cgi-bin/Badminton.cgi $TOPDIR/cgi-bin/BadmintonAjax.cgi $TOPDIR/bin/SendStatus.pl $TOPDIR/bin/SendMatchdaysReminder.pl"

for f in $FUNCTIONS $DB_FUNCTIONS;do
  SUM=0
  for file in $FILES;do
    HITS=$(grep -c $f $file)
    SUM=$((SUM + HITS))
  done
  if [ $SUM == 0 ];then
    echo "Function $f not used"
  fi
done

exit 0
