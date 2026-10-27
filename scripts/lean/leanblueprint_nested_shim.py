#!/usr/bin/env python3
"""leanblueprint shim for nested Lean projects (portable form).

leanblueprint 0.0.17 resolves the project root via GitPython
(git-root == lakefile dir) at module-import time; when a Lean corpus is
nested at docs/easci/lean inside a parent repository, the shim pins
the root relative to THIS FILE's location (blueprint/shim.py ->
docs/easci/lean). Works both locally and in CI.
"""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

fake_git = types.ModuleType("git")


class GitCommandError(Exception):
    pass


class InvalidGitRepositoryError(Exception):
    pass


class NoSuchPathError(Exception):
    pass


class _GitCmd:
    @staticmethod
    def config(*a, **k):
        raise GitCommandError("git config", 1)


class PinnedRepo:
    working_dir = ROOT
    git = _GitCmd

    def __init__(self, *a, **k):
        pass

    def is_dirty(self, *a, **k):
        return False

    def iter_commits(self):
        return iter(())

    def remote(self, *a, **k):
        raise ValueError("no remote configured")


fake_git.Repo = PinnedRepo  # type: ignore[attr-defined]
fake_git.exc = types.ModuleType("git.exc")
fake_git.exc.GitCommandError = GitCommandError  # type: ignore[attr-defined]
fake_git.exc.InvalidGitRepositoryError = InvalidGitRepositoryError  # type: ignore[attr-defined]
fake_git.repo = types.ModuleType("git.repo")
fake_git.repo.Repo = PinnedRepo  # type: ignore[attr-defined]
fake_git.__path__ = []
sys.modules["git"] = fake_git
sys.modules["git.exc"] = fake_git.exc
sys.modules["git.repo"] = fake_git.repo

import leanblueprint.client as c

sys.argv[0] = "leanblueprint"
c.cli()
