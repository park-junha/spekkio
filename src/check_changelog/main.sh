#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "err: argument \$1 not supplied"
  exit 1
fi

version=$1
filename="CHANGELOG.md"
changelog_path="$(git rev-parse --show-toplevel)/$filename"

if [[ ! -f "$changelog_path" ]]; then
  echo "err: $changelog_path not found"
  exit 1
fi

# Search for $version in the CHANGELOG file
grep_result=$(cat $changelog_path | egrep "^#+ $version")

if [[ -z $grep_result ]]; then
  echo "err: could not find $version in CHANGELOG"
  exit 1
fi

echo "success: found $version in CHANGELOG"
exit 0
