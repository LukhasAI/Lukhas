#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


🖥️ CPU-Friendly Compliance Scanner
Monitor CPU usage and run compliance scan when safe
"""

import psutil
import time
import subprocess
import sys

def get_cpu_usage():
    """Get current CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def check_vscode_cpu():
    """Check if VS Code is using high CPU."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'code' in proc.info['name'].lower():
                cpu_percent = proc.cpu_percent()
                if cpu_percent and cpu_percent > 20:  # High CPU usage
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def wait_for_low_cpu(max_wait=300):  # 5 minutes max
    """Wait for CPU usage to drop below threshold."""
    print("🖥️ Monitoring CPU usage...")
    
    for i in range(max_wait):
        cpu_usage = get_cpu_usage()
        vscode_high = check_vscode_cpu()
        
        print(f"⏱️ CPU: {cpu_usage:.1f}% | VS Code High: {'Yes' if vscode_high else 'No'}")
        
        if cpu_usage < 50 and not vscode_high:
            print("✅ CPU usage is low - safe to run compliance scan!")
            return True
            
        if i % 10 == 0:  # Every 10 seconds
            print(f"⏳ Waiting for CPU to settle... ({i}/{max_wait}s)")
            
        time.sleep(1)
    
    print("⚠️ Timeout waiting for low CPU usage")
    return False

def run_compliance_scan():
    """Run the full compliance scan."""
    print("🛡️ Starting full compliance scan...")
    try:
        result = subprocess.run([
            sys.executable, 'symbol_validator.py', 
            '--critical-only', '--verbose'
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠️ Compliance scan timed out")
        return False
    except Exception as e:
        print(f"❌ Error running compliance scan: {e}")
        return False

def main():
    print("🛡️ CPU-Friendly Compliance Scanner")
    print("=" * 40)
    
    # Quick status check first
    print("🔍 Quick status check...")
    current_cpu = get_cpu_usage()
    vscode_high = check_vscode_cpu()
    
    print(f"📊 Current CPU: {current_cpu:.1f}%")
    print(f"🖥️ VS Code High CPU: {'Yes' if vscode_high else 'No'}")
    
    if current_cpu > 70 or vscode_high:
        print("⏳ CPU usage too high - waiting for it to settle...")
        if not wait_for_low_cpu():
            print("❌ Skipping full scan due to high CPU usage")
            return
    
    # Run the compliance scan
    success = run_compliance_scan()
    
    if success:
        print("✅ Compliance scan completed successfully!")
    else:
        print("❌ Compliance scan failed or timed out")

if __name__ == "__main__":
    main()
