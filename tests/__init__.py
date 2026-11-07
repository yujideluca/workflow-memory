"""Tests never inherit git's repository-location variables.

Git exports some of them to hooks (in a worktree GIT_DIR points at the real repository). A test that runs git in a
temporary clone would otherwise act on this repository: on 2026-11-07 a pre-push hook run from a worktree let the sync
tests push test commits to main. Removing them here covers every test module, the git helpers and mem's own git calls.
"""
import os

GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                     "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_PREFIX",
                     "GIT_QUARANTINE_PATH")
for _v in GIT_LOCATION_VARS:
    os.environ.pop(_v, None)
