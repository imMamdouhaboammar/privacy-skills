#!/usr/bin/env bash
set -euo pipefail

# Privacy & Data Protection Skills Multi-Agent Installer
# Installs skills into Claude Code, Google Antigravity / Gemini CLI, Codex, and Cursor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_NAME="privacy-skills"

echo "========================================================"
echo "  Installing Privacy & Data Protection Skills"
echo "  Author: Mamdouh Aboammar (@imMamdouhaboammar)"
echo "  Ecosystem: Bug Killer Companion Network"
echo "========================================================"

# 1. Claude Code (~/.claude/skills)
if [ -d "$HOME/.claude" ]; then
  mkdir -p "$HOME/.claude/skills"
  rm -rf "$HOME/.claude/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.claude/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Claude Code -> $HOME/.claude/skills/${TARGET_NAME}"
fi

# 2. Google Antigravity & Gemini CLI (~/.gemini/config/skills)
if [ -d "$HOME/.gemini" ]; then
  mkdir -p "$HOME/.gemini/config/skills"
  rm -rf "$HOME/.gemini/config/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.gemini/config/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Antigravity / Gemini CLI -> $HOME/.gemini/config/skills/${TARGET_NAME}"
fi

# 3. Universal Agent Kernel (~/.agents/skills)
if [ -d "$HOME/.agents" ]; then
  mkdir -p "$HOME/.agents/skills"
  rm -rf "$HOME/.agents/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.agents/skills/${TARGET_NAME}"
  echo "  ✅ Installed for Universal Agent Kernel -> $HOME/.agents/skills/${TARGET_NAME}"
fi

# 4. OpenAI Codex (~/.codex/skills)
if [ -d "$HOME/.codex" ]; then
  mkdir -p "$HOME/.codex/skills"
  rm -rf "$HOME/.codex/skills/${TARGET_NAME}"
  cp -r "$SCRIPT_DIR" "$HOME/.codex/skills/${TARGET_NAME}"
  echo "  ✅ Installed for OpenAI Codex -> $HOME/.codex/skills/${TARGET_NAME}"
fi

echo ""
echo "Installation complete! 257 privacy procedures ready across your AI agents."
