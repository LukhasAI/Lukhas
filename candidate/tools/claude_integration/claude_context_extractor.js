// Claude Code Context Extractor
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
    let markdown = `# Claude Code Context - ${new Date().toLocaleString()}\n\n`;
    
    context.forEach(msg => {
        markdown += `## ${msg.role}\n${msg.content}\n\n`;
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
