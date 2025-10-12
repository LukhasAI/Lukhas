#!/bin/bash

# ╔════════════════════════════════════════════╗
# ║ 🚀 LUKHAS MIND — SYMBOLIC PUSH TO GITHUB   ║
# ╚════════════════════════════════════════════╝

REPO_NAME="lukhas_mind_private"
ORG_NAME="L-U-C-A-S-Cognitive AI"
REPO_VISIBILITY="private"

echo "🧠 Initializing symbolic GitHub push for: $REPO_NAME"
cd "$(dirname "$0")"

if gh repo view "$ORG_NAME/$REPO_NAME" > /dev/null 2>&1; then
  echo "🔁 Repo already exists on GitHub: $ORG_NAME/$REPO_NAME"
else
  echo "🛠️ Creating GitHub repo..."
  gh repo create "$ORG_NAME/$REPO_NAME" --private --confirm --description "Symbolic Cognitive Core — Lukhas_Mind Scaffold"
fi

if [ ! -d .git ]; then
  echo "🔧 Git not initialized. Initializing..."
  git init
  git branch -M main
  git remote add origin "https://github.com/$ORG_NAME/$REPO_NAME.git"
else
  echo "✅ Git already initialized."
fi

git add .
git commit -m "🌕 Initial commit — Symbolic Cognitive AI scaffold and encrypted structure"
git push -u origin main

echo "✅ LUKHAS_MIND pushed to GitHub: https://github.com/$ORG_NAME/$REPO_NAME"
open "https://github.com/$ORG_NAME/$REPO_NAME"
