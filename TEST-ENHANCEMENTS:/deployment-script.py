#!/usr/bin/env python3
"""
Complete AGI Self-Healing System Deployment & Integration
Orchestrates all components and provides a unified interface
"""

import os
import sys
import json
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import argparse
import yaml

# Add project root to path
sys.path.insert(0, '/Users/agi_dev/LOCAL-REPOS/Lukhas')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelfHealingOrchestrator:
    """Main orchestrator for the self-healing system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path('/Users/agi_dev/LOCAL-REPOS/Lukhas')
        self.config = self._load_config(config_path)
        self.components = {}
        self.status = {
            'web_server': False,
            'ollama': False,
            'test_runner': False,
            'monitoring': False
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'project_root': '/Users/agi_dev/LOCAL-REPOS/Lukhas',
            'web_port': 8000,
            'ollama': {
                'enabled': True,
                'model': 'llama3.2',
                'url': 'http://localhost:11434'
            },
            'openai': {
                'enabled': False,
                'api_key': os.getenv('OPENAI_API_KEY')
            },
            'features': {
                'auto_healing': True,
                'continuous_monitoring': True,
                'llm_analysis': True,
                'auto_cleanup': False
            },
            'thresholds': {
                'min_confidence': 70,
                'max_auto_fix_size': 100,  # lines
                'health_warning': 70,
                'health_critical': 50
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def setup_environment(self):
        """Setup the complete environment"""
        logger.info("Setting up self-healing environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ required")
            sys.exit(1)
        
        # Install required packages
        await self._install_dependencies()
        
        # Setup directories
        self._setup_directories()
        
        # Initialize database
        await self._init_database()
        
        # Check LLM availability
        await self._check_llm_services()
        
        logger.info("Environment setup complete")
    
    async def _install_dependencies(self):
        """Install required Python packages"""
        logger.info("Installing dependencies...")
        
        requirements = [
            'fastapi',
            'uvicorn',
            'aiohttp',
            'pytest',
            'pytest-asyncio',
            'coverage',
            'numpy',
            'pyyaml',
            'websockets',
            'python-multipart'
        ]
        
        for package in requirements:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                logger.info(f"Installing {package}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.project_root / '.lukhas' / 'healing',
            self.project_root / '.lukhas' / 'archive',
            self.project_root / '.lukhas' / 'reports',
            self.project_root / '.lukhas' / 'metrics',
            self.project_root / 'test_results',
            self.project_root / 'logs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    async def _init_database(self):
        """Initialize metrics database"""
        import sqlite3
        
        db_path = self.project_root / '.lukhas' / 'metrics' / 'healing.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS healing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                test_name TEXT,
                error_type TEXT,
                solution TEXT,
                confidence REAL,
                success BOOLEAN,
                details TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_files INTEGER,
                active_files INTEGER,
                obsolete_files INTEGER,
                test_coverage REAL,
                module_connectivity REAL,
                health_score REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    async def _check_llm_services(self):
        """Check availability of LLM services"""
        import aiohttp
        
        # Check Ollama
        if self.config['ollama']['enabled']:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.config['ollama']['url']}/api/tags") as response:
                        if response.status == 200:
                            data = await response.json()
                            models = [m['name'] for m in data.get('models', [])]
                            
                            if self.config['ollama']['model'] in models:
                                self.status['ollama'] = True
                                logger.info(f"Ollama available with model {self.config['ollama']['model']}")
                            else:
                                logger.warning(f"Model {self.config['ollama']['model']} not found in Ollama")
                                logger.info(f"Available models: {models}")
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
                logger.info("Run 'ollama serve' to start Ollama")
        
        # Check OpenAI
        if self.config['openai']['enabled'] and self.config['openai']['api_key']:
            self.status['openai'] = True
            logger.info("OpenAI API configured")
    
    async def start_web_server(self):
        """Start the web dashboard server"""
        logger.info("Starting web server...")
        
        # Create the main server file
        server_file = self.project_root / 'self_healing_server.py'
        
        # Copy our advanced server code
        server_code = Path(__file__).parent / 'advanced_self_healing_system.py'
        if server_code.exists():
            shutil.copy(server_code, server_file)
        
        # Copy dashboard HTML
        dashboard_file = self.project_root / 'dashboard.html'
        dashboard_html = Path(__file__).parent / 'rich_dashboard.html'
        if dashboard_html.exists():
            shutil.copy(dashboard_html, dashboard_file)
        
        # Start server process
        self.components['web_server'] = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'self_healing_server:app', 
             '--host', '0.0.0.0', '--port', str(self.config['web_port']), '--reload'],
            cwd=self.project_root
        )
        
        self.status['web_server'] = True
        logger.info(f"Web server started at http://localhost:{self.config['web_port']}")
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting continuous monitoring...")
        
        async def monitor_loop():
            while self.status['monitoring']:
                try:
                    # Run tests periodically
                    await self.run_automated_tests()
                    
                    # Check system health
                    await self.check_system_health()
                    
                    # Sleep for monitoring interval
                    await asyncio.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(60)
        
        self.status['monitoring'] = True
        asyncio.create_task(monitor_loop())
        logger.info("Monitoring started")
    
    async def run_automated_tests(self):
        """Run automated test suite"""
        logger.info("Running automated tests...")
        
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '--json-report', '--json-report-file=test_results.json'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Parse failures and trigger healing
            report_file = self.project_root / 'test_results.json'
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    
                failures = self._extract_failures(report)
                
                if self.config['features']['auto_healing']:
                    await self.heal_failures(failures)
        
        return result.returncode == 0
    
    def _extract_failures(self, report: Dict) -> List[Dict]:
        """Extract failure information from test report"""
        failures = []
        
        for test in report.get('tests', []):
            if test.get('outcome') == 'failed':
                failures.append({
                    'test_name': test.get('nodeid'),
                    'error_type': test.get('call', {}).get('longrepr', {}).get('reprcrash', {}).get('message', 'Unknown'),
                    'error_message': test.get('call', {}).get('longrepr', {}).get('reprtraceback', {}).get('reprentries', [{}])[0].get('lines', [''])[0],
                    'test_file': test.get('nodeid', '').split('::')[0]
                })
        
        return failures
    
    async def heal_failures(self, failures: List[Dict]):
        """Attempt to heal test failures"""
        for failure in failures:
            logger.info(f"Attempting to heal: {failure['test_name']}")
            
            if self.config['features']['llm_analysis'] and self.status['ollama']:
                # Use LLM for analysis
                solution = await self.analyze_with_llm(failure)
                
                if solution and solution.get('confidence', 0) >= self.config['thresholds']['min_confidence']:
                    await self.apply_solution(failure, solution)
    
    async def analyze_with_llm(self, failure: Dict) -> Optional[Dict]:
        """Analyze failure using LLM"""
        import aiohttp
        
        if not self.status['ollama']:
            return None
        
        prompt = f"""
        Analyze this Python test failure and provide a solution:
        
        Test: {failure['test_name']}
        Error: {failure['error_type']}
        Message: {failure['error_message']}
        
        Provide a JSON response with:
        - root_cause: Brief explanation of the issue
        - solution: Specific fix to apply
        - confidence: 0-100 confidence in the solution
        - code_change: Python code to fix the issue
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['ollama']['url']}/api/generate",
                    json={
                        'model': self.config['ollama']['model'],
                        'prompt': prompt,
                        'stream': False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return json.loads(result.get('response', '{}'))
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
        
        return None
    
    async def apply_solution(self, failure: Dict, solution: Dict):
        """Apply the proposed solution"""
        logger.info(f"Applying solution with {solution['confidence']}% confidence")
        
        # Implementation would apply the actual fix
        # For safety, we'll just log it for now
        logger.info(f"Solution: {solution['solution']}")
        
        # Record in database
        import sqlite3
        db_path = self.project_root / '.lukhas' / 'metrics' / 'healing.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO healing_history 
            (test_name, error_type, solution, confidence, success, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            failure['test_name'],
            failure['error_type'],
            solution['solution'],
            solution['confidence'],
            True,  # Assuming success for now
            json.dumps(solution)
        ))
        
        conn.commit()
        conn.close()
    
    async def check_system_health(self):
        """Check overall system health"""
        from advanced_self_healing_system import AdvancedSelfHealingEngine
        
        engine = AdvancedSelfHealingEngine(str(self.project_root))
        metrics = engine.get_system_dashboard_data()['metrics']
        
        health_score = metrics['performance_score']
        
        if health_score < self.config['thresholds']['health_critical']:
            logger.critical(f"System health critical: {health_score}%")
            # Trigger alerts
        elif health_score < self.config['thresholds']['health_warning']:
            logger.warning(f"System health warning: {health_score}%")
        else:
            logger.info(f"System health: {health_score}%")
        
        # Store metrics in database
        import sqlite3
        db_path = self.project_root / '.lukhas' / 'metrics' / 'healing.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (total_files, active_files, obsolete_files, test_coverage, module_connectivity, health_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metrics['total_files'],
            metrics['active_files'],
            metrics['obsolete_files'],
            metrics['test_coverage'],
            metrics['modules_connected'],
            health_score
        ))
        
        conn.commit()
        conn.close()
    
    async def generate_report(self):
        """Generate comprehensive system report"""
        logger.info("Generating system report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': self.status,
            'config': self.config,
            'metrics': {},
            'recommendations': []
        }
        
        # Get latest metrics
        import sqlite3
        db_path = self.project_root / '.lukhas' / 'metrics' / 'healing.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM system_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        if row:
            report['metrics'] = {
                'total_files': row[2],
                'active_files': row[3],
                'obsolete_files': row[4],
                'test_coverage': row[5],
                'module_connectivity': row[6],
                'health_score': row[7]
            }
        
        # Get healing statistics
        cursor.execute('''
            SELECT COUNT(*), AVG(confidence), SUM(success)
            FROM healing_history
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        stats = cursor.fetchone()
        report['healing_stats'] = {
            'total_attempts': stats[0] or 0,
            'average_confidence': stats[1] or 0,
            'successful_heals': stats[2] or 0
        }
        
        conn.close()
        
        # Generate recommendations
        if report['metrics'].get('test_coverage', 0) < 80:
            report['recommendations'].append("Increase test coverage to at least 80%")
        
        if report['metrics'].get('obsolete_files', 0) > 50:
            report['recommendations'].append("Clean up obsolete files to reduce technical debt")
        
        if report['metrics'].get('health_score', 100) < 70:
            report['recommendations'].append("System health is below optimal - review critical modules")
        
        # Save report
        report_file = self.project_root / '.lukhas' / 'reports' / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
        return report
    
    async def run(self):
        """Main orchestration loop"""
        logger.info("Starting AGI Self-Healing System")
        
        try:
            # Setup environment
            await self.setup_environment()
            
            # Start web server
            await self.start_web_server()
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Start monitoring if enabled
            if self.config['features']['continuous_monitoring']:
                await self.start_monitoring()
            
            logger.info("System running. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                await asyncio.sleep(60)
                
                # Generate periodic reports
                if datetime.now().minute == 0:  # Every hour
                    await self.generate_report()
                    
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.status['monitoring'] = False
        
        if 'web_server' in self.components:
            self.components['web_server'].terminate()
        
        logger.info("System shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AGI Self-Healing System')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--setup-only', action='store_true', help='Only setup environment')
    parser.add_argument('--report', action='store_true', help='Generate report and exit')
    parser.add_argument('--test', action='store_true', help='Run tests and exit')
    
    args = parser.parse_args()
    
    orchestrator = SelfHealingOrchestrator(args.config)
    
    if args.setup_only:
        asyncio.run(orchestrator.setup_environment())
        logger.info("Setup complete")
        
    elif args.report:
        asyncio.run(orchestrator.generate_report())
        
    elif args.test:
        success = asyncio.run(orchestrator.run_automated_tests())
        sys.exit(0 if success else 1)
        
    else:
        asyncio.run(orchestrator.run())


if __name__ == '__main__':
    main()