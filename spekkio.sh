#!/bin/bash
BASE_DIR="$(cd "$(dirname "$0" )" && pwd )"
SRC_DIR=$BASE_DIR/src

NC='\033[0m'
GREEN_LOG='\033[0;32m'
BLUE_LOG='\033[0;36m'

function usage {
  echo "available options:"
  echo "[git_merge, gm] merge locally with git, with additional params:"
  echo "  [squash] squash merge"
  echo "  [rebase] rebase merge"
  echo "  [merge] merge with merge commit"
  echo "[pygithub_merge, pghm] merge a pull request with pygithub"
}

function invalid {
  echo "err: invalid parameters"
}

function log {
  sed -e "s/^/`printf "${2}"`[$1] `printf "${NC}"`/"
}

if [[ $# -eq 0 ]]; then
  usage
elif [[ $# -gt 0 ]]; then
  case $1 in
  pygithub_merge | pghm)
    echo "running pygithub_merge..." | log "spekkio:sh" $GREEN_LOG
    python3 $SRC_DIR/pygithub_merge/main.py | log \
      "spekkio:pygithub_merge:py" $BLUE_LOG
    exit_code=${PIPESTATUS[0]}
    if [[ $exit_code -ne 0 ]]; then
      echo "err: script exited with code $exit_code" | log "spekkio:sh" \
        $GREEN_LOG
      exit $exit_code
    fi
    echo "complete!" | log "spekkio:sh" $GREEN_LOG
    exit 0
    ;;
  git_merge | gm)
    if [[ $# -eq 1 ]]; then
      echo "warn: git_merge arg \$2 not provided, defaulting to squash" | \
        log "spekkio:sh" $GREEN_LOG
      git_merge_method=squash
    else
      git_merge_method=$2
    fi

    # Get user inputs
    echo -n "[base branch]: "
    read base_branch
    echo -n "[branch]: "
    read branch
    echo -n "[commit message]: "
    read commit_summary
    echo -n "[version]: "
    read version

    commit_message="($version) $commit_summary"

    echo "running git_merge with param $git_merge_method..." | \
      log "spekkio:sh" $GREEN_LOG
    $SRC_DIR/git_merge/main.sh $git_merge_method "$base_branch" "$branch" \
      "$commit_message" "$version" "$commit_summary" | log \
      "spekkio:git_merge:sh" $GREEN_LOG

    exit_code=${PIPESTATUS[0]}
    if [[ $exit_code -ne 0 ]]; then
      echo "err: script exited with code $exit_code" | log "spekkio:sh" \
        $GREEN_LOG
      exit $exit_code
    fi
    echo "git_merge complete!" | log "spekkio:sh" $GREEN_LOG
    exit 0
    ;;
  check_changelog | cc)
    if [[ $# -lt 2 ]]; then
      echo "err: check_changelog \$2 not provided" | log "spekkio:sh" \
        $GREEN_LOG
      exit 1
    fi

    version=$2

    echo "running check_changelog with param $version..." | \
      log "spekkio:sh" $GREEN_LOG
    $SRC_DIR/check_changelog/main.sh $version | log \
      "spekkio:check_changelog:sh" $GREEN_LOG

    exit_code=${PIPESTATUS[0]}
    if [[ $exit_code -ne 0 ]]; then
      echo "err: script exited with code $exit_code" | log "spekkio:sh" \
        $GREEN_LOG
      exit $exit_code
    fi
    echo "check_changelog complete!" | log "spekkio:sh" $GREEN_LOG
    exit 0
    ;;
  *)
    invalid
    usage
    exit 1
    ;;
  esac
else
  usage
fi
