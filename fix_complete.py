with open('scripts/bench_t4_excellence.py', 'r') as f:
    lines = f.readlines()

# Find where the imports should be and rebuild correctly
new_lines = []
in_bad_section = False

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Skip the entire malformed section (lines 29-42 approximately)
    if line_num >= 29 and 'from bench_core import (' in line:
        # Start our clean import section
        new_lines.extend([
            'from bench_core import (\n',
            '    PerformanceBenchmark,  # - requires sys.path manipulation before import\n',
            ')\n',
            'from preflight_check import (\n', 
            '    PreflightValidator,  # - requires sys.path manipulation before import\n',
            ')\n',
            '\n',
            '# Module-level logger\n',
            'logger = logging.getLogger(__name__)\n',
            '\n'
        ])
        in_bad_section = True
        continue
    
    # Skip lines in the bad section until we find "# Suppress verbose logging"
    if in_bad_section:
        if '# Suppress verbose logging' in line:
            in_bad_section = False
            new_lines.append(line)  # Include this line
        continue
    
    # Keep all other lines
    new_lines.append(line)

with open('scripts/bench_t4_excellence.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Complete fix applied")
