from github import Github
from github.Branch import Branch
from github.GitTag import GitTag
from github.GitRef import GitRef
from github.PullRequest import PullRequest
from github.PullRequestMergeStatus import PullRequestMergeStatus
from github.Repository import Repository

from dotenv import load_dotenv
from enum import Enum
import os
import sys

class DebugColors:
  SUCCESS = '\033[96m\033[1m'
  INFO = '\033[93m\033[1m'
  COLOR_END = '\033[0m'

def DEBUG(prefix: str, message: str, prefix_color = DebugColors.INFO):
  PREFIX_START = prefix_color
  print(f'{PREFIX_START}debug:{prefix}{DebugColors.COLOR_END}: {message}')

def SUCCESS(prefix: str, message: str):
  DEBUG(prefix, message, DebugColors.SUCCESS)

class MergeMode(Enum):
  squash = 0
  rebase = 1
  merge = 2

class MergeCommitInfo():
  def __init__(self, pr_id: int, merge_mode: MergeMode):
    self.pr_id: int = pr_id
    self.merge_mode: str = merge_mode.name

class TagInfo():
  def __init__(self, tag: str, tag_message: str):
    self.tag: str = tag
    self.tag_message: str = tag_message

def merge_and_tag(repo: Repository, merge_params: MergeCommitInfo,
  tag_params: TagInfo):

  # TODO: Need to implement rebase and merge
  #       Throw an exception for now
  if merge_params.merge_mode != MergeMode.squash.name:
    raise Exception(f'Merge mode f{merge_params.merge_mode.name} ' + \
      'not yet implemented.')

  # Get PR
  DEBUG('merge_and_tag', 'Getting PR number...')
  pr: PullRequest = repo.get_pull(number=merge_params.pr_id)
  SUCCESS('merge_and_tag', f'Successfully fetched PR {pr.number}')

  # Check if PR was successfully fetched
  if pr.number != merge_params.pr_id:
    raise Exception(f'Could not fetch PR {merge_params.pr_id}')

  # Create temp branch off latest base branch
  DEBUG(
    'merge_and_tag',
    f'Creating temporary branch from PR base branch: {pr.head.ref}...')
  source_base_branch: Branch = repo.get_branch(branch=pr.base.ref)

  temp_base_branch: str = f'temp_{pr.head.ref}'

  repo.create_git_ref(
    ref = f'refs/heads/{temp_base_branch}',
    sha = source_base_branch.commit.sha
  )
  SUCCESS('merge_and_tag', f'Created temporary branch: {temp_base_branch}')

  # Change PR base branch to temp branch
  DEBUG(
    'merge_and_tag',
    f'Switching PR base branch {pr.head.ref} to {temp_base_branch}...')
  pr.edit(base=temp_base_branch)

  # Merge PR to temp branch
  DEBUG('merge_and_tag', f'Merging PR {pr.number}...')
  pr_merge_status: PullRequestMergeStatus = pr.merge(
    commit_title = pr.title,
    commit_message = pr.body,
    merge_method = merge_params.merge_mode
  )

  # Check if PR was successfully merged
  if pr_merge_status.merged == False:
    raise Exception(f'PR {merge_params.pr_id} was not ' + \
      'successfully merged.')

  # Open a new PR to merge temp branch to original base branch
  DEBUG('merge_and_tag', 'Opening intermediary PR with temp branch...')
  temp_pr: PullRequest = repo.create_pull(
    title = f'(temp:spekkio-bot) merge pr {merge_params.pr_id}',
    body = 'Opened by Spekkio.',
    base = source_base_branch.name,
    head = temp_base_branch,
    draft = False
  )

  # Rebase merge the new PR to original base branch
  DEBUG(
    'merge_and_tag',
    f'Rebase merging temp branch to {source_base_branch.name}...')
  temp_pr_merge_status: PullRequestMergeStatus = temp_pr.merge(
    merge_method = MergeMode.rebase.name
  )

  # Check if PR was successfully merged
  if temp_pr_merge_status.merged == False:
    raise Exception(f'Temp PR was not successfully merged.')

  # Delete temp branch
  DEBUG('merge_and_tag', f'Deleting temp branch {temp_base_branch}...')
  repo.get_git_ref(ref = f'heads/{temp_base_branch}').delete()

  # TODO: Delete temp PR (?)

  # Make an annotated tag at the resulting commit SHA
  DEBUG('merge_and_tag', f'Creating annotated tag {tag_params.tag}...')
  resulting_tag: GitTag = repo.create_git_tag(
    tag = tag_params.tag,
    message = tag_params.tag_message,
    object = temp_pr_merge_status.sha,
    type = 'commit'
  )
  annotated_tag: GitRef = repo.create_git_ref(
    ref = f'refs/tags/{resulting_tag.tag}',
    sha = resulting_tag.sha
  )

  # Check if tag was successfully created
  if annotated_tag.object.sha != resulting_tag.sha or \
    resulting_tag.tag != tag_params.tag:
    raise Exception(f'Tag {tag_params.tag} was not ' + \
      'successfully created.')

  # Success!
  SUCCESS('merge_and_tag', 'Done!')
  return

if __name__ == '__main__':
  # Load environmental variables
  DEBUG('main', 'Loading environmental variables...')
  load_dotenv()
  env = {
    'token': os.getenv('TOKEN')
  }

  DEBUG('main', 'Establishing connection to GitHub...')
  conn = Github(env['token'])

  # Parse user input
  DEBUG('main', 'Parsing user input...')
  env['repo']: str = sys.argv[1]
  env['pr_id']: int = int(sys.argv[2])
  env['tag']: str = sys.argv[3]
  env['tag_message']: str = sys.argv[4]

  # Get GitHub repository
  try:
    DEBUG('main', 'Fetching GitHub repository...')
    repo = conn.get_repo(env['repo'])
  except:
    raise Exception('Repository not found')

  # Create merge_params and tag_params from user input
  DEBUG('main', 'Creating parameters for function merge_and_tag...')
  merge_params = MergeCommitInfo(env['pr_id'], MergeMode.squash)
  tag_params = TagInfo(env['tag'], env['tag_message'])

  DEBUG('main', 'Running function merge_and_tag...')
  merge_and_tag(repo, merge_params, tag_params)

  SUCCESS('main', 'Done!')
