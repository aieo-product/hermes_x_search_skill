#!/usr/bin/env bash
# Install the hermes-x-search skill into Claude Code and/or Codex by
# symlinking this repository's skill directory into the user's skill dirs.
#
# Usage:
#   ./scripts/install.sh                 # install to whichever client is present
#   ./scripts/install.sh --claude        # Claude Code only
#   ./scripts/install.sh --codex         # Codex only
#   ./scripts/install.sh --uninstall     # remove the symlinks
#
# Re-running is safe (idempotent). The symlink approach means `git pull` in
# this repo immediately updates the installed skill.

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="hermes-x-search"
SKILL_SRC="${REPO_ROOT}/skills/${SKILL_NAME}"

CLAUDE_SKILL_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
CODEX_SKILL_DIR="${HOME}/.codex/skills/${SKILL_NAME}"

want_claude=auto
want_codex=auto
uninstall=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude)    want_claude=yes;  want_codex=no;  shift ;;
    --codex)     want_codex=yes;   want_claude=no; shift ;;
    --both)      want_claude=yes;  want_codex=yes; shift ;;
    --uninstall) uninstall=true;   shift ;;
    -h|--help)
      sed -n '2,12p' "${BASH_SOURCE[0]}"
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Auto-detect when not explicitly specified.
if [[ "${want_claude}" == "auto" ]]; then
  [[ -d "${HOME}/.claude" ]] && want_claude=yes || want_claude=no
fi
if [[ "${want_codex}" == "auto" ]]; then
  [[ -d "${HOME}/.codex" ]] && want_codex=yes || want_codex=no
fi

if [[ ! -d "${SKILL_SRC}" ]]; then
  echo "error: skill source not found at ${SKILL_SRC}" >&2
  exit 1
fi

install_one() {
  local target="$1"
  local label="$2"
  mkdir -p "$(dirname "${target}")"
  if [[ -L "${target}" ]]; then
    local current
    current="$(readlink "${target}")"
    if [[ "${current}" == "${SKILL_SRC}" ]]; then
      echo "✓ ${label}: already installed (symlink up to date)"
      return 0
    fi
    echo "✗ ${label}: existing symlink points elsewhere: ${current}" >&2
    echo "  remove it manually or re-run with --uninstall first" >&2
    return 1
  fi
  if [[ -e "${target}" ]]; then
    echo "✗ ${label}: ${target} exists and is not a symlink — refusing to overwrite" >&2
    return 1
  fi
  ln -s "${SKILL_SRC}" "${target}"
  echo "✓ ${label}: installed → ${target}"
}

uninstall_one() {
  local target="$1"
  local label="$2"
  if [[ -L "${target}" ]]; then
    rm "${target}"
    echo "✓ ${label}: removed symlink ${target}"
  elif [[ -e "${target}" ]]; then
    echo "✗ ${label}: ${target} is not a symlink — leaving it alone" >&2
  else
    echo "- ${label}: not installed"
  fi
}

if ${uninstall}; then
  [[ "${want_claude}" == "yes" ]] && uninstall_one "${CLAUDE_SKILL_DIR}" "Claude Code"
  [[ "${want_codex}" == "yes" ]]  && uninstall_one "${CODEX_SKILL_DIR}"  "Codex"
  exit 0
fi

[[ "${want_claude}" == "yes" ]] && install_one "${CLAUDE_SKILL_DIR}" "Claude Code"
[[ "${want_codex}" == "yes" ]]  && install_one "${CODEX_SKILL_DIR}"  "Codex"

if [[ "${want_claude}" == "no" && "${want_codex}" == "no" ]]; then
  echo "nothing to do: neither ~/.claude nor ~/.codex exists" >&2
  exit 1
fi

cat <<EOF

Next steps:
  1. Confirm Hermes Agent is set up:
       hermes status
  2. Confirm xAI Grok OAuth is logged in (look for 'xAI Grok' provider):
       hermes status | grep -i xai
  3. Confirm X (Twitter) Search tool is enabled (run interactively):
       hermes tools
  4. Try it from your client:
       Claude Code: just ask "Xで Claude Code を検索して"
       Codex:       codex "@example_user の最新ポストを取得して"
EOF
