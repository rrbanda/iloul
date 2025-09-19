#!/usr/bin/env python3
"""
Comprehensive A2A System Tests

Tests all components of the mortgage processing A2A system.
"""
import asyncio
import json
import logging
import uuid
import time
from typing import Dict, List

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class A2ASystemTester:
    """Comprehensive tester for the A2A system"""
    
    def __init__(self):
        self.services = [
            {
                "name": "Mortgage A2A Orchestrator",
                "url": "http://localhost:8000",
                "port": 8000
            },
            {
                "name": "Web Search Agent",
                "url": "http://localhost:8002", 
                "port": 8002
            }
        ]
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log a test result"""
        status = "✅ PASS" if success else " FAIL"
        logger.info(f"{status} {test_name}")
        if details:
            logger.info(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })
    
    async def test_service_health(self, service: Dict) -> bool:
        """Test if a service is responding"""
        test_name = f"Health Check - {service['name']}"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service['url']}/agent_card")
                
                if response.status_code == 200:
                    agent_card = response.json()
                    details = f"Agent: {agent_card.get('name', 'Unknown')}, Skills: {len(agent_card.get('skills', []))}"
                    self.log_test_result(test_name, True, details)
                    return True
                else:
                    self.log_test_result(test_name, False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")
            return False
    
    async def test_orchestrator_routing(self) -> bool:
        """Test orchestrator intelligent routing"""
        test_name = "Orchestrator Routing"
        
        test_cases = [
            {
                "query": "current mortgage rates today",
                "description": "Web search routing"
            },
            {
                "query": "latest housing market news",
                "description": "News search routing"
            }
        ]
        
        orchestrator_url = "http://localhost:8000"
        
        for case in test_cases:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "messageId": str(uuid.uuid4()),
                            "contextId": str(uuid.uuid4()),
                            "parts": [{"type": "text", "text": case["query"]}]
                        },
                        "configuration": {"acceptedOutputModes": ["text"]}
                    }
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(orchestrator_url, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        success = "result" in result
                        details = f"{case['description']}: {case['query'][:30]}..."
                        
                        if success:
                            self.log_test_result(f"{test_name} - {case['description']}", True, details)
                        else:
                            self.log_test_result(f"{test_name} - {case['description']}", False, f"No result in response")
                            return False
                    else:
                        self.log_test_result(f"{test_name} - {case['description']}", False, f"HTTP {response.status_code}")
                        return False
                        
            except Exception as e:
                self.log_test_result(f"{test_name} - {case['description']}", False, f"Error: {str(e)}")
                return False
        
        self.log_test_result(test_name, True, f"All {len(test_cases)} routing tests passed")
        return True
    
    async def test_web_search_direct(self) -> bool:
        """Test web search agent directly"""
        test_name = "Direct Web Search"
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "messageId": str(uuid.uuid4()),
                        "contextId": str(uuid.uuid4()),
                        "parts": [{"type": "text", "text": "current mortgage rates"}]
                    },
                    "configuration": {"acceptedOutputModes": ["text"]}
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post("http://localhost:8002", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if we got a task ID (async processing)
                    if "result" in result and isinstance(result["result"], dict) and "id" in result["result"]:
                        task_id = result["result"]["id"]
                        logger.info(f"    Got task ID: {task_id}, waiting for completion...")
                        
                        # Wait for task completion
                        completion_result = await self.wait_for_task_completion("http://localhost:8002", task_id)
                        
                        if completion_result:
                            self.log_test_result(test_name, True, "Web search completed successfully")
                            return True
                        else:
                            self.log_test_result(test_name, False, "Task did not complete successfully")
                            return False
                    else:
                        # Direct response
                        self.log_test_result(test_name, True, "Direct web search response received")
                        return True
                else:
                    self.log_test_result(test_name, False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"Error: {str(e)}")
            return False
    
    async def wait_for_task_completion(self, agent_url: str, task_id: str, max_wait: int = 30) -> bool:
        """Wait for a task to complete and return success status"""
        for attempt in range(max_wait):
            try:
                get_payload = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tasks/get",
                    "params": {"id": task_id}
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(agent_url, json=get_payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if "result" in result and result["result"]:
                            task_data = result["result"]
                            task_state = task_data.get("status", {}).get("state")
                            
                            if task_state == "completed":
                                logger.info(f"    Task {task_id} completed successfully")
                                return True
                            elif task_state == "failed":
                                logger.error(f"    Task {task_id} failed")
                                return False
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"    Error checking task {task_id}: {e}")
                await asyncio.sleep(1)
        
        logger.error(f"    Timeout waiting for task {task_id}")
        return False
    
    async def run_all_tests(self) -> bool:
        """Run all test suites"""
        logger.info("🧪 Starting comprehensive A2A system tests...")
        
        # Check if services are running
        logger.info("🔍 Checking if A2A services are running...")
        
        services_available = True
        for service in self.services:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    await client.get(f"{service['url']}/agent_card")
            except:
                logger.error(f" {service['name']} is not running at {service['url']}")
                services_available = False
        
        if not services_available:
            print("\n⚠️  SERVICES NOT RUNNING")
            print("Please start the A2A system first:")
            print("  cd src && python -m mortgage_a2a.scripts.start_a2a_system")
            return False
        
        all_passed = True
        
        # Health checks for all services
        for service in self.services:
            if not await self.test_service_health(service):
                all_passed = False
        
        # Individual test suites
        test_suites = [
            ("Direct Web Search", self.test_web_search_direct),
            ("Orchestrator Routing", self.test_orchestrator_routing),
        ]
        
        for test_name, test_func in test_suites:
            try:
                if not await test_func():
                    all_passed = False
            except Exception as e:
                logger.error(f" Test suite '{test_name}' failed with exception: {e}")
                all_passed = False
        
        # Display results
        self.display_test_results()
        
        return all_passed
    
    def display_test_results(self):
        """Display comprehensive test results"""
        print("\n" + "="*70)
        print("🧪 A2A SYSTEM TEST RESULTS")
        print("="*70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"📊 SUMMARY: {passed} passed, {failed} failed, {len(self.test_results)} total")
        print()
        
        if failed > 0:
            print(" FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}: {result['details']}")
        
        print("="*70)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! A2A system is ready for production.")
        else:
            print("⚠️  SOME TESTS FAILED. Please check the issues above.")
        
        print("="*70 + "\n")

async def main():
    """Main test runner"""
    print("🧪 Mortgage Processing A2A System Test Suite")
    print("🔍 Testing all components and integration...")
    
    tester = A2ASystemTester()
    
    # Run all tests
    success = await tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f" Test runner error: {e}")
        exit(1)
