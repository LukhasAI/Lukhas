#!/bin/bash

# Fixed script to create gemini.md files by copying from claude.me files
echo "🤖 Creating gemini.md files for Gemini AI navigation..."

count=0
failed=0

# Process claude.me files first
while IFS= read -r -d '' claude_file; do
    dir=$(dirname "$claude_file")
    gemini_file="$dir/gemini.md"
    
    echo "📝 Creating $gemini_file"
    
    # Create gemini.md with header and content from claude.me
    {
        echo "# Gemini AI Navigation Context"
        echo "*This file is optimized for Gemini AI navigation and understanding*"
        echo ""
        echo "---"
        echo "title: gemini"
        echo "slug: gemini.md"
        echo "source: claude.me"
        echo "optimized_for: gemini_ai"
        echo "last_updated: $(date '+%Y-%m-%d')"
        echo "---"
        echo ""
        cat "$claude_file"
    } > "$gemini_file"
    
    if [[ $? -eq 0 ]]; then
        count=$((count + 1))
        echo "✅ Created $gemini_file"
    else
        failed=$((failed + 1))
        echo "❌ Failed to create $gemini_file"
    fi
    
done < <(find . -name "claude.me" -type f -print0)

echo ""
echo "🎉 Completed creating gemini.md files from claude.me!"
echo "📊 Created: $count files"
echo "❌ Failed: $failed files"
echo ""
echo "🧭 Gemini AI can now navigate LUKHAS using gemini.md files!"