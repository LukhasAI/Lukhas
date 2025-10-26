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
        echo "primary_source: lukhas_context.md"
        echo "secondary_source: claude.me"
        echo "optimized_for: gemini_ai"
        echo "last_updated: $(date '+%Y-%m-%d')"
        echo "navigation_note: \"lukhas_context.md files are the most comprehensive and frequently updated source of truth. gemini.md files provide Gemini-optimized summaries.\""
        echo "---"
        echo ""
        echo "> **For Gemini**: This file provides navigation context. For comprehensive details, check lukhas_context.md in this directory (primary source)."
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