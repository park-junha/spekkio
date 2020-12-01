#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "err: argument \$1 not supplied"
  exit 1
fi

version=$1

# Search for $version in the CHANGELOG file
grep_result=$(cat $(git rev-parse --show-toplevel)/CHANGELOG* | \
  egrep "^#+ $version")

if [[ -z $grep_result ]]; then
  echo "err: could not find $version in CHANGELOG"
  exit 1
fi

echo "success: found $version in CHANGELOG"
exit 0
