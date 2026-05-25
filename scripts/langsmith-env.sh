#!/usr/bin/env bash
# Load Career Forge .env and run LangSmith CLI with correct credentials.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export LANGSMITH_PROJECT="${LANGSMITH_PROJECT:-career-forge}"
export PATH="${HOME}/.local/bin:${PATH}"

if [[ $# -eq 0 ]]; then
  echo "langsmith-env: Career Forge LangSmith context"
  echo "  repo:    $ROOT"
  echo "  project: ${LANGSMITH_PROJECT}"
  if [[ -n "${LANGSMITH_API_KEY:-}" ]]; then
    echo "  api_key: set (${#LANGSMITH_API_KEY} chars)"
  else
    echo "  api_key: NOT SET — add LANGSMITH_API_KEY to .env (see .env.example)"
  fi
  if command -v langsmith >/dev/null 2>&1; then
    langsmith --version
  else
    echo "  cli:     not installed — curl -fsSL https://cli.langsmith.com/install.sh | sh"
    exit 127
  fi
  exit 0
fi

if ! command -v langsmith >/dev/null 2>&1; then
  echo "langsmith-env: langsmith CLI not found in PATH" >&2
  echo "Install: curl -fsSL https://cli.langsmith.com/install.sh | sh" >&2
  exit 127
fi

exec langsmith "$@"
