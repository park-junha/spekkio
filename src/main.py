from enum import Enum
import git
import os

class CommitMode(Enum):
  squash: int = 0
  rebase: int = 1
  merge: int = 2

def commit_branch(repo: git.Repo, branch: str, base_branch: str,
  commit_message: str, commit_mode: CommitMode):
  r = repo.git
  if commit_mode == CommitMode.squash:
    print('Merge mode: Squash\n')

    print(f'Checking out branch {base_branch}...')
    r.checkout(base_branch)
    print(f'Successfully checked out branch {base_branch}!')

    print(f'Squash merging {branch} to {base_branch}...')
    r.merge('--squash', branch)
    print(f'Successfully squash merged {branch} to {base_branch}!')

    print(f'Committing with message ${commit_message}...')
    repo.index.commit(commit_message)
    print(f'Successfully committed!')

    print(f'Tagging with tag...')
    r.tag('-a', '0.0.0', '-m', 'test')
    print(f'Successfully tagged!')

#   r.push()
#   r.push('--tags')

    print('Done!')
    return

  if commit_mode == CommitMode.rebase:
    raise Exception('Not yet implemented')
  if commit_mode == CommitMode.merge:
    raise Exception('Not yet implemented')

if __name__ == '__main__':
  repo_dir = os.path.abspath('/Users/junha/cave/testzone/20201108')
  repo = git.Repo(repo_dir)
  commit_branch(repo, 't1', 'master', 'squash success!!', CommitMode.squash)
