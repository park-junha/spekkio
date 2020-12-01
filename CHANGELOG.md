# CHANGELOG

## 0.4.2
- Remove `version`

## 0.4.1
- `git_merge` now unsets local config after completing

## 0.4.0
- Renamed former `main.py` to `pygithub_merge`
- Added a main script at top level
- Added `git_merge` script

## 0.3.0
- Initial version of new Spekkio repository.
- Added a script that merges a PR and adds a tag to the resulting commit
  - Retains `spekkio-bot` as committer
  - DRAWBACKS: Opens an extra PR
