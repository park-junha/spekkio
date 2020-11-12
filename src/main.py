from github import Github
from github.Branch import Branch
from github.GitTag import GitTag
from github.GitRef import GitRef
from github.PullRequest import PullRequest
from github.PullRequestMergeStatus import PullRequestMergeStatus
from github.Repository import Repository
from enum import Enum
from dotenv import load_dotenv
import os

class MergeMode(Enum):
  squash = 0
  rebase = 1
  merge = 2

class MergeCommitInfo():
  def __init__(self, pr_id: int, merge_mode: MergeMode, commit_title: str,
    commit_message: str = ''):
    self.pr_id: int = pr_id
    self.commit_title: str = commit_title
    self.commit_message: str = commit_message
    self.merge_mode: str = merge_mode.name

class TagInfo():
  def __init__(self, tag: str, tag_message: str):
    self.tag: str = tag
    self.tag_message: str = tag_message

def merge_and_tag(repo: Repository, merge_params: MergeCommitInfo,
  tag_params: TagInfo):

  # Get PR
  pr: PullRequest = repo.get_pull(number=merge_params.pr_id)

  # Check if PR was successfully fetched
  if pr.number != merge_params.pr_id:
    raise Exception(f'Could not fetch PR {merge_params.pr_id}')

  # Create temp branch off latest base branch
  source_base_branch: Branch = repo.get_branch(branch=pr.base.ref)

  temp_base_branch: str = f'temp_{pr.head.ref}'
  repo.create_git_ref(
    ref=f'refs/heads/{temp_base_branch}',
    sha=source_base_branch.commit.sha
  )

  # Change PR base branch to temp branch
  pr.edit(base=temp_base_branch)

  # Merge PR to temp branch
  pr_merge_status: PullRequestMergeStatus = pr.merge(
    commit_message=merge_params.commit_message,
    commit_title=merge_params.commit_title,
    merge_method=merge_params.merge_mode
  )

  # Check if PR was successfully merged
  if pr_merge_status.merged == False:
    raise Exception(f'PR {merge_params.pr_id} was not ' + \
      'successfully merged.')

  # Open a new PR to merge temp branch to original base branch
  temp_pr: PullRequest = repo.create_pull(
    title=f'[spekkio-bot] merge pr {merge_params.pr_id}',
    body='Opened by Spekkio.',
    base=source_base_branch.name,
    head=temp_base_branch,
    draft=False
  )

  # Rebase merge the new PR to original base branch
  temp_pr_merge_status: PullRequestMergeStatus = temp_pr.merge(
    commit_message=merge_params.commit_message,
    commit_title=merge_params.commit_title,
    merge_method=MergeMode.rebase.name
  )

  # Check if PR was successfully merged
  if temp_pr_merge_status.merged == False:
    raise Exception(f'Temp PR was not successfully merged.')

  # Delete temp branch
  repo.get_git_ref(ref=f'heads/{temp_base_branch}').delete()

  # TODO: Delete temp PR (?)

  # Make an annotated tag at the resulting commit SHA
  resulting_tag: GitTag = repo.create_git_tag(
    tag=tag_params.tag,
    message=tag_params.tag_message,
    object=temp_pr_merge_status.sha,
    type='commit'
  )
  annotated_tag: GitRef = repo.create_git_ref(
    ref=f'refs/tags/{resulting_tag.tag}',
    sha=resulting_tag.sha
  )

  # Check if tag was successfully created
  if annotated_tag.object.sha != resulting_tag.sha or \
    resulting_tag.tag != tag_params.tag:
    raise Exception(f'Tag {tag_params.tag} was not ' + \
      'successfully created.')

  # Success!
  return

if __name__ == '__main__':
  load_dotenv()
  env = {
    'token': os.getenv('TOKEN'),
    'username': os.getenv('USERNAME'),
    'repo': os.getenv('FULL_REPO_NAME')
  }
  conn = Github(env['token'])

  # Get GitHub repository
  try:
    repo = conn.get_repo(env['repo'])
  except:
    raise Exception('Repository not found')

  # TODO: replace MergeCommitInfo args with user inputs
  merge_params = MergeCommitInfo(20, MergeMode.squash, '(0.0.0) Finally it works', 'I think pygithub is better than gitpython')
  tag_params = TagInfo('0.0.0', 'Yes')

  merge_and_tag(repo, merge_params, tag_params)
