# CHANGELOG

## 0.7.0
- Remove `pygithub_merge`

## 0.6.3
- Use `git push --atomic` in `git_merge`

## 0.6.2
- Add `check_changelog, cc` and `check_package_json, cpj` to `usage`

## 0.6.1
- CHANGELOG checker now checks if file exists

## 0.6.0
- Added a package.json version checker

## 0.5.0
- Added a CHANGELOG checker

## 0.4.6
- Add some rollback logic to `git_merge` in case it fails

## 0.4.5
- Change logging prefixes

## 0.4.4
- Rework `git_merge` to unset local config only if local config did not exist previously
  - Pre existing local config will be restored otherwise

## 0.4.3
- Combine some inputs in `git_merge`

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
