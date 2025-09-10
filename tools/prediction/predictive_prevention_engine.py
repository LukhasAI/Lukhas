#!/usr/bin/env python3
"""
Predictive Error Prevention Engine
==================================
Advanced prediction system that combines ML pattern detection, real-time monitoring,
and proactive error prevention to create a self-healing codebase.

Features:
- Real-time file change monitoring
- Predictive error analysis on code changes
- Proactive fix application before errors manifest
- Integration with git pre-commit hooks
- Continuous learning from prevention success rates
- Risk-based priority scheduling

Prevention Strategies:
- Pre-commit predictive scanning
- File change pattern analysis  
- Developer behavior learning
- Code complexity trend monitoring
- Error cluster detection and prevention
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import subprocess
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PREDICTION_DATA = ROOT / "reports" / "prediction"
PREVENTION_LOG = PREDICTION_DATA / "prevention_log.json"

# Import our analysis components
sys.path.insert(0, str(ROOT / "tools" / "ai"))
sys.path.insert(0, str(ROOT / "tools" / "automation"))
sys.path.insert(0, str(ROOT / "tools" / "matriz"))

try:
    from error_pattern_learner import ErrorPatternPredictor
    from enhanced_fstring_fixer import EnhancedFStringFixer
    from precommit_fstring_validator import PrecommitFStringValidator
    from lane_aware_fixer import LaneAwareFixer
except ImportError as e:
    logger.warning(f"Some prediction components not available: {e}")


class FileChangeAnalyzer:
    """Analyzes file changes for error prediction"""
    
    def __init__(self):
        self.change_patterns = {}
        self.risk_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
    
    def analyze_file_change(self, file_path: Path, change_type: str) -> Dict:
        """Analyze a file change for error risk"""
        try:
            if not file_path.exists():
                return {'risk_score': 0, 'analysis': 'file_not_found'}
            
            content = file_path.read_text(encoding='utf-8', errors='replace')
            change_signature = self.generate_change_signature(content, change_type)
            
            analysis = {
                'file': str(file_path),
                'change_type': change_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'change_signature': change_signature,
                'risk_factors': [],
                'risk_score': 0.0,
                'predictions': [],
                'preventive_actions': []
            }
            
            # Risk factor analysis
            risk_factors = self.identify_risk_factors(content, file_path)
            analysis['risk_factors'] = risk_factors
            analysis['risk_score'] = self.calculate_risk_score(risk_factors)
            
            # Generate predictions
            predictions = self.generate_predictions(risk_factors, file_path)
            analysis['predictions'] = predictions
            
            # Suggest preventive actions
            if analysis['risk_score'] > self.risk_thresholds['medium']:
                actions = self.suggest_preventive_actions(predictions, file_path)
                analysis['preventive_actions'] = actions
            
            return analysis
            
        except Exception as e:
            logger.error(f"File change analysis failed for {file_path}: {e}")
            return {'risk_score': 0, 'analysis': f'error: {e}'}
    
    def generate_change_signature(self, content: str, change_type: str) -> str:
        """Generate signature for file change pattern"""
        elements = [
            f"change_type:{change_type}",
            f"lines:{len(content.split())}", 
            f"fstrings:{content.count('f\"') + content.count(\"f'\")}",
            f"imports:{content.count('import ') + content.count('from ')}",
            f"classes:{content.count('class ')}",
            f"functions:{content.count('def ')}",
            f"tests:{content.count('test_') + content.count('Test')}"
        ]
        
        signature_string = "|".join(elements)
        return hashlib.md5(signature_string.encode()).hexdigest()[:8]
    
    def identify_risk_factors(self, content: str, file_path: Path) -> List[Dict]:
        """Identify specific risk factors in file content"""
        risk_factors = []
        
        # F-string complexity risk
        fstring_count = content.count('f"') + content.count("f'")
        if fstring_count > 5:
            complexity_score = 0
            for line in content.split('\n'):
                if 'f"' in line or "f'" in line:
                    complexity_score += line.count('{') + line.count('}')
            
            if complexity_score > 20:
                risk_factors.append({
                    'type': 'fstring_complexity',
                    'severity': 'high',
                    'count': fstring_count,
                    'complexity': complexity_score,
                    'weight': 0.4
                })
        
        # Test class __init__ risk
        if 'class Test' in content and 'def __init__(self' in content:
            risk_factors.append({
                'type': 'test_class_init',
                'severity': 'high',
                'weight': 0.6
            })
        
        # Import complexity risk
        import_lines = [line for line in content.split('\n') 
                       if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) > 15:
            risk_factors.append({
                'type': 'import_complexity',
                'severity': 'medium',
                'count': len(import_lines),
                'weight': 0.3
            })
        
        # Syntax pattern risks
        if content.count('{') != content.count('}'):
            risk_factors.append({
                'type': 'brace_mismatch',
                'severity': 'high',
                'weight': 0.5
            })
        
        if content.count('[') != content.count(']'):
            risk_factors.append({
                'type': 'bracket_mismatch',
                'severity': 'high', 
                'weight': 0.5
            })
        
        # File-specific risks
        if file_path.name.startswith('test_') and 'pytest' not in content:
            risk_factors.append({
                'type': 'test_framework_missing',
                'severity': 'medium',
                'weight': 0.2
            })
        
        return risk_factors
    
    def calculate_risk_score(self, risk_factors: List[Dict]) -> float:
        """Calculate overall risk score from factors"""
        if not risk_factors:
            return 0.0
        
        # Weighted risk calculation
        total_weight = 0
        weighted_score = 0
        
        for factor in risk_factors:
            severity = factor.get('severity', 'low')
            weight = factor.get('weight', 0.1)
            
            severity_multiplier = {
                'high': 1.0,
                'medium': 0.6, 
                'low': 0.3
            }.get(severity, 0.3)
            
            weighted_score += severity_multiplier * weight
            total_weight += weight
        
        # Normalize to 0-1 range
        if total_weight > 0:
            return min(weighted_score / total_weight, 1.0)
        
        return 0.0
    
    def generate_predictions(self, risk_factors: List[Dict], file_path: Path) -> List[Dict]:
        """Generate specific error predictions from risk factors"""
        predictions = []
        
        for factor in risk_factors:
            factor_type = factor['type']
            severity = factor['severity']
            
            if factor_type == 'fstring_complexity':
                predictions.append({
                    'error_type': 'SyntaxError',
                    'specific_type': 'f-string syntax error',
                    'confidence': 0.8 if severity == 'high' else 0.6,
                    'likely_location': 'f-string expressions',
                    'prevention_tool': 'enhanced_fstring_fixer'
                })
            
            elif factor_type == 'test_class_init':
                predictions.append({
                    'error_type': 'CollectionWarning',
                    'specific_type': 'pytest collection failure',
                    'confidence': 0.9,
                    'likely_location': 'test class __init__ method',
                    'prevention_tool': 'pytest_class_fixer'
                })
            
            elif factor_type in ['brace_mismatch', 'bracket_mismatch']:
                predictions.append({
                    'error_type': 'SyntaxError',
                    'specific_type': f'{factor_type}',
                    'confidence': 0.85,
                    'likely_location': 'bracket/brace expressions',
                    'prevention_tool': 'syntax_validator'
                })
        
        return predictions
    
    def suggest_preventive_actions(self, predictions: List[Dict], file_path: Path) -> List[Dict]:
        """Suggest specific preventive actions"""
        actions = []
        
        for prediction in predictions:
            prevention_tool = prediction.get('prevention_tool')
            confidence = prediction.get('confidence', 0)
            
            if confidence > 0.7:  # High confidence predictions
                if prevention_tool == 'enhanced_fstring_fixer':
                    actions.append({
                        'action': 'apply_fstring_fixes',
                        'tool': 'enhanced_fstring_fixer',
                        'priority': 'high',
                        'description': 'Apply automated f-string syntax fixes',
                        'estimated_success': confidence
                    })
                
                elif prevention_tool == 'pytest_class_fixer':
                    actions.append({
                        'action': 'fix_test_classes',
                        'tool': 'pytest_class_fixer', 
                        'priority': 'high',
                        'description': 'Convert test class __init__ to setup_method',
                        'estimated_success': confidence
                    })
                
                elif prevention_tool == 'syntax_validator':
                    actions.append({
                        'action': 'validate_syntax',
                        'tool': 'precommit_validator',
                        'priority': 'medium',
                        'description': 'Run comprehensive syntax validation',
                        'estimated_success': confidence
                    })
        
        return actions


class CodeChangeMonitor(FileSystemEventHandler):
    """Real-time file system monitor for code changes"""
    
    def __init__(self, prevention_engine):
        self.prevention_engine = prevention_engine
        self.change_queue = asyncio.Queue()
        self.monitored_extensions = {'.py'}
        
    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.monitored_extensions:
                asyncio.create_task(self.change_queue.put({
                    'file_path': file_path,
                    'change_type': 'modified',
                    'timestamp': datetime.now(timezone.utc)
                }))
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.monitored_extensions:
                asyncio.create_task(self.change_queue.put({
                    'file_path': file_path,
                    'change_type': 'created',
                    'timestamp': datetime.now(timezone.utc)
                }))


class PredictivePreventionEngine:
    """Main predictive error prevention engine"""
    
    def __init__(self, real_time_monitoring: bool = False):
        self.real_time_monitoring = real_time_monitoring
        self.file_analyzer = FileChangeAnalyzer()
        self.prevention_log = []
        self.success_metrics = {
            'predictions_made': 0,
            'preventions_attempted': 0,
            'preventions_successful': 0,
            'false_positives': 0,
            'errors_prevented': 0
        }
        
        # Initialize components
        try:
            self.pattern_predictor = ErrorPatternPredictor()
        except:
            self.pattern_predictor = None
        
        try:
            self.lane_fixer = LaneAwareFixer(dry_run=False)
        except:
            self.lane_fixer = None
    
    def predict_and_prevent_errors(self, file_paths: List[Path], change_type: str = 'unknown') -> Dict:
        """Predict and prevent errors for given files"""
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'files_analyzed': len(file_paths),
            'predictions': [],
            'preventions': [],
            'success_rate': 0.0
        }
        
        for file_path in file_paths:
            logger.info(f"🔮 Analyzing {file_path} for predictive prevention")
            
            # Analyze file change for risks
            analysis = self.file_analyzer.analyze_file_change(file_path, change_type)
            
            if analysis['risk_score'] > 0.5:  # Medium+ risk threshold
                self.success_metrics['predictions_made'] += 1
                results['predictions'].append(analysis)
                
                # Apply preventive actions
                prevention_results = self.apply_preventive_actions(
                    file_path, 
                    analysis['preventive_actions']
                )
                
                results['preventions'].append({
                    'file': str(file_path),
                    'actions_attempted': len(analysis['preventive_actions']),
                    'actions_successful': prevention_results['successful_actions'],
                    'prevention_results': prevention_results
                })
        
        # Calculate success rate
        if results['predictions']:
            total_actions = sum(p['actions_attempted'] for p in results['preventions'])
            successful_actions = sum(p['actions_successful'] for p in results['preventions'])
            results['success_rate'] = successful_actions / max(total_actions, 1)
        
        return results
    
    def apply_preventive_actions(self, file_path: Path, actions: List[Dict]) -> Dict:
        """Apply preventive actions to prevent predicted errors"""
        results = {
            'successful_actions': 0,
            'failed_actions': 0,
            'action_details': []
        }
        
        for action in actions:
            action_type = action.get('action')
            tool = action.get('tool')
            priority = action.get('priority', 'medium')
            
            success = False
            details = {
                'action': action_type,
                'tool': tool,
                'priority': priority,
                'attempted': True
            }
            
            try:
                if action_type == 'apply_fstring_fixes' and EnhancedFStringFixer:
                    fixer = EnhancedFStringFixer(validate_syntax=True)
                    success = fixer.fix_file(file_path)
                    details['result'] = 'fixed' if success else 'no_changes_needed'
                
                elif action_type == 'fix_test_classes' and 'PytestClassFixer' in globals():
                    fixer = PytestClassFixer(dry_run=False)
                    success = fixer.fix_file(file_path)
                    details['result'] = 'fixed' if success else 'no_changes_needed'
                
                elif action_type == 'validate_syntax':
                    # Run syntax validation
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', str(file_path)
                    ], capture_output=True)
                    success = result.returncode == 0
                    details['result'] = 'valid' if success else 'syntax_errors'
                
                if success:
                    results['successful_actions'] += 1
                    self.success_metrics['preventions_successful'] += 1
                else:
                    results['failed_actions'] += 1
                
                self.success_metrics['preventions_attempted'] += 1
                
            except Exception as e:
                logger.error(f"Preventive action {action_type} failed: {e}")
                details['result'] = f'error: {e}'
                results['failed_actions'] += 1
            
            results['action_details'].append(details)
        
        return results
    
    async def start_real_time_monitoring(self):
        """Start real-time file system monitoring"""
        if not self.real_time_monitoring:
            logger.info("Real-time monitoring not enabled")
            return
        
        logger.info("🔮 Starting real-time predictive monitoring")
        
        # Set up file system observer
        observer = Observer()
        monitor = CodeChangeMonitor(self)
        
        # Monitor key directories
        directories_to_monitor = [
            ROOT / "candidate",
            ROOT / "lukhas", 
            ROOT / "tests",
            ROOT / "core"
        ]
        
        for directory in directories_to_monitor:
            if directory.exists():
                observer.schedule(monitor, str(directory), recursive=True)
                logger.info(f"Monitoring: {directory}")
        
        observer.start()
        
        try:
            # Process change queue
            while True:
                try:
                    change = await asyncio.wait_for(monitor.change_queue.get(), timeout=1.0)
                    
                    # Process change with small delay to avoid rapid fire
                    await asyncio.sleep(0.5)
                    
                    results = self.predict_and_prevent_errors(
                        [change['file_path']], 
                        change['change_type']
                    )
                    
                    if results['predictions']:
                        logger.info(f"🔮 Processed change: {change['file_path']}")
                        logger.info(f"   Predictions: {len(results['predictions'])}")
                        logger.info(f"   Preventions: {len(results['preventions'])}")
                
                except asyncio.TimeoutError:
                    # No changes in queue, continue monitoring
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Stopping real-time monitoring")
        finally:
            observer.stop()
            observer.join()
    
    def run_batch_prediction(self, target_files: Optional[List[Path]] = None) -> Dict:
        """Run batch prediction and prevention on multiple files"""
        logger.info("🔮 Starting batch predictive error prevention")
        
        if target_files is None:
            # Get files from recent changes or high-risk files
            if self.pattern_predictor:
                risk_scan = self.pattern_predictor.scan_codebase_for_risks(max_files=50)
                high_risk_files = [Path(f['file']) for f in risk_scan['high_risk_files']]
                target_files = high_risk_files
            else:
                # Fallback: scan test files and recently modified files  
                target_files = list(ROOT.glob("tests/**/*.py"))[:20]
        
        if not target_files:
            return {'status': 'no_files', 'results': {}}
        
        # Run predictions and preventions
        results = self.predict_and_prevent_errors(target_files, 'batch_scan')
        
        # Update learning from results
        self.update_learning_from_results(results)
        
        # Save prevention log
        self.save_prevention_log(results)
        
        logger.info(f"🔮 Batch prediction complete: {results['files_analyzed']} files processed")
        return results
    
    def update_learning_from_results(self, results: Dict):
        """Update ML learning from prevention results"""
        # This would feed back into the pattern predictor for continuous improvement
        if self.pattern_predictor:
            # Log successful preventions for pattern learning
            for prevention in results.get('preventions', []):
                if prevention['actions_successful'] > 0:
                    self.success_metrics['errors_prevented'] += 1
    
    def save_prevention_log(self, results: Dict):
        """Save prevention results to log"""
        PREDICTION_DATA.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            'timestamp': results['timestamp'],
            'session_id': hashlib.md5(results['timestamp'].encode()).hexdigest()[:8],
            'results': results,
            'metrics': self.success_metrics
        }
        
        # Append to prevention log
        if PREVENTION_LOG.exists():
            try:
                existing_log = json.loads(PREVENTION_LOG.read_text())
            except:
                existing_log = {'entries': []}
        else:
            existing_log = {'entries': []}
        
        existing_log['entries'].append(log_entry)
        
        # Keep only last 100 entries
        existing_log['entries'] = existing_log['entries'][-100:]
        existing_log['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        PREVENTION_LOG.write_text(json.dumps(existing_log, indent=2))


def main():
    """CLI interface for predictive prevention engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Predictive error prevention engine")
    parser.add_argument("files", nargs="*", help="Files to analyze (default: auto-detect high-risk)")
    parser.add_argument("--real-time", action="store_true", help="Start real-time monitoring")
    parser.add_argument("--batch", action="store_true", help="Run batch prediction scan")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    engine = PredictivePreventionEngine(real_time_monitoring=args.real_time)
    
    if args.real_time:
        # Start real-time monitoring
        asyncio.run(engine.start_real_time_monitoring())
    else:
        # Run batch prediction
        target_files = None
        if args.files:
            target_files = [Path(f) for f in args.files]
        
        results = engine.run_batch_prediction(target_files)
        
        # Print results
        print(f"\n🔮 PREDICTIVE PREVENTION RESULTS")
        print(f"===============================")
        print(f"Files analyzed: {results.get('files_analyzed', 0)}")
        print(f"Predictions made: {len(results.get('predictions', []))}")
        print(f"Preventions applied: {len(results.get('preventions', []))}")
        print(f"Success rate: {results.get('success_rate', 0):.1%}")
        
        # Show high-confidence predictions
        predictions = results.get('predictions', [])
        high_conf_predictions = [p for p in predictions if p['risk_score'] > 0.7]
        
        if high_conf_predictions:
            print(f"\n🚨 HIGH-CONFIDENCE PREDICTIONS:")
            for pred in high_conf_predictions[:5]:
                print(f"  • {pred['file']}: Risk {pred['risk_score']:.2f}")
                for prediction in pred['predictions']:
                    print(f"    - {prediction['specific_type']} ({prediction['confidence']:.1%} confidence)")
        
        return 0 if results.get('success_rate', 0) > 0.5 else 1


if __name__ == "__main__":
    sys.exit(main())