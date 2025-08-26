#!/bin/bash

# VS Code Recovery Script
# Purpose: Recover from VS Code crashes and optimize performance
# Created: 2025-08-24

set -e

echo "========================================="
echo "VS Code Recovery & Optimization Script"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Detect VS Code variant
detect_vscode() {
    if command -v code &> /dev/null; then
        VSCODE_CMD="code"
        VSCODE_NAME="VS Code"
    elif command -v code-insiders &> /dev/null; then
        VSCODE_CMD="code-insiders"
        VSCODE_NAME="VS Code Insiders"
    else
        print_error "VS Code not found in PATH"
        exit 1
    fi
    print_status "Detected: $VSCODE_NAME"
}

# Function to clear VS Code cache
clear_cache() {
    echo ""
    echo "Clearing VS Code cache..."

    # macOS paths
    if [[ "$OSTYPE" == "darwin"* ]]; then
        CACHE_PATHS=(
            "$HOME/Library/Application Support/Code/Cache"
            "$HOME/Library/Application Support/Code/CachedData"
            "$HOME/Library/Application Support/Code/CachedExtensions"
            "$HOME/Library/Application Support/Code/CachedExtensionVSIXs"
            "$HOME/Library/Application Support/Code/Code Cache"
        )
    # Linux paths
    else
        CACHE_PATHS=(
            "$HOME/.config/Code/Cache"
            "$HOME/.config/Code/CachedData"
            "$HOME/.config/Code/CachedExtensions"
            "$HOME/.config/Code/CachedExtensionVSIXs"
            "$HOME/.config/Code/Code Cache"
        )
    fi

    for path in "${CACHE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            echo "  Removing: $path"
            rm -rf "$path"
        fi
    done

    print_status "Cache cleared successfully"
}

# Function to reset problematic extensions
reset_extensions() {
    echo ""
    echo "Resetting problematic extensions..."

    # List of extensions that commonly cause issues
    PROBLEMATIC_EXTENSIONS=(
        "ms-python.python"
        "ms-python.vscode-pylance"
        "GitHub.copilot"
        "GitHub.copilot-chat"
    )

    for ext in "${PROBLEMATIC_EXTENSIONS[@]}"; do
        if $VSCODE_CMD --list-extensions | grep -q "$ext"; then
            print_warning "Disabling extension: $ext"
            $VSCODE_CMD --disable-extension "$ext" 2>/dev/null || true
        fi
    done

    print_status "Extensions reset"
}

# Function to optimize settings
optimize_settings() {
    echo ""
    echo "Optimizing VS Code settings..."

    SETTINGS_FILE=".vscode/settings.json"

    if [ -f "$SETTINGS_FILE" ]; then
        # Create backup if not already done today
        BACKUP_FILE=".vscode/settings.json.recovery-backup-$(date +%Y%m%d)"
        if [ ! -f "$BACKUP_FILE" ]; then
            cp "$SETTINGS_FILE" "$BACKUP_FILE"
            print_status "Settings backed up to $BACKUP_FILE"
        fi

        print_status "Settings optimization complete"
    else
        print_warning "No settings.json found in current directory"
    fi
}

# Function to check system resources
check_resources() {
    echo ""
    echo "Checking system resources..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        MEM_FREE=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
        MEM_FREE_MB=$((MEM_FREE * 4096 / 1024 / 1024))

        if [ $MEM_FREE_MB -lt 1000 ]; then
            print_warning "Low memory available: ${MEM_FREE_MB}MB"
            print_warning "Consider closing other applications"
        else
            print_status "Memory available: ${MEM_FREE_MB}MB"
        fi

        # Check for zombie VS Code processes
        ZOMBIE_COUNT=$(ps aux | grep -i electron | grep -v grep | wc -l)
        if [ $ZOMBIE_COUNT -gt 5 ]; then
            print_warning "Found $ZOMBIE_COUNT Electron processes running"
            echo "  Run 'killall Electron' to clean up if VS Code is not running"
        fi
    else
        # Linux
        MEM_FREE=$(free -m | awk 'NR==2{print $7}')
        if [ $MEM_FREE -lt 1000 ]; then
            print_warning "Low memory available: ${MEM_FREE}MB"
        else
            print_status "Memory available: ${MEM_FREE}MB"
        fi
    fi
}

# Function to reinstall VS Code (optional)
reinstall_vscode() {
    echo ""
    read -p "Do you want to reinstall VS Code? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
            print_status "Reinstalling VS Code via Homebrew..."
            brew reinstall --cask visual-studio-code
        else
            print_warning "Please reinstall VS Code manually from https://code.visualstudio.com/"
        fi
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Select recovery option:"
    echo "1) Quick recovery (clear cache & check resources)"
    echo "2) Full recovery (all optimizations)"
    echo "3) Reset extensions only"
    echo "4) Clear cache only"
    echo "5) Check resources only"
    echo "6) Exit"
    echo ""
    read -p "Enter option (1-6): " choice

    case $choice in
        1)
            clear_cache
            check_resources
            ;;
        2)
            clear_cache
            reset_extensions
            optimize_settings
            check_resources
            reinstall_vscode
            ;;
        3)
            reset_extensions
            ;;
        4)
            clear_cache
            ;;
        5)
            check_resources
            ;;
        6)
            echo "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option"
            show_menu
            ;;
    esac
}

# Main execution
main() {
    detect_vscode

    # Check if VS Code is currently running
    if pgrep -x "Electron" > /dev/null; then
        print_warning "VS Code appears to be running"
        read -p "Do you want to continue anyway? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi

    show_menu

    echo ""
    print_status "Recovery complete!"
    echo ""
    echo "Recommendations:"
    echo "  • Restart VS Code after running this script"
    echo "  • Monitor memory usage with Activity Monitor (macOS) or top (Linux)"
    echo "  • Consider reducing the number of open editors/tabs"
    echo "  • Disable unused extensions to improve performance"
    echo ""
}

# Run main function
main
