#!/usr/bin/env python3
import os
import re

count = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath) as f:
                content = f.read()

            original = content

            # Update import statements and references
            content = re.sub(r'from qi_', 'from qi_', content)
            content = re.sub(r'import qi_', 'import qi_', content)
            content = re.sub(r'qi_engine', 'qi_engine', content)
            content = re.sub(r'qi_processor', 'qi_processor', content)
            content = re.sub(r'qi_hub', 'qi_hub', content)
            content = re.sub(r'qi_bio', 'qi_bio', content)
            content = re.sub(r'qi_state', 'qi_state', content)
            content = re.sub(r'QIEngine', 'QIEngine', content)
            content = re.sub(r'QIProcessor', 'QIProcessor', content)
            content = re.sub(r'QIHub', 'QIHub', content)
            content = re.sub(r'QIBio', 'QIBio', content)
            content = re.sub(r'QIState', 'QIState', content)

            # But keep "post_quantum_crypto" as is
            content = re.sub(r'post_quantum_crypto', 'post_quantum_crypto', content)

            if content != original:
                with open(filepath, 'w') as f:
                    f.write(content)
                count += 1

print(f"Updated {count} files with quantum -> qi references")
