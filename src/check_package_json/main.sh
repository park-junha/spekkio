#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "err: argument \$1 not supplied"
  exit 1
fi

version=$1
package_json_path="$(git rev-parse --show-toplevel)/package.json"

if [[ ! -f "$package_json_path" ]]; then
  echo "err: $package_json_path not found"
  exit 1
fi

# Search and retrieve version property in package.json
package_json_version=$(cat $package_json_path | \
  grep '\"version\":' | sed 's/\"version": //' | xargs | sed 's/\,//')

if [[ -z $package_json_version ]]; then
  echo "err: could not retrieve version property from package.json"
  exit 1
elif [[ $package_json_version != $version ]]; then
  echo "err: version in package.json does not equal: $version"
  echo "     package.json version is: $package_json_version"
  exit 1
fi

echo "success: package.json version matches: $version"
exit 0
