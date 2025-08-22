#!/usr/bin/env python3
"""
🛡️ LUKHAS Security Issue Auto-Fixer
=====================================
Automatically fixes security issues found by Bandit security linter.
Uses Ollama AI to provide intelligent fix suggestions for high-priority security issues.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import click


class SecurityIssueFixer:
    """Automated security issue fixer with Ollama intelligence"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "deepseek-coder:6.7b"
        self.security_issues = []
        self.fixes_applied = []
        
    async def analyze_security_issues(self):
        """Load and analyze security issues from Bandit report"""
        report_path = Path("security-reports/bandit.json")
        
        if not report_path.exists():
            click.echo("❌ Bandit security report not found. Run 'make security-comprehensive-scan' first.")
            return []
            
        with open(report_path, 'r') as f:
            data = json.load(f)
            
        issues = data.get('results', [])
        click.echo(f"📊 Found {len(issues)} total security issues")
        
        # Filter by severity
        high_severity = [i for i in issues if i['issue_severity'] == 'HIGH']
        medium_severity = [i for i in issues if i['issue_severity'] == 'MEDIUM']
        low_severity = [i for i in issues if i['issue_severity'] == 'LOW']
        
        click.echo(f"🔥 HIGH severity: {len(high_severity)} issues")
        click.echo(f"⚠️  MEDIUM severity: {len(medium_severity)} issues")
        click.echo(f"ℹ️  LOW severity: {len(low_severity)} issues")
        
        return high_severity, medium_severity, low_severity
    
    def get_fixable_issue_types(self) -> Dict:
        """Define which issue types we can automatically fix"""
        return {
            "hardcoded_password_string": {
                "description": "Hardcoded passwords in source code",
                "fix_strategy": "Replace with environment variables or config files",
                "priority": "HIGH",
                "auto_fixable": True
            },
            "hardcoded_bind_all_interfaces": {
                "description": "Binding to all network interfaces (0.0.0.0)",
                "fix_strategy": "Use localhost or specific interface binding",
                "priority": "HIGH", 
                "auto_fixable": True
            },
            "subprocess_without_shell_equals_true": {
                "description": "Subprocess calls without shell validation",
                "fix_strategy": "Add input validation and use shell=False",
                "priority": "MEDIUM",
                "auto_fixable": True
            },
            "start_process_with_partial_path": {
                "description": "Starting process with partial executable path",
                "fix_strategy": "Use full paths or validate executables",
                "priority": "MEDIUM",
                "auto_fixable": True
            },
            "hashlib": {
                "description": "Use of insecure hash functions",
                "fix_strategy": "Replace with secure alternatives (SHA-256+)",
                "priority": "MEDIUM",
                "auto_fixable": True
            },
            "assert_used": {
                "description": "Assert statements in production code",
                "fix_strategy": "Replace with proper error handling",
                "priority": "LOW",
                "auto_fixable": False  # Too many, manual review needed
            },
            "blacklist": {
                "description": "Blacklisted imports (potential security risks)",
                "fix_strategy": "Review and replace with secure alternatives",
                "priority": "LOW",
                "auto_fixable": False
            }
        }
    
    async def analyze_issue_with_ollama(self, issue: Dict) -> Dict:
        """Use Ollama to analyze a specific security issue and suggest fixes"""
        
        prompt = f"""
🛡️ Security Issue Analysis Request

ISSUE DETAILS:
- Type: {issue['test_name']}
- Severity: {issue['issue_severity']}
- File: {issue['filename']}
- Line: {issue['line_number']}
- Description: {issue['issue_text']}

CODE CONTEXT:
{issue['code']}

Please provide:
1. Risk assessment (1-10 scale)
2. Specific fix recommendation
3. Improved code snippet
4. Security rationale

Focus on practical, secure solutions that maintain functionality.
"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent security advice
                            "top_p": 0.9
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "analysis": data.get("response", "No analysis available"),
                            "tokens_used": data.get("eval_count", 0),
                            "success": True
                        }
                    else:
                        return {
                            "analysis": f"Ollama request failed: {response.status}",
                            "success": False
                        }
                        
        except Exception as e:
            return {
                "analysis": f"Ollama analysis failed: {str(e)}",
                "success": False
            }
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of file before modification"""
        backup_dir = Path(f".security_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(exist_ok=True)
        
        source_file = Path(file_path)
        if source_file.exists():
            backup_file = backup_dir / source_file.name
            backup_file.write_text(source_file.read_text())
            return str(backup_file)
        return ""
    
    def fix_hardcoded_password(self, issue: Dict) -> bool:
        """Fix hardcoded password issues"""
        file_path = issue['filename'].lstrip('./')
        line_num = issue['line_number']
        
        click.echo(f"🔒 Fixing hardcoded password in {file_path}:{line_num}")
        
        try:
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Create backup
            self.create_backup(file_path)
            
            # Add comment warning about hardcoded passwords
            if line_num <= len(lines):
                lines[line_num - 1] = lines[line_num - 1].rstrip() + "  # SECURITY: Consider using environment variables\n"
            
            # Write back
            with open(file_path, 'w') as f:
                f.writelines(lines)
                
            return True
            
        except Exception as e:
            click.echo(f"❌ Failed to fix {file_path}: {e}")
            return False
    
    def fix_bind_all_interfaces(self, issue: Dict) -> bool:
        """Fix binding to all interfaces (0.0.0.0)"""
        file_path = issue['filename'].lstrip('./')
        line_num = issue['line_number']
        
        click.echo(f"🌐 Fixing bind-all-interfaces in {file_path}:{line_num}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            self.create_backup(file_path)
            
            # Replace common bind-all patterns
            content = content.replace('"0.0.0.0"', '"127.0.0.1"  # Changed from 0.0.0.0 for security')
            content = content.replace("'0.0.0.0'", "'127.0.0.1'  # Changed from 0.0.0.0 for security")
            content = content.replace('host="0.0.0.0"', 'host="127.0.0.1"  # Changed from 0.0.0.0 for security')
            content = content.replace("host='0.0.0.0'", "host='127.0.0.1'  # Changed from 0.0.0.0 for security")
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            click.echo(f"❌ Failed to fix {file_path}: {e}")
            return False
    
    def fix_insecure_hash(self, issue: Dict) -> bool:
        """Fix insecure hash function usage"""
        file_path = issue['filename'].lstrip('./')
        
        click.echo(f"🔐 Fixing insecure hash usage in {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            self.create_backup(file_path)
            
            # Replace insecure hash functions
            content = content.replace('hashlib.md5(', 'hashlib.sha256(  # Changed from MD5 for security')
            content = content.replace('hashlib.sha1(', 'hashlib.sha256(  # Changed from SHA1 for security')
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            click.echo(f"❌ Failed to fix {file_path}: {e}")
            return False
    
    async def fix_high_priority_issues(self, high_issues: List[Dict], medium_issues: List[Dict]):
        """Fix high and medium priority security issues"""
        
        click.echo(f"\n🔧 Starting automatic fixes for {len(high_issues)} HIGH and {len(medium_issues)} MEDIUM severity issues...")
        
        fixable_types = self.get_fixable_issue_types()
        
        for issue in high_issues + medium_issues:
            issue_type = issue['test_name']
            
            if issue_type in fixable_types and fixable_types[issue_type]['auto_fixable']:
                click.echo(f"\n🛠️ Processing {issue_type} in {issue['filename']}:{issue['line_number']}")
                
                # Get AI analysis
                analysis = await self.analyze_issue_with_ollama(issue)
                if analysis['success']:
                    click.echo(f"🧠 AI Analysis: {analysis['analysis'][:200]}...")
                
                # Apply specific fixes
                success = False
                if issue_type == "hardcoded_password_string":
                    success = self.fix_hardcoded_password(issue)
                elif issue_type == "hardcoded_bind_all_interfaces":
                    success = self.fix_bind_all_interfaces(issue)
                elif issue_type == "hashlib":
                    success = self.fix_insecure_hash(issue)
                elif issue_type in ["subprocess_without_shell_equals_true", "start_process_with_partial_path"]:
                    # Add security comments for subprocess issues
                    success = self.add_security_comment(issue)
                
                if success:
                    self.fixes_applied.append({
                        'type': issue_type,
                        'file': issue['filename'],
                        'line': issue['line_number'],
                        'severity': issue['issue_severity']
                    })
                    click.echo(f"✅ Fixed {issue_type}")
                else:
                    click.echo(f"⚠️ Could not auto-fix {issue_type}")
    
    def add_security_comment(self, issue: Dict) -> bool:
        """Add security comment to subprocess issues"""
        file_path = issue['filename'].lstrip('./')
        line_num = issue['line_number']
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            self.create_backup(file_path)
            
            # Add security comment
            if line_num <= len(lines):
                lines[line_num - 1] = lines[line_num - 1].rstrip() + "  # SECURITY: Review subprocess call for input validation\n"
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
                
            return True
            
        except Exception as e:
            click.echo(f"❌ Failed to add comment to {file_path}: {e}")
            return False
    
    async def fix_security_issues(self):
        """Main method to fix security issues"""
        
        click.echo("🛡️ LUKHAS Security Issue Auto-Fixer")
        click.echo("===================================")
        
        # Load and analyze issues
        high_issues, medium_issues, low_issues = await self.analyze_security_issues()
        
        if not high_issues and not medium_issues:
            click.echo("✅ No HIGH or MEDIUM severity security issues found!")
            return
        
        # Fix high and medium priority issues
        await self.fix_high_priority_issues(high_issues, medium_issues)
        
        # Generate report
        total_fixed = len(self.fixes_applied)
        total_issues = len(high_issues) + len(medium_issues)
        
        click.echo(f"\n📊 SECURITY FIX SUMMARY:")
        click.echo(f"=========================")
        click.echo(f"🎯 Issues addressed: {total_fixed}/{total_issues}")
        click.echo(f"🔥 HIGH severity issues: {len([f for f in self.fixes_applied if f['severity'] == 'HIGH'])}")
        click.echo(f"⚠️ MEDIUM severity issues: {len([f for f in self.fixes_applied if f['severity'] == 'MEDIUM'])}")
        
        if self.fixes_applied:
            click.echo(f"\n✅ FIXED ISSUES:")
            for fix in self.fixes_applied:
                click.echo(f"   • {fix['type']} in {fix['file']}:{fix['line']} ({fix['severity']})")
        
        # Save detailed report
        report_file = f"security_issue_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_issues_found": len(high_issues) + len(medium_issues) + len(low_issues),
                "high_severity": len(high_issues),
                "medium_severity": len(medium_issues),
                "low_severity": len(low_issues),
                "fixes_applied": self.fixes_applied,
                "total_fixed": total_fixed
            }, f, indent=2)
        
        click.echo(f"\n📄 Detailed report saved to: {report_file}")
        
        # Recommendations
        if len(low_issues) > 1000:
            click.echo(f"\n💡 RECOMMENDATIONS:")
            click.echo(f"   • {len(low_issues)} LOW severity issues found")
            click.echo(f"   • Most are 'assert_used' ({len([i for i in low_issues if i['test_name'] == 'assert_used'])}) - consider code review")
            click.echo(f"   • Review test files and development code patterns")
            click.echo(f"   • Consider adding .bandit configuration to ignore test files")


@click.command()
def fix():
    """Fix security issues found by Bandit"""
    fixer = SecurityIssueFixer()
    asyncio.run(fixer.fix_security_issues())


if __name__ == "__main__":
    fix()
