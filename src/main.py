from github import Github
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
  pr: PullRequest = repo.get_pull(merge_params.pr_id)

  # Check if PR was successfully fetched
  if pr.number != merge_params.pr_id:
    raise Exception(f'Could not fetch PR {merge_params.pr_id}')

  # Merge PR
  pr_merge_status: PullRequestMergeStatus = pr.merge(
    merge_params.commit_message,
    merge_params.commit_title,
    merge_params.merge_mode
  )

  # Check if PR was successfully merged
  if pr_merge_status.merged == False:
    raise Exception(f'PR {merge_params.pr_id} was not ' + \
      'successfully merged.')

  # Make an annotated tag at the resulting commit SHA
  resulting_tag: GitTag = repo.create_git_tag(
    tag_params.tag,
    tag_params.tag_message,
    pr_merge_status.sha,
    'commit'
  )
  annotated_tag: GitRef = repo.create_git_ref(
    f'refs/tags/{resulting_tag.tag}',
    resulting_tag.sha
  )

  # Check if tag was successfully created
  if annotated_tag.object.sha != resulting_tag.sha or \
    resulting_tag.tag != tag_params.tag:
    raise Exception(f'Tag {tag_params.tag} was not ' + \
      'successfully created.')

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

  merge_params = MergeCommitInfo(1, MergeMode.squash, 'test', 'moretest')
  tag_params = TagInfo('0.0.0', 'tagtest')

  merge_and_tag(repo, merge_params, tag_params)
