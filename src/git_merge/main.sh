#!/bin/bash
BOT_USERNAME="spekkio-bot"
BOT_EMAIL="ttvdeidarabochi@gmail.com"

if [[ $# -eq 6 ]]; then
  base_branch=$2
  branch=$3
  commit_message=$4
  tag=$5
  tag_message=$6

  case $1 in
  squash)
    # Checkout to base branch and pull
    git checkout $base_branch && git pull
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Get author info from branch
    git checkout $branch
    rc=$?; [[ $rc -ne 0 ]] && exit $rc
    # TODO: below line assumes there is only one author
    author=$(git log $base_branch.. | grep Author | sed 's/Author: //' | \
      uniq)

    # Get pre existing local configs if they exist
    username_before=$(git config --local --list | egrep 'user\.name' | \
      sed 's/user\.name=//')
    useremail_before=$(git config --local --list | egrep 'user\.email' | \
      sed 's/user\.email=//')

    # Set (bot) committer info
    git config --local user.name "$BOT_USERNAME"
    git config --local user.email "$BOT_EMAIL"

    # Checkout to base branch and pull again
    git checkout $base_branch && git pull
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Merge
    git merge --squash $branch
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Commit
    git commit --message="$commit_message" --author="$author"
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Tag
    git tag --annotate $tag --message="$tag_message"
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Push commit and tag
    git push && git push --tags
    rc=$?; [[ $rc -ne 0 ]] && exit $rc

    # Unset (bot) committer info OR reset to configs before if they existed
    if [[ -z $username_before ]]; then
      git config --local --unset user.name
    else
      git config --local user.name "$username_before"
    fi
    if [[ -z $useremail_before ]]; then
      git config --local --unset user.email
    else
      git config --local user.email "$useremail_before"
    fi

    exit 0
    ;;
  rebase)
    echo "err: sorry, param rebase is not yet supported"
    exit 1
    ;;
  merge)
    echo "err: sorry, param rebase is not yet supported"
    exit 1
    ;;
  *)
    echo "err: invalid param $1"
    exit 1
    ;;
  esac
else
  echo "err: expected 6 params but received $#"
  exit 1
fi
