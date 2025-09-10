#!/usr/bin/env python3
"""
ML-Based Error Pattern Learner
===============================
Machine learning system that analyzes historical fixes, git commits, and diagnostic patterns
to predict and prevent future errors before they occur.

Features:
- Git history analysis for error patterns
- Commit message classification
- File change pattern recognition
- Error prediction based on code changes
- Automated fix suggestion generation
- Integration with diagnostic orchestrator

ML Approaches:
- Pattern matching with fuzzy logic
- Statistical analysis of error frequencies
- Temporal correlation analysis
- Code complexity metrics correlation
- Developer behavior pattern recognition
"""

import ast
import re
import json
import subprocess
import sys
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
ML_DATA_DIR = ROOT / "reports" / "ml_patterns"
PATTERN_DB = ML_DATA_DIR / "pattern_database.json"


class CodePatternAnalyzer:
    """Analyzes code patterns to identify error-prone constructs"""
    
    def __init__(self):
        self.pattern_signatures = {}
        self.complexity_metrics = {}
    
    def analyze_file_complexity(self, file_path: Path) -> Dict:
        """Analyze code complexity metrics that correlate with errors"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(content)
            
            metrics = {
                'lines_of_code': len(content.split('\n')),
                'ast_nodes': len(list(ast.walk(tree))),
                'functions': 0,
                'classes': 0,
                'nested_depth': 0,
                'complexity_score': 0
            }
            
            # Count functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
            
            # Calculate complexity score
            metrics['complexity_score'] = (
                metrics['lines_of_code'] * 0.1 +
                metrics['ast_nodes'] * 0.05 +
                metrics['functions'] * 2 +
                metrics['classes'] * 3
            )
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Could not analyze complexity for {file_path}: {e}")
            return {'complexity_score': 0}
    
    def extract_fstring_patterns(self, content: str) -> List[Dict]:
        """Extract f-string usage patterns from content"""
        patterns = []
        
        # Find all f-strings
        fstring_regex = r'f["\']([^"\']*)["\']'
        matches = re.finditer(fstring_regex, content)
        
        for match in matches:
            fstring_content = match.group(1)
            
            # Analyze pattern characteristics
            pattern = {
                'has_format_spec': ':' in fstring_content and any(c in fstring_content.split(':')[-1] for c in 'fFeEgGdiouxXbcrsa'),
                'has_method_call': '()' in fstring_content,
                'has_brackets': '[' in fstring_content or ']' in fstring_content,
                'brace_count': fstring_content.count('{'),
                'bracket_count': fstring_content.count('['),
                'length': len(fstring_content),
                'complexity': len(re.findall(r'[{}\[\]().]', fstring_content))
            }
            
            patterns.append(pattern)
        
        return patterns
    
    def generate_pattern_signature(self, file_path: Path) -> str:
        """Generate a signature for code patterns in a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # Extract key pattern elements
            elements = []
            
            # F-string patterns
            fstring_patterns = self.extract_fstring_patterns(content)
            if fstring_patterns:
                avg_complexity = sum(p['complexity'] for p in fstring_patterns) / len(fstring_patterns)
                elements.append(f"fstring_avg_complexity:{avg_complexity:.2f}")
            
            # Test class patterns
            if 'class Test' in content:
                elements.append("has_test_classes")
                if 'def __init__(self' in content:
                    elements.append("test_class_with_init")
            
            # Import patterns
            import_count = content.count('import ')
            from_count = content.count('from ')
            elements.append(f"imports:{import_count}:{from_count}")
            
            # Generate signature hash
            signature_string = "|".join(sorted(elements))
            signature_hash = hashlib.md5(signature_string.encode()).hexdigest()[:8]
            
            self.pattern_signatures[str(file_path)] = {
                'signature': signature_hash,
                'elements': elements,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return signature_hash
            
        except Exception as e:
            logger.warning(f"Could not generate signature for {file_path}: {e}")
            return "unknown"


class GitHistoryAnalyzer:
    """Analyzes git history for error patterns and fix patterns"""
    
    def __init__(self):
        self.commit_patterns = []
        self.fix_patterns = {}
    
    def get_recent_commits(self, days: int = 30) -> List[Dict]:
        """Get recent commits with their metadata"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            result = subprocess.run([
                'git', 'log', '--since', since_date,
                '--pretty=format:%H|%s|%an|%ad|%d',
                '--date=iso', '--name-only'
            ], capture_output=True, text=True, cwd=ROOT)
            
            if result.returncode != 0:
                logger.warning("Could not get git history")
                return []
            
            commits = []
            current_commit = None
            
            for line in result.stdout.split('\n'):
                if '|' in line and len(line.split('|')) >= 4:
                    # New commit line
                    parts = line.split('|')
                    current_commit = {
                        'hash': parts[0],
                        'message': parts[1], 
                        'author': parts[2],
                        'date': parts[3],
                        'refs': parts[4] if len(parts) > 4 else '',
                        'files': []
                    }
                    commits.append(current_commit)
                elif current_commit and line.strip() and not line.startswith(' '):
                    # File name
                    current_commit['files'].append(line.strip())
            
            return commits
            
        except Exception as e:
            logger.error(f"Git history analysis failed: {e}")
            return []
    
    def classify_commit_type(self, commit_message: str) -> str:
        """Classify commit type based on message"""
        message_lower = commit_message.lower()
        
        # Fix-related keywords
        fix_keywords = ['fix', 'bugfix', 'error', 'syntax', 'import', 'resolve', 'correct']
        feature_keywords = ['add', 'implement', 'create', 'new', 'feature']
        refactor_keywords = ['refactor', 'cleanup', 'improve', 'optimize', 'enhance']
        test_keywords = ['test', 'testing', 'pytest', 'unittest']
        
        if any(keyword in message_lower for keyword in fix_keywords):
            return 'fix'
        elif any(keyword in message_lower for keyword in feature_keywords):
            return 'feature'
        elif any(keyword in message_lower for keyword in refactor_keywords):
            return 'refactor'
        elif any(keyword in message_lower for keyword in test_keywords):
            return 'test'
        else:
            return 'other'
    
    def extract_error_patterns_from_fixes(self, commits: List[Dict]) -> List[Dict]:
        """Extract error patterns from fix commits"""
        error_patterns = []
        
        for commit in commits:
            commit_type = self.classify_commit_type(commit['message'])
            
            if commit_type == 'fix':
                # Analyze files changed in fix commits
                python_files = [f for f in commit['files'] if f.endswith('.py')]
                
                pattern = {
                    'commit_hash': commit['hash'],
                    'message': commit['message'],
                    'files_affected': python_files,
                    'file_count': len(python_files),
                    'date': commit['date'],
                    'pattern_indicators': self.extract_fix_indicators(commit['message'])
                }
                
                error_patterns.append(pattern)
        
        return error_patterns
    
    def extract_fix_indicators(self, commit_message: str) -> List[str]:
        """Extract specific error indicators from commit messages"""
        indicators = []
        
        message_lower = commit_message.lower()
        
        # Specific error patterns
        if 'f-string' in message_lower or 'fstring' in message_lower:
            indicators.append('fstring_error')
        if 'syntax' in message_lower:
            indicators.append('syntax_error')
        if 'import' in message_lower:
            indicators.append('import_error')
        if 'test' in message_lower and ('collect' in message_lower or '__init__' in message_lower):
            indicators.append('test_collection_error')
        if 'bracket' in message_lower or 'brace' in message_lower:
            indicators.append('bracket_mismatch')
        if 'pytest' in message_lower or 'marker' in message_lower:
            indicators.append('pytest_config_error')
        
        return indicators


class ErrorPatternPredictor:
    """Predicts potential errors based on learned patterns"""
    
    def __init__(self):
        self.pattern_database = self.load_pattern_database()
        self.code_analyzer = CodePatternAnalyzer()
        self.git_analyzer = GitHistoryAnalyzer()
    
    def load_pattern_database(self) -> Dict:
        """Load existing pattern database"""
        if PATTERN_DB.exists():
            try:
                return json.loads(PATTERN_DB.read_text())
            except Exception as e:
                logger.warning(f"Could not load pattern database: {e}")
        
        return {
            'error_patterns': [],
            'fix_patterns': [],
            'file_signatures': {},
            'prediction_accuracy': {},
            'last_updated': None
        }
    
    def save_pattern_database(self):
        """Save updated pattern database"""
        ML_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.pattern_database['last_updated'] = datetime.now(timezone.utc).isoformat()
        PATTERN_DB.write_text(json.dumps(self.pattern_database, indent=2))
    
    def learn_from_git_history(self) -> Dict:
        """Learn error patterns from git commit history"""
        logger.info("📚 Learning from git history...")
        
        commits = self.git_analyzer.get_recent_commits(days=60)
        error_patterns = self.git_analyzer.extract_error_patterns_from_fixes(commits)
        
        # Update pattern database
        self.pattern_database['error_patterns'].extend(error_patterns)
        
        # Keep only recent patterns (last 100)
        self.pattern_database['error_patterns'] = self.pattern_database['error_patterns'][-100:]
        
        # Analyze pattern frequencies
        pattern_stats = self.analyze_pattern_frequencies()
        
        return {
            'commits_analyzed': len(commits),
            'fix_commits_found': len(error_patterns),
            'pattern_stats': pattern_stats
        }
    
    def analyze_pattern_frequencies(self) -> Dict:
        """Analyze frequency of different error patterns"""
        indicator_counts = Counter()
        file_type_counts = Counter()
        
        for pattern in self.pattern_database['error_patterns']:
            for indicator in pattern['pattern_indicators']:
                indicator_counts[indicator] += 1
            
            for file_path in pattern['files_affected']:
                if '/' in file_path:
                    directory = file_path.split('/')[0]
                    file_type_counts[directory] += 1
        
        return {
            'most_common_errors': dict(indicator_counts.most_common(10)),
            'most_affected_directories': dict(file_type_counts.most_common(10))
        }
    
    def predict_file_error_risk(self, file_path: Path) -> Dict:
        """Predict error risk for a specific file"""
        if not file_path.exists():
            return {'risk_score': 0, 'predictions': []}
        
        try:
            # Analyze file complexity
            complexity = self.code_analyzer.analyze_file_complexity(file_path)
            
            # Generate pattern signature
            signature = self.code_analyzer.generate_pattern_signature(file_path)
            
            # Calculate base risk from complexity
            risk_score = min(complexity['complexity_score'] / 1000, 1.0)
            
            predictions = []
            
            # Check against known error patterns
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # F-string risk assessment
            fstring_patterns = self.code_analyzer.extract_fstring_patterns(content)
            if fstring_patterns:
                high_complexity_fstrings = [p for p in fstring_patterns if p['complexity'] > 5]
                if high_complexity_fstrings:
                    risk_score = min(risk_score + 0.3, 1.0)
                    predictions.append({
                        'type': 'fstring_error',
                        'confidence': 0.7,
                        'description': f'Found {len(high_complexity_fstrings)} complex f-strings'
                    })
            
            # Test class risk
            if 'class Test' in content and 'def __init__(self' in content:
                risk_score = min(risk_score + 0.4, 1.0)
                predictions.append({
                    'type': 'test_collection_error',
                    'confidence': 0.8,
                    'description': 'Test class with __init__ method detected'
                })
            
            # Import complexity risk
            import_lines = [line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
            if len(import_lines) > 20:
                risk_score = min(risk_score + 0.2, 1.0)
                predictions.append({
                    'type': 'import_error',
                    'confidence': 0.5,
                    'description': f'High import complexity: {len(import_lines)} import statements'
                })
            
            return {
                'risk_score': risk_score,
                'predictions': predictions,
                'complexity_metrics': complexity,
                'pattern_signature': signature
            }
            
        except Exception as e:
            logger.warning(f"Could not predict risk for {file_path}: {e}")
            return {'risk_score': 0, 'predictions': []}
    
    def scan_codebase_for_risks(self, max_files: int = 100) -> Dict:
        """Scan entire codebase for error risks"""
        logger.info("🔍 Scanning codebase for error risks...")
        
        # Find Python files to scan
        python_files = list(ROOT.rglob("*.py"))
        
        # Prioritize test files and recently changed files
        test_files = [f for f in python_files if 'test' in str(f)]
        other_files = [f for f in python_files if 'test' not in str(f)]
        
        # Limit scan size
        files_to_scan = (test_files + other_files)[:max_files]
        
        high_risk_files = []
        risk_summary = {'high': 0, 'medium': 0, 'low': 0}
        
        for file_path in files_to_scan:
            risk_analysis = self.predict_file_error_risk(file_path)
            risk_score = risk_analysis['risk_score']
            
            if risk_score > 0.7:
                risk_level = 'high'
                high_risk_files.append({
                    'file': str(file_path),
                    'risk_score': risk_score,
                    'predictions': risk_analysis['predictions']
                })
            elif risk_score > 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            risk_summary[risk_level] += 1
        
        return {
            'files_scanned': len(files_to_scan),
            'risk_summary': risk_summary,
            'high_risk_files': sorted(high_risk_files, key=lambda x: x['risk_score'], reverse=True),
            'recommendations': self.generate_recommendations(high_risk_files)
        }
    
    def generate_recommendations(self, high_risk_files: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on risk analysis"""
        recommendations = []
        
        # Count prediction types
        prediction_counts = Counter()
        for file_data in high_risk_files:
            for prediction in file_data['predictions']:
                prediction_counts[prediction['type']] += 1
        
        # Generate specific recommendations
        if prediction_counts['fstring_error'] > 0:
            recommendations.append(
                f"Run enhanced f-string validation on {prediction_counts['fstring_error']} files with complex f-strings"
            )
        
        if prediction_counts['test_collection_error'] > 0:
            recommendations.append(
                f"Apply pytest class fixer to {prediction_counts['test_collection_error']} test files with __init__ methods"
            )
        
        if prediction_counts['import_error'] > 0:
            recommendations.append(
                f"Review import complexity in {prediction_counts['import_error']} files with high import counts"
            )
        
        return recommendations
    
    def run_ml_analysis(self) -> Dict:
        """Run complete ML-based error pattern analysis"""
        logger.info("🤖 Starting ML-based error pattern analysis")
        
        # Learn from git history
        git_learning = self.learn_from_git_history()
        
        # Scan codebase for risks
        risk_scan = self.scan_codebase_for_risks()
        
        # Save updated patterns
        self.save_pattern_database()
        
        # Generate comprehensive report
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'git_analysis': git_learning,
            'risk_scan': risk_scan,
            'pattern_database_stats': {
                'total_patterns': len(self.pattern_database['error_patterns']),
                'unique_signatures': len(self.pattern_database['file_signatures'])
            }
        }
        
        # Save analysis report
        self.save_analysis_report(report)
        
        logger.info(f"🤖 ML analysis complete: {len(risk_scan['high_risk_files'])} high-risk files identified")
        return report
    
    def save_analysis_report(self, report: Dict):
        """Save ML analysis report"""
        ML_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save latest report
        latest_report = ML_DATA_DIR / "ml_analysis_report.json"
        latest_report.write_text(json.dumps(report, indent=2))
        
        # Save timestamped report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_report = ML_DATA_DIR / f"ml_analysis_{timestamp}.json"
        timestamped_report.write_text(json.dumps(report, indent=2))


def main():
    """CLI interface for ML error pattern learner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ML-based error pattern learner")
    parser.add_argument("--scan-only", action="store_true", help="Only scan for risks, don't learn from git")
    parser.add_argument("--learn-only", action="store_true", help="Only learn from git history")
    parser.add_argument("--file", type=Path, help="Analyze specific file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    predictor = ErrorPatternPredictor()
    
    if args.file:
        # Analyze specific file
        risk_analysis = predictor.predict_file_error_risk(args.file)
        print(f"\n🎯 RISK ANALYSIS: {args.file}")
        print(f"Risk Score: {risk_analysis['risk_score']:.2f}")
        print(f"Predictions: {len(risk_analysis['predictions'])}")
        
        for prediction in risk_analysis['predictions']:
            print(f"  • {prediction['type']}: {prediction['description']} ({prediction['confidence']:.1%} confidence)")
        
        return 0
    
    # Run full analysis
    if args.learn_only:
        result = predictor.learn_from_git_history()
        print(f"📚 Git Learning Complete: {result['fix_commits_found']} fix patterns learned")
    elif args.scan_only:
        result = predictor.scan_codebase_for_risks()
        print(f"🔍 Risk Scan Complete: {len(result['high_risk_files'])} high-risk files found")
    else:
        result = predictor.run_ml_analysis()
        print(f"\n🤖 ML ANALYSIS RESULTS")
        print(f"=====================")
        print(f"Git commits analyzed: {result['git_analysis']['commits_analyzed']}")
        print(f"Fix patterns learned: {result['git_analysis']['fix_commits_found']}")
        print(f"Files scanned: {result['risk_scan']['files_scanned']}")
        print(f"High-risk files: {len(result['risk_scan']['high_risk_files'])}")
        
        # Show high-risk files
        if result['risk_scan']['high_risk_files']:
            print(f"\n🚨 HIGH-RISK FILES:")
            for file_data in result['risk_scan']['high_risk_files'][:5]:
                print(f"  • {file_data['file']} (risk: {file_data['risk_score']:.2f})")
        
        # Show recommendations
        if result['risk_scan']['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in result['risk_scan']['recommendations']:
                print(f"  • {rec}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())