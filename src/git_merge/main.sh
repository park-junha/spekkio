#!/bin/bash
BOT_USERNAME="spekkio-bot"
BOT_EMAIL="ttvdeidarabochi@gmail.com"

function rollback_gitconfig {
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
}

function rollback_commit {
  git reset --hard HEAD~1
}

function rollback_commit_and_tag {
  git tag --delete $tag
  rollback_commit
}

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
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git checkout $base_branch && git pull\" returned $rc"
      exit $rc
    fi

    # Get author info from branch
    git checkout $branch
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git checkout $branch\" returned $rc"
      exit $rc
    fi
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
    echo "applying temporary git config user\.name: $BOT_USERNAME"
    git config --local user.email "$BOT_EMAIL"
    echo "applying temporary git config user\.email: $BOT_EMAIL"

    # Checkout to base branch and pull again
    git checkout $base_branch && git pull
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git checkout $base_branch && git pull\" returned $rc"
      echo "rolling back temporary git config"
      rollback_gitconfig
      exit $rc
    fi

    # Squash merge
    git merge --squash $branch
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git merge --squash $base_branch\" returned $rc"
      echo "rolling back temporary git config"
      rollback_gitconfig
      exit $rc
    fi

    # Commit
    git commit --message="$commit_message" --author="$author"
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git merge --squash $base_branch\" returned $rc"
      echo "unstaging and discaring all items in working tree..."
      git reset --hard
      echo "rolling back temporary git config"
      rollback_gitconfig
      exit $rc
    fi

    # Tag
    git tag --annotate $tag --message="$tag_message"
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git tag --annotate $tag --message=\"$tag_message\"\""
      echo "     returned $rc"
      echo "rolling back commit..."
      rollback_commit
      echo "rolling back temporary git config"
      rollback_gitconfig
      exit $rc
    fi

    # Push commit and tag
    git push --atomic origin "$base_branch" "$tag"
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "err: \"git push --atomic origin \"$base_branch\" \"$tag\"\""
      echo "     returned $rc"
      echo "rolling back commit and tag..."
      rollback_commit_and_tag
      echo "rolling back temporary git config"
      rollback_gitconfig
      exit $rc
    fi

    # Unset (bot) committer info OR reset to configs before if they existed
    rollback_gitconfig

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
