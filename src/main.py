from enum import Enum
from dotenv import load_dotenv
import git
import os

class CommitMode(Enum):
  squash = 0
  rebase = 1
  merge = 2

class MergeCommitInfo():
  def __init__(self, branch: str, base_branch: str, commit_title: str,
    commit_author: str, commit_author_email: str, commit_mode: CommitMode):
    self.branch: str = branch
    self.base_branch: str = base_branch
    self.commit_title: str = commit_title
    self.commit_author: str = commit_author
    self.commit_author_email: str = commit_author_email
    self.commit_mode: CommitMode = commit_mode

class TagInfo():
  def __init__(self, tag: str, message: str):
    self.tag: str = tag
    self.message: str = message

def commit_branch(repo: git.Repo, merge_params: MergeCommitInfo,
  tag_params: TagInfo):
  r = repo.git

  if merge_params.commit_mode == CommitMode.squash:
    print('Merge mode: Squash\n')

    print(f'Checking out branch {merge_params.base_branch}...')
    r.checkout(merge_params.base_branch)
    print(f'Successfully checked out branch {merge_params.base_branch}!')

    print(f'Squash merging {merge_params.branch} to ' + \
      f'{merge_params.base_branch}...')
    r.merge('--squash', merge_params.branch)
    print(f'Successfully squash merged {merge_params.branch} to ' + \
      f'{merge_params.base_branch}!')

    print(f'Committing with message ${merge_params.commit_title}...')
    r.commit(
      '-m',
      merge_params.commit_title,
      '--author',
      f'{merge_params.commit_author} <{merge_params.commit_author_email}>')
    print(f'Successfully committed!')

    print(f'Tagging with tag {tag_params.tag}...')
    r.tag(
      '-a',
      tag_params.tag,
      '-m',
      tag_params.message)
    print(f'Successfully tagged!')

    r.push()
    r.push('--tags')

    print('Done!')
    return

  if commit_mode == CommitMode.rebase:
    raise Exception('Not yet implemented')
  if commit_mode == CommitMode.merge:
    raise Exception('Not yet implemented')

if __name__ == '__main__':
  load_dotenv()
  env = {
    'user': os.getenv('USER'),
    'email': os.getenv('EMAIL')
  }

  repo_dir = os.path.abspath('/Users/junha/cave/testzone/20201108')
# repo_dir = os.getcwd()
  repo: git.Repo = git.Repo(repo_dir)
  repo.config_writer().set_value('user', 'name', env['user']).release()
  repo.config_writer().set_value('user', 'email', env['email']).release()

  merge_params = MergeCommitInfo(
    't1',
    'master',
    'success wooo',
    'park-junha',
    'jpark3@scu.edu',
    CommitMode.squash)

  tag_params = TagInfo(
    '0.0.0',
    'wooo again')

  commit_branch(repo, merge_params, tag_params)

  # TODO: replace this HACK
  os.system('git config --local --unset user.name')
  os.system('git config --local --unset user.email')

  # does not close PR
