#!/bin/bash

DIRS="bin cgi-bin config htdocs perl-lib"
FILES=""
OWNER=$(id -un)
GROUP=$(id -gn)
FILEMODE="664"
DIRMODE="775"

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
VERSION=$(git describe)
TOPDIR=$(git rev-parse --show-toplevel)

[[ -z $TOPDIR ]] && exit

for dir in $DIRS;do
  sudo chown -R "$OWNER"."$GROUP" "$TOPDIR/$dir"
  find "$TOPDIR/$dir" -type d -print0 | xargs -0r sudo chmod "$DIRMODE"
  find "$TOPDIR/$dir" -type f -print0 | xargs -0r sudo chmod "$FILEMODE"
  find "$TOPDIR/$dir" -type f \( -name '*.sh' -o -name '*.pl' -o -name '*.cgi' \) -print0 | xargs -0r sudo chmod "$DIRMODE"
done

for file in $FILES;do
  sudo chown "$OWNER"."$GROUP" "$file"
  sudo chmod "$FILEMODE" "$file"
done

exit 0
