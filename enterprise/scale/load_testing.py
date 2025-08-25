"""
T4 Enterprise Load Testing Framework
Sam Altman (Scale) Standards Implementation

Tests system performance at enterprise scale (10,000+ concurrent users)
Validates <50ms p95 latency requirements across global regions
"""

import asyncio
import aiohttp
import time
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import ssl
import certifi

logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Load test configuration for T4 enterprise testing"""
    target_url: str
    concurrent_users: int = 10000  # T4 target capacity
    test_duration_minutes: int = 15
    ramp_up_minutes: int = 5
    api_endpoints: List[str] = None
    regions: List[str] = None
    auth_token: Optional[str] = None
    expected_latency_p95_ms: float = 50.0  # Sam Altman standard
    expected_latency_p99_ms: float = 100.0
    expected_error_rate_percent: float = 0.01  # <0.01% error rate

@dataclass 
class LoadTestResult:
    """Individual load test result"""
    timestamp: datetime
    endpoint: str
    region: str
    response_time_ms: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class LoadTestReport:
    """Comprehensive load test report for T4 enterprise"""
    test_start_time: datetime
    test_end_time: datetime
    config: LoadTestConfig
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate_percent: float
    
    # Latency metrics (Sam Altman scale requirements)
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_max_ms: float
    latency_min_ms: float
    average_latency_ms: float
    
    # Throughput metrics
    requests_per_second: float
    concurrent_users_achieved: int
    
    # SLA compliance
    sla_latency_p95_compliant: bool  # <50ms target
    sla_latency_p99_compliant: bool  # <100ms target
    sla_error_rate_compliant: bool   # <0.01% target
    overall_sla_compliant: bool
    
    # Regional performance
    regional_performance: Dict[str, Dict[str, float]]
    
    # Enterprise assessment
    enterprise_readiness_score: float  # 0-100
    sam_altman_scale_grade: str  # A, B, C, D, F

class T4EnterpriseLoadTester:
    """
    T4 Enterprise Premium Load Testing Framework
    Implements Sam Altman (Scale) standards for enterprise deployment
    """
    
    def __init__(self, config: LoadTestConfig):
        """
        Initialize T4 enterprise load tester
        
        Args:
            config: LoadTestConfig with test parameters
        """
        self.config = config
        self.results: List[LoadTestResult] = []
        
        # Default API endpoints for LUKHAS AI testing
        if not self.config.api_endpoints:
            self.config.api_endpoints = [
                "/api/v1/health",
                "/api/v1/consciousness/status",
                "/api/v1/identity/auth",
                "/api/v1/governance/safety_check",
                "/api/v1/matriz/process",
                "/api/v1/trinity/framework"
            ]
            
        # Default regions for global scale testing
        if not self.config.regions:
            self.config.regions = [
                "us-east-1",    # US East (Virginia)
                "us-west-2",    # US West (Oregon)  
                "eu-west-1",    # EU (Ireland)
                "eu-central-1", # EU (Frankfurt)
                "ap-south-1",   # Asia Pacific (Mumbai)
                "ap-southeast-1" # Asia Pacific (Singapore)
            ]
        
        # SSL context for HTTPS requests
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        logger.info(f"T4 Enterprise Load Tester initialized: {config.concurrent_users} users, {config.test_duration_minutes}min")

    async def run_load_test(self) -> LoadTestReport:
        """
        Execute T4 enterprise load test
        
        Returns:
            LoadTestReport with comprehensive results
        """
        logger.info("🚀 Starting T4 Enterprise Load Test (Sam Altman Scale Standards)")
        start_time = datetime.now()
        
        try:
            # Phase 1: Warm-up phase
            await self._warmup_phase()
            
            # Phase 2: Ramp-up phase
            await self._ramp_up_phase()
            
            # Phase 3: Sustained load phase
            await self._sustained_load_phase()
            
            # Phase 4: Peak load test
            await self._peak_load_phase()
            
            end_time = datetime.now()
            
            # Generate comprehensive report
            report = self._generate_report(start_time, end_time)
            
            logger.info(f"✅ T4 Load Test Completed: {report.enterprise_readiness_score:.1f}% Enterprise Ready")
            return report
            
        except Exception as e:
            logger.error(f"❌ T4 Load Test Failed: {e}")
            # Return partial report with error information
            return self._generate_error_report(start_time, datetime.now(), str(e))

    async def _warmup_phase(self):
        """Warm-up phase: Light load to initialize system"""
        logger.info("Phase 1: System warm-up (100 users)")
        
        await self._execute_concurrent_requests(
            concurrent_users=100,
            duration_minutes=2,
            phase="warmup"
        )

    async def _ramp_up_phase(self):
        """Ramp-up phase: Gradually increase load"""
        logger.info(f"Phase 2: Ramp-up ({self.config.ramp_up_minutes} minutes)")
        
        ramp_steps = 5
        step_duration = self.config.ramp_up_minutes / ramp_steps
        
        for step in range(1, ramp_steps + 1):
            users = int((step / ramp_steps) * self.config.concurrent_users)
            logger.info(f"Ramp-up step {step}: {users} users")
            
            await self._execute_concurrent_requests(
                concurrent_users=users,
                duration_minutes=step_duration,
                phase=f"ramp_up_step_{step}"
            )

    async def _sustained_load_phase(self):
        """Sustained load phase: Full enterprise load"""
        logger.info(f"Phase 3: Sustained load ({self.config.concurrent_users} users)")
        
        await self._execute_concurrent_requests(
            concurrent_users=self.config.concurrent_users,
            duration_minutes=self.config.test_duration_minutes,
            phase="sustained_load"
        )

    async def _peak_load_phase(self):
        """Peak load phase: 150% of target to test limits"""
        peak_users = int(self.config.concurrent_users * 1.5)
        logger.info(f"Phase 4: Peak load test ({peak_users} users)")
        
        await self._execute_concurrent_requests(
            concurrent_users=peak_users,
            duration_minutes=3,
            phase="peak_load"
        )

    async def _execute_concurrent_requests(self, concurrent_users: int, duration_minutes: float, phase: str):
        """
        Execute concurrent requests for specified duration
        
        Args:
            concurrent_users: Number of concurrent users to simulate
            duration_minutes: Duration to maintain the load
            phase: Test phase name for tracking
        """
        end_time = time.time() + (duration_minutes * 60)
        
        # Create connector with connection pooling for enterprise scale
        connector = aiohttp.TCPConnector(
            limit=concurrent_users * 2,  # Connection pool
            limit_per_host=concurrent_users,
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=self.ssl_context
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_default_headers()
        ) as session:
            
            # Generate user tasks
            tasks = []
            for user_id in range(concurrent_users):
                task = asyncio.create_task(
                    self._user_simulation(session, f"user_{phase}_{user_id}", end_time)
                )
                tasks.append(task)
            
            # Wait for all user simulations to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log phase completion
            successful_users = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"Phase '{phase}' completed: {successful_users}/{concurrent_users} users successful")

    async def _user_simulation(self, session: aiohttp.ClientSession, user_id: str, end_time: float):
        """
        Simulate individual user behavior
        
        Args:
            session: aiohttp session
            user_id: Unique user identifier
            end_time: When to stop the simulation
        """
        request_count = 0
        
        while time.time() < end_time:
            try:
                # Select random endpoint and region
                endpoint = random.choice(self.config.api_endpoints)
                region = random.choice(self.config.regions)
                
                # Execute request
                result = await self._execute_request(session, endpoint, region, user_id)
                self.results.append(result)
                
                request_count += 1
                
                # Simulate realistic user behavior with random delays
                await asyncio.sleep(random.uniform(0.1, 2.0))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"User {user_id} request failed: {e}")
                # Continue with next request
                continue
        
        logger.debug(f"User {user_id} completed {request_count} requests")

    async def _execute_request(self, session: aiohttp.ClientSession, endpoint: str, region: str, user_id: str) -> LoadTestResult:
        """
        Execute single API request and measure performance
        
        Args:
            session: aiohttp session
            endpoint: API endpoint to test
            region: Target region
            user_id: User identifier
            
        Returns:
            LoadTestResult with timing and status information
        """
        start_time = time.time()
        timestamp = datetime.now()
        
        # Construct URL (with region-specific routing if supported)
        url = f"{self.config.target_url}{endpoint}"
        
        headers = {}
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        
        # Add region header for region-aware load balancing
        headers["X-Target-Region"] = region
        headers["X-Load-Test-User"] = user_id
        
        try:
            async with session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Read response to ensure full request completion
                await response.read()
                
                success = 200 <= response.status < 400
                error_message = None if success else f"HTTP {response.status}"
                
                return LoadTestResult(
                    timestamp=timestamp,
                    endpoint=endpoint,
                    region=region,
                    response_time_ms=response_time,
                    status_code=response.status,
                    success=success,
                    error_message=error_message,
                    user_id=user_id
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return LoadTestResult(
                timestamp=timestamp,
                endpoint=endpoint,
                region=region,
                response_time_ms=response_time,
                status_code=0,
                success=False,
                error_message="Request timeout",
                user_id=user_id
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return LoadTestResult(
                timestamp=timestamp,
                endpoint=endpoint, 
                region=region,
                response_time_ms=response_time,
                status_code=0,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        return {
            "User-Agent": "LUKHAS-AI-T4-LoadTester/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Test-Type": "T4-Enterprise-Load-Test",
            "X-Expected-Latency": str(self.config.expected_latency_p95_ms)
        }

    def _generate_report(self, start_time: datetime, end_time: datetime) -> LoadTestReport:
        """
        Generate comprehensive T4 enterprise load test report
        
        Args:
            start_time: Test start time
            end_time: Test end time
            
        Returns:
            LoadTestReport with detailed metrics
        """
        if not self.results:
            logger.warning("No results available for report generation")
            return self._generate_empty_report(start_time, end_time)
        
        # Calculate basic metrics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        error_rate_percent = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # Calculate latency metrics
        response_times = [r.response_time_ms for r in self.results if r.success]
        
        if response_times:
            latency_p50 = statistics.median(response_times)
            latency_p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            latency_p99 = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            latency_max = max(response_times)
            latency_min = min(response_times)
            latency_avg = statistics.mean(response_times)
        else:
            latency_p50 = latency_p95 = latency_p99 = 0.0
            latency_max = latency_min = latency_avg = 0.0
        
        # Calculate throughput
        duration_seconds = (end_time - start_time).total_seconds()
        requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
        
        # SLA compliance checks (Sam Altman scale standards)
        sla_latency_p95_compliant = latency_p95 <= self.config.expected_latency_p95_ms
        sla_latency_p99_compliant = latency_p99 <= self.config.expected_latency_p99_ms
        sla_error_rate_compliant = error_rate_percent <= self.config.expected_error_rate_percent
        overall_sla_compliant = all([sla_latency_p95_compliant, sla_latency_p99_compliant, sla_error_rate_compliant])
        
        # Regional performance analysis
        regional_performance = self._analyze_regional_performance()
        
        # Enterprise readiness score (0-100)
        enterprise_score = self._calculate_enterprise_readiness_score(
            latency_p95, error_rate_percent, requests_per_second
        )
        
        # Sam Altman scale grade
        scale_grade = self._calculate_scale_grade(enterprise_score)
        
        report = LoadTestReport(
            test_start_time=start_time,
            test_end_time=end_time,
            config=self.config,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            error_rate_percent=error_rate_percent,
            latency_p50_ms=latency_p50,
            latency_p95_ms=latency_p95,
            latency_p99_ms=latency_p99,
            latency_max_ms=latency_max,
            latency_min_ms=latency_min,
            average_latency_ms=latency_avg,
            requests_per_second=requests_per_second,
            concurrent_users_achieved=self.config.concurrent_users,
            sla_latency_p95_compliant=sla_latency_p95_compliant,
            sla_latency_p99_compliant=sla_latency_p99_compliant,
            sla_error_rate_compliant=sla_error_rate_compliant,
            overall_sla_compliant=overall_sla_compliant,
            regional_performance=regional_performance,
            enterprise_readiness_score=enterprise_score,
            sam_altman_scale_grade=scale_grade
        )
        
        return report

    def _analyze_regional_performance(self) -> Dict[str, Dict[str, float]]:
        """Analyze performance by region"""
        regional_data = {}
        
        for region in self.config.regions:
            region_results = [r for r in self.results if r.region == region and r.success]
            
            if region_results:
                response_times = [r.response_time_ms for r in region_results]
                regional_data[region] = {
                    "avg_latency_ms": statistics.mean(response_times),
                    "p95_latency_ms": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
                    "success_rate": len(region_results) / len([r for r in self.results if r.region == region]) * 100,
                    "request_count": len(region_results)
                }
            else:
                regional_data[region] = {
                    "avg_latency_ms": 0.0,
                    "p95_latency_ms": 0.0, 
                    "success_rate": 0.0,
                    "request_count": 0
                }
        
        return regional_data

    def _calculate_enterprise_readiness_score(self, latency_p95: float, error_rate: float, rps: float) -> float:
        """
        Calculate enterprise readiness score based on Sam Altman scale standards
        
        Args:
            latency_p95: 95th percentile latency
            error_rate: Error rate percentage
            rps: Requests per second
            
        Returns:
            Enterprise readiness score (0-100)
        """
        score = 100.0
        
        # Latency penalty (Sam Altman: <50ms is critical)
        if latency_p95 > 50:
            penalty = min(50, (latency_p95 - 50) / 50 * 50)  # Max 50 point penalty
            score -= penalty
        
        # Error rate penalty
        if error_rate > 0.01:
            penalty = min(30, error_rate * 10)  # Max 30 point penalty  
            score -= penalty
        
        # Throughput bonus/penalty
        expected_rps = self.config.concurrent_users * 0.1  # Expected throughput
        if rps < expected_rps * 0.5:
            score -= 20  # Significant throughput penalty
        elif rps > expected_rps * 1.5:
            score = min(100, score + 10)  # Throughput bonus
        
        return max(0.0, score)

    def _calculate_scale_grade(self, enterprise_score: float) -> str:
        """Calculate Sam Altman scale grade"""
        if enterprise_score >= 95:
            return "A+"  # Exceeds enterprise standards
        elif enterprise_score >= 90:
            return "A"   # Meets enterprise standards
        elif enterprise_score >= 80:
            return "B"   # Good, needs minor improvements
        elif enterprise_score >= 70:
            return "C"   # Acceptable, needs improvements
        elif enterprise_score >= 60:
            return "D"   # Below enterprise standards
        else:
            return "F"   # Fails enterprise standards

    def _generate_empty_report(self, start_time: datetime, end_time: datetime) -> LoadTestReport:
        """Generate empty report when no results available"""
        return LoadTestReport(
            test_start_time=start_time,
            test_end_time=end_time,
            config=self.config,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            error_rate_percent=100.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
            latency_max_ms=0.0,
            latency_min_ms=0.0,
            average_latency_ms=0.0,
            requests_per_second=0.0,
            concurrent_users_achieved=0,
            sla_latency_p95_compliant=False,
            sla_latency_p99_compliant=False,
            sla_error_rate_compliant=False,
            overall_sla_compliant=False,
            regional_performance={},
            enterprise_readiness_score=0.0,
            sam_altman_scale_grade="F"
        )

    def _generate_error_report(self, start_time: datetime, end_time: datetime, error: str) -> LoadTestReport:
        """Generate error report when test fails"""
        logger.error(f"Generating error report: {error}")
        report = self._generate_empty_report(start_time, end_time)
        # Could add error details to report if needed
        return report

    def export_results(self, filename: str = None) -> str:
        """
        Export load test results to JSON file
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Filename of exported results
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"t4_load_test_results_{timestamp}.json"
        
        try:
            export_data = {
                "test_metadata": {
                    "test_type": "T4_Enterprise_Load_Test",
                    "framework_version": "1.0.0",
                    "sam_altman_standards": True,
                    "export_timestamp": datetime.now().isoformat()
                },
                "configuration": asdict(self.config),
                "results": [asdict(result) for result in self.results]
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Load test results exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return ""


# CLI interface for running T4 load tests
async def run_t4_load_test_cli():
    """CLI interface for T4 enterprise load testing"""
    
    # Default configuration for T4 enterprise testing
    config = LoadTestConfig(
        target_url="http://localhost:8000",  # Update with actual LUKHAS AI endpoint
        concurrent_users=1000,  # Start with 1000 for testing, scale to 10000 for full test
        test_duration_minutes=10,
        ramp_up_minutes=3,
        expected_latency_p95_ms=50.0,  # Sam Altman standard
        expected_latency_p99_ms=100.0,
        expected_error_rate_percent=0.01
    )
    
    print("🚀 T4 Enterprise Load Testing Framework")
    print("   Sam Altman (Scale) Standards Implementation")
    print(f"   Target: {config.concurrent_users} concurrent users")
    print(f"   SLA: <{config.expected_latency_p95_ms}ms p95 latency")
    print("")
    
    # Initialize and run load test
    load_tester = T4EnterpriseLoadTester(config)
    report = await load_tester.run_load_test()
    
    # Display results
    print("📊 T4 Enterprise Load Test Results")
    print("=" * 50)
    print(f"Total Requests: {report.total_requests:,}")
    print(f"Successful: {report.successful_requests:,} ({(report.successful_requests/report.total_requests*100):.1f}%)")
    print(f"Failed: {report.failed_requests:,} ({report.error_rate_percent:.2f}%)")
    print("")
    print("⚡ Latency Metrics")
    print(f"P50: {report.latency_p50_ms:.1f}ms")
    print(f"P95: {report.latency_p95_ms:.1f}ms {'✅' if report.sla_latency_p95_compliant else '❌'}")
    print(f"P99: {report.latency_p99_ms:.1f}ms {'✅' if report.sla_latency_p99_compliant else '❌'}")
    print("")
    print("🎯 SLA Compliance")
    print(f"Overall: {'✅ COMPLIANT' if report.overall_sla_compliant else '❌ VIOLATION'}")
    print("")
    print("🏆 Enterprise Assessment")
    print(f"Readiness Score: {report.enterprise_readiness_score:.1f}%")
    print(f"Sam Altman Scale Grade: {report.sam_altman_scale_grade}")
    
    # Export detailed results
    filename = load_tester.export_results()
    print(f"\n📄 Detailed results exported to: {filename}")


if __name__ == "__main__":
    # Run T4 enterprise load test
    asyncio.run(run_t4_load_test_cli())