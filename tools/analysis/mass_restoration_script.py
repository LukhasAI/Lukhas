#!/usr/bin/env python3
"""
Mass Restoration Script - Restore large batches of files from clean commits
"""

import json
import subprocess
from pathlib import Path


def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas")
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return "", 1

def get_current_error_files():
    """Get list of files with current syntax errors"""
    output, _ = run_command(".venv/bin/ruff check branding/ candidate/ tools/ products/ matriz/ next_gen/ lukhas/ --select=E999 --output-format=json --quiet")
    
    if not output:
        return []
    
    try:
        errors = json.loads(output)
        return [error["filename"] for error in errors]
    except json.JSONDecodeError:
        return []

def restore_files_in_batches(commit_hash, batch_size=50):
    """Restore files in batches from specified commit"""
    current_error_files = get_current_error_files()
    
    if not current_error_files:
        print("No current syntax errors found")
        return
    
    print(f"Found {len(current_error_files)} files with syntax errors")
    print(f"Restoring from commit {commit_hash} in batches of {batch_size}")
    
    total_restored = 0
    successful_restorations = []
    
    # Process in batches
    for i in range(0, len(current_error_files), batch_size):
        batch = current_error_files[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}: {len(batch)} files")
        
        # Restore each file in the batch
        for file_path in batch:
            print(f"  Restoring {file_path}...")
            result, returncode = run_command(f'git checkout {commit_hash} -- "{file_path}"')
            
            if returncode == 0:
                successful_restorations.append(file_path)
                total_restored += 1
            else:
                print(f"    ❌ Failed to restore {file_path}")
        
        # Check syntax error count after this batch
        error_count_output, _ = run_command(".venv/bin/ruff check branding/ candidate/ tools/ products/ matriz/ next_gen/ lukhas/ --select=F821 --statistics")
        if "syntax-error" in error_count_output:
            error_count = error_count_output.split()[0]
            print(f"  Current syntax errors: {error_count}")
        
        print(f"  Batch complete: {len(batch)} files restored")
    
    print(f"\n🎯 MASS RESTORATION COMPLETE:")
    print(f"Total files restored: {total_restored}")
    print(f"Successful restorations: {len(successful_restorations)}")
    
    # Final error count
    final_output, _ = run_command(".venv/bin/ruff check branding/ candidate/ tools/ products/ matriz/ next_gen/ lukhas/ --select=F821 --statistics")
    if "syntax-error" in final_output:
        final_count = final_output.split()[0]
        print(f"Final syntax error count: {final_count}")
    
    return successful_restorations

if __name__ == "__main__":
    # Use the commit right before automation experiment
    commit_hash = "f5b810c75"  # This was our successful manual fix commit
    
    print("Starting mass restoration from proven clean commit...")
    successful_restorations = restore_files_in_batches(commit_hash, batch_size=100)
    
    if successful_restorations:
        print(f"\n✅ Successfully restored {len(successful_restorations)} files")
        print("Ready to commit mass restoration!")
    else:
        print("\n❌ No files were successfully restored")
