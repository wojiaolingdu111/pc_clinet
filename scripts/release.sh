#!/usr/bin/env bash
set -euo pipefail

# Release helper for Debian-first workflow.
# Usage:
#   scripts/release.sh 1.0.1
#   scripts/release.sh 1.0.1 origin github

VERSION="${1:-}"
PRIMARY_REMOTE="${2:-origin}"
SECONDARY_REMOTE="${3:-github}"

if [[ -z "$VERSION" ]]; then
  echo "Usage: scripts/release.sh <version> [primary_remote] [secondary_remote]"
  exit 1
fi

TAG="v${VERSION#v}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository"
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: working tree has uncommitted changes. Commit or stash before release."
  exit 1
fi

if ! git remote get-url "$PRIMARY_REMOTE" >/dev/null 2>&1; then
  echo "Error: remote '$PRIMARY_REMOTE' not found"
  exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Error: tag '$TAG' already exists locally"
  exit 1
fi

echo "[1/4] Push current branch to $PRIMARY_REMOTE"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git push "$PRIMARY_REMOTE" "$CURRENT_BRANCH"

echo "[2/4] Create tag $TAG"
git tag "$TAG"

echo "[3/4] Push tag to $PRIMARY_REMOTE"
git push "$PRIMARY_REMOTE" "$TAG"

echo "[4/4] Push branch and tag to secondary remote if configured"
if git remote get-url "$SECONDARY_REMOTE" >/dev/null 2>&1; then
  git push "$SECONDARY_REMOTE" "$CURRENT_BRANCH"
  git push "$SECONDARY_REMOTE" "$TAG"
  echo "Secondary push completed: $SECONDARY_REMOTE"
else
  echo "Secondary remote '$SECONDARY_REMOTE' not found, skipped."
fi

echo "Release trigger completed for tag $TAG"
