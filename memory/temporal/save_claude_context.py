#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Save Claude Code Chat Context
Saves the current Claude Code conversation context to a file for later reference.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_claude_context():
    """
    Attempts to retrieve Claude Code chat context.
    Note: This is a placeholder - Claude Code doesn't expose chat history via API.
    """
    print("Note: Claude Code doesn't provide direct API access to chat history.")
    print("To save your context, you can:")
    print("1. Copy the conversation from the Claude Code interface")
    print("2. Use browser developer tools to extract the conversation")
    print("3. Take screenshots of important parts")
    return None


def save_context_manually():
    """
    Guide user to manually save context.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create contexts directory
    context_dir = Path("/Users/agi_dev/Lukhas_PWM/docs/claude_contexts")
    context_dir.mkdir(parents=True, exist_ok=True)

    filename = f"claude_context_{timestamp}.md"
    filepath = context_dir / filename

    print("\nTo save your Claude Code context:")
    print("1. Copy your entire conversation from the Claude Code interface")
    print(f"2. I'll create a file at: {filepath}")
    print("3. Paste your conversation content when prompted\n")

    # Create template
    template = f"""# Claude Code Context - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Session Information
- Repository: LUKHAS PWM
- Date: {datetime.now().strftime("%Y-%m-%d")}
- Time: {datetime.now().strftime("%H:%M:%S")}

## Conversation Context

### User Query
[Paste your initial query here]

### Claude Response
[Paste Claude's responses here]

### Additional Context
[Add any relevant context, file changes, or important notes]

## Files Modified
[List any files that were created or modified during this session]

## Key Decisions
[Document any important decisions or approaches taken]

## Follow-up Tasks
[List any pending tasks or next steps]
"""

    # Write template
    with open(filepath, "w") as f:
        f.write(template)

    print(f"Template created at: {filepath}")
    print("\nYou can now:")
    print("1. Open the file and paste your conversation")
    print("2. Or use the command below to open in your default editor:")
    print(f"\n   open {filepath}")

    # Try to open in default editor
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(filepath)])
            print("\nFile opened in your default editor!")
    except:
        pass

    return filepath


def create_context_script():
    """
    Create a JavaScript snippet to extract Claude Code conversation.
    """
    script_content = """// Claude Code Context Extractor
// Run this in your browser console while on claude.ai/code

function extractClaudeContext() {
    const messages = document.querySelectorAll('[data-testid="message"]');
    let context = [];
    
    messages.forEach((msg, index) => {
        const role = msg.querySelector('[data-testid="message-role"]')?.textContent || 
                    (index % 2 === 0 ? 'User' : 'Assistant');
        const content = msg.querySelector('[data-testid="message-content"]')?.textContent || 
                       msg.textContent;
        
        context.push({
            role: role,
            content: content.trim(),
            timestamp: new Date().toISOString()
        });
    });
    
    // Format as markdown
    let markdown = `# Claude Code Context - ${new Date().toLocaleString()}\\n\\n`;
    
    context.forEach(msg => {
        markdown += `## ${msg.role}\\n${msg.content}\\n\\n`;
    });
    
    // Copy to clipboard
    navigator.clipboard.writeText(markdown).then(() => {
        console.log('Context copied to clipboard!');
        alert('Context copied to clipboard! You can now paste it into a file.');
    });
    
    return context;
}

// Run the extractor
extractClaudeContext();
"""

    script_path = Path(
        "/Users/agi_dev/Lukhas_PWM/tools/scripts/claude_context_extractor.js"
    )
    with open(script_path, "w") as f:
        f.write(script_content)

    print(f"\nJavaScript extractor created at: {script_path}")
    print("To use it:")
    print("1. Open Claude Code in your browser")
    print("2. Open Developer Console (F12)")
    print("3. Copy and paste the script from the file above")
    print("4. The conversation will be copied to your clipboard")


if __name__ == "__main__":
    print("Claude Code Context Saver")
    print("=" * 50)

    # Create manual save template
    filepath = save_context_manually()

    # Create browser extractor script
    create_context_script()

    print("\n✅ Context saving tools created successfully!")
    print("\nFor automated extraction in the future, consider:")
    print("- Using browser automation tools (Selenium, Playwright)")
    print("- Creating a browser extension")
    print("- Using Claude's API when it becomes available")
