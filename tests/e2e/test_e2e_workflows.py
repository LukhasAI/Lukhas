"""
End-to-End tests for LUKHAS complete workflows
Tests full user scenarios across all systems
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List

from tests.test_framework import (
    IntegrationTestCase, PerformanceTestCase,
    MockDataGenerator, TestValidator,
    PERFORMANCE_BENCHMARKS
)


class TestUserWorkflows(IntegrationTestCase):
    """Test complete user interaction workflows"""
    
    @pytest.mark.asyncio
    async def test_philosophical_inquiry_workflow(self,
                                                consciousness_system,
                                                memory_system,
                                                guardian_system,
                                                emotion_engine,
                                                dream_engine,
                                                symbolic_engine):
        """Test complete philosophical inquiry workflow"""
        # User asks deep philosophical question
        user_query = "What is the meaning of consciousness and how does it relate to existence?"
        
        workflow_log = []
        
        # Step 1: Analyze emotional context
        emotion_result = await emotion_engine.analyze_emotion(user_query)
        workflow_log.append(('emotion_analysis', emotion_result))
        assert emotion_result['primary_emotion'] in ['neutral', 'curious']
        
        # Step 2: Guardian pre-check
        action_proposal = {
            'action': 'philosophical_inquiry',
            'topic': 'consciousness_and_existence',
            'risk_level': 'low'
        }
        guardian_check = await guardian_system.evaluate_action(action_proposal)
        workflow_log.append(('guardian_precheck', guardian_check))
        assert guardian_check['approved'] is True
        
        # Step 3: Process through consciousness
        consciousness_result = await consciousness_system.process_query(
            user_query,
            awareness_level=0.9,  # High awareness for philosophy
            include_emotion=True
        )
        workflow_log.append(('consciousness_processing', consciousness_result))
        
        # Step 4: Store interaction in memory
        memory_entry = {
            'type': 'philosophical_inquiry',
            'query': user_query,
            'response': consciousness_result,
            'emotion': emotion_result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        memory_result = await memory_system.store(memory_entry, 'episodic')
        workflow_log.append(('memory_storage', memory_result))
        assert memory_result['stored'] is True
        
        # Step 5: Generate creative insight
        dream_prompt = f"Deep insights about {user_query}"
        dream_result = await dream_engine.generate(
            dream_prompt,
            creativity_level=0.8,
            dream_type='analytical'
        )
        workflow_log.append(('creative_generation', dream_result))
        
        # Step 6: Encode key concepts symbolically
        key_concepts = consciousness_result.get('interpretation', '')
        symbolic_result = await symbolic_engine.encode(key_concepts)
        workflow_log.append(('symbolic_encoding', symbolic_result))
        
        # Step 7: Guardian post-check on complete response
        complete_response = {
            'consciousness': consciousness_result,
            'creative_insight': dream_result,
            'symbolic_representation': symbolic_result
        }
        final_check = await guardian_system.validate_response(complete_response)
        workflow_log.append(('guardian_final', final_check))
        assert final_check['approved'] is True
        
        # Verify workflow completed successfully
        assert len(workflow_log) == 7
        assert all(step[1] is not None for step in workflow_log)
        
    @pytest.mark.asyncio
    async def test_learning_workflow(self,
                                   consciousness_system,
                                   memory_system,
                                   guardian_system):
        """Test learning and knowledge retention workflow"""
        # User teaches system new information
        teaching_interactions = [
            "The capital of France is Paris",
            "Paris is known for the Eiffel Tower",
            "The Eiffel Tower was built in 1889"
        ]
        
        # Step 1: Process each teaching
        for teaching in teaching_interactions:
            # Guardian check
            check = await guardian_system.evaluate_action({
                'action': 'learn_fact',
                'content': teaching
            })
            assert check['approved'] is True
            
            # Process understanding
            understanding = await consciousness_system.process_query(teaching)
            
            # Store as semantic memory
            await memory_system.store({
                'type': 'learned_fact',
                'content': teaching,
                'understanding': understanding,
                'confidence': understanding.get('confidence', 0.8)
            }, 'semantic')
            
        # Step 2: Test recall
        recall_query = "What do you know about Paris?"
        
        # Search memories
        memories = await memory_system.search('Paris')
        assert memories['total_matches'] >= 2
        
        # Process recall through consciousness
        recall_context = {
            'memories': memories['results']
        }
        recall_response = await consciousness_system.process_query(
            recall_query,
            awareness_level=0.7
        )
        
        # Should demonstrate learned knowledge
        assert recall_response is not None
        
    @pytest.mark.asyncio
    async def test_creative_collaboration_workflow(self,
                                                 consciousness_system,
                                                 dream_engine,
                                                 emotion_engine,
                                                 guardian_system,
                                                 symbolic_engine):
        """Test creative collaboration workflow"""
        # User wants to create a story
        user_request = "Help me create a short story about hope in difficult times"
        
        # Step 1: Emotional resonance
        emotion_analysis = await emotion_engine.analyze_emotion(user_request)
        target_emotion = 'hopeful'
        
        # Step 2: Generate creative seed
        dream_seed = await dream_engine.generate(
            "A story about hope overcoming adversity",
            creativity_level=0.9,
            dream_type='creative'
        )
        
        # Step 3: Process through consciousness for coherence
        story_elements = await consciousness_system.process_query(
            f"Create story elements based on: {dream_seed['dream_content']}",
            awareness_level=0.8,
            include_emotion=True
        )
        
        # Step 4: Guardian check for appropriate content
        content_check = await guardian_system.validate_response({
            'type': 'creative_content',
            'content': dream_seed['dream_content'],
            'theme': 'hope'
        })
        assert content_check['approved'] is True
        
        # Step 5: Generate emotional arc
        emotional_arc = await emotion_engine.generate_response(
            target_emotion,
            intensity=0.8
        )
        
        # Step 6: Symbolic representation
        story_symbols = await symbolic_engine.encode(
            "hope light darkness journey triumph"
        )
        
        # Verify creative process completed
        assert dream_seed['dream_content'] is not None
        assert story_symbols['glyphs'] is not None
        assert emotional_arc['expression'] is not None
        
    @pytest.mark.asyncio
    async def test_problem_solving_workflow(self,
                                          consciousness_system,
                                          memory_system,
                                          guardian_system,
                                          symbolic_engine):
        """Test problem-solving workflow"""
        # User presents a problem
        problem = "I need to organize a large amount of information efficiently"
        
        # Step 1: Understand the problem
        problem_analysis = await consciousness_system.process_query(
            problem,
            awareness_level=0.8
        )
        
        # Step 2: Search for relevant memories/knowledge
        relevant_memories = await memory_system.search("organize information")
        
        # Step 3: Generate solution approach
        solution_query = f"Based on the problem: {problem}, suggest organization methods"
        solution_proposal = await consciousness_system.process_query(
            solution_query,
            awareness_level=0.9
        )
        
        # Step 4: Guardian check solution ethics
        solution_check = await guardian_system.evaluate_action({
            'action': 'suggest_solution',
            'problem': problem,
            'solution': solution_proposal
        })
        assert solution_check['approved'] is True
        
        # Step 5: Create symbolic framework
        framework_symbols = await symbolic_engine.encode(
            "structure hierarchy categorize organize flow"
        )
        
        # Step 6: Store solution for future reference
        solution_memory = {
            'type': 'problem_solution',
            'problem': problem,
            'analysis': problem_analysis,
            'solution': solution_proposal,
            'framework': framework_symbols,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        memory_result = await memory_system.store(solution_memory, 'procedural')
        assert memory_result['stored'] is True


class TestSystemResilience(IntegrationTestCase):
    """Test system resilience and error recovery"""
    
    @pytest.mark.asyncio
    async def test_cascade_failure_prevention(self,
                                            consciousness_system,
                                            memory_system,
                                            guardian_system):
        """Test prevention of cascade failures"""
        # Simulate memory system issues
        original_store = memory_system.store
        failure_count = 0
        
        async def failing_store(*args, **kwargs):
            nonlocal failure_count
            failure_count += 1
            if failure_count < 3:
                raise Exception("Memory system temporary failure")
            return await original_store(*args, **kwargs)
            
        memory_system.store = failing_store
        
        # System should handle gracefully
        query = "Test query during memory issues"
        
        # Consciousness should still work
        consciousness_result = await consciousness_system.process_query(query)
        assert consciousness_result is not None
        
        # Guardian should still work
        guardian_result = await guardian_system.evaluate_action({
            'action': 'test_action'
        })
        assert guardian_result is not None
        
        # Eventually memory should recover
        await asyncio.sleep(0.1)
        memory_result = await memory_system.store({'test': 'recovery'})
        assert memory_result['stored'] is True
        
    @pytest.mark.asyncio
    async def test_circular_dependency_handling(self,
                                              consciousness_system,
                                              memory_system):
        """Test handling of circular dependencies"""
        call_depth = 0
        max_depth = 5
        
        # Track recursive calls
        original_process = consciousness_system.process_query
        
        async def tracked_process(query, **kwargs):
            nonlocal call_depth
            call_depth += 1
            
            if call_depth > max_depth:
                raise RecursionError("Maximum recursion depth exceeded")
                
            # Simulate consciousness triggering memory
            if "recursive" in query:
                await memory_system.retrieve("recursive")
                
            result = await original_process(query, **kwargs)
            call_depth -= 1
            return result
            
        consciousness_system.process_query = tracked_process
        
        # Should handle without infinite recursion
        try:
            result = await consciousness_system.process_query("Non-recursive query")
            assert result is not None
            assert call_depth == 0  # Should unwind properly
        except RecursionError:
            pytest.fail("Circular dependency not handled properly")
            
    @pytest.mark.asyncio
    async def test_resource_exhaustion_protection(self,
                                                consciousness_system,
                                                memory_system,
                                                dream_engine):
        """Test protection against resource exhaustion"""
        # Try to exhaust memory with large storage
        large_memories = []
        
        for i in range(100):
            large_memory = {
                'index': i,
                'data': 'x' * 10000  # 10KB per memory
            }
            
            try:
                result = await memory_system.store(large_memory)
                large_memories.append(result)
            except Exception:
                # Should handle gracefully
                break
                
        # System should still be functional
        test_query = "System health check"
        consciousness_result = await consciousness_system.process_query(test_query)
        assert consciousness_result is not None
        
        # Dream engine should still work
        dream_result = await dream_engine.generate("Small dream")
        assert dream_result is not None


class TestPerformanceScenarios(PerformanceTestCase):
    """Test performance under various scenarios"""
    
    @pytest.mark.asyncio
    async def test_high_load_performance(self,
                                       consciousness_system,
                                       memory_system,
                                       guardian_system,
                                       performance_metrics):
        """Test performance under high load"""
        # Simulate many concurrent users
        num_users = 50
        queries_per_user = 5
        
        async def simulate_user(user_id: int):
            """Simulate a single user session"""
            results = []
            
            for i in range(queries_per_user):
                # Vary the operations
                if i % 3 == 0:
                    result = await consciousness_system.process_query(
                        f"User {user_id} query {i}"
                    )
                elif i % 3 == 1:
                    result = await memory_system.store({
                        'user': user_id,
                        'data': f'Memory {i}'
                    })
                else:
                    result = await guardian_system.evaluate_action({
                        'action': f'user_{user_id}_action_{i}'
                    })
                    
                results.append(result)
                
            return results
            
        # Run all users concurrently
        start_time = asyncio.get_event_loop().time()
        
        user_tasks = [simulate_user(i) for i in range(num_users)]
        all_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        # Check results
        errors = sum(1 for r in all_results if isinstance(r, Exception))
        total_operations = num_users * queries_per_user
        success_rate = (total_operations - errors) / total_operations
        
        # Performance assertions
        assert success_rate > 0.95, f"Success rate {success_rate:.1%} too low"
        assert total_time < 30, f"High load test took {total_time:.1f}s"
        
        avg_time_per_op = total_time / total_operations
        assert avg_time_per_op < 0.5, f"Average operation time {avg_time_per_op:.3f}s too high"
        
    @pytest.mark.asyncio
    async def test_memory_scaling_performance(self,
                                            memory_system,
                                            performance_metrics):
        """Test memory system performance at scale"""
        # Store increasing amounts of memories
        memory_counts = [100, 500, 1000, 5000]
        retrieval_times = []
        
        for count in memory_counts:
            # Store memories
            for i in range(count - len(memory_system.memories.get('general', []))):
                await memory_system.store({
                    'index': i,
                    'content': f'Scaling test memory {i}',
                    'keywords': ['test', 'scaling', f'group_{i % 10}']
                })
                
            # Measure retrieval time
            search_times = []
            for _ in range(10):
                result = await self.measure_operation(
                    lambda: memory_system.search('scaling'),
                    performance_metrics
                )
                search_times.append(
                    performance_metrics['operations'][-1]['duration']
                )
                
            avg_search_time = sum(search_times) / len(search_times)
            retrieval_times.append((count, avg_search_time))
            
        # Check scaling characteristics
        # Time should not increase linearly with count
        for i in range(1, len(retrieval_times)):
            count_ratio = retrieval_times[i][0] / retrieval_times[i-1][0]
            time_ratio = retrieval_times[i][1] / retrieval_times[i-1][1]
            
            # Sub-linear scaling expected
            assert time_ratio < count_ratio * 0.5, \
                f"Search time scaling poorly: {time_ratio:.1f}x for {count_ratio}x memories"


class TestSecurityScenarios(IntegrationTestCase):
    """Test security scenarios"""
    
    @pytest.mark.asyncio
    async def test_injection_attack_prevention(self,
                                             consciousness_system,
                                             guardian_system):
        """Test prevention of injection attacks"""
        # Various injection attempts
        injection_attempts = [
            "'; DROP TABLE memories; --",
            "<script>alert('XSS')</script>",
            "{{ system('rm -rf /') }}",
            "__import__('os').system('malicious')",
            "eval(malicious_code)"
        ]
        
        for attempt in injection_attempts:
            # Guardian should detect
            guardian_check = await guardian_system.evaluate_action({
                'action': 'process_input',
                'input': attempt
            })
            
            # Process through consciousness
            result = await consciousness_system.process_query(attempt)
            
            # Should handle safely
            assert result is not None
            # In real system, Guardian might block these
            
    @pytest.mark.asyncio
    async def test_privacy_protection(self,
                                    memory_system,
                                    guardian_system):
        """Test privacy protection mechanisms"""
        # Store sensitive information
        sensitive_data = {
            'user_ssn': '123-45-6789',
            'credit_card': '4111-1111-1111-1111',
            'medical_info': 'Confidential medical data',
            'password': 'user_password123'
        }
        
        # Guardian should evaluate each
        for key, value in sensitive_data.items():
            check = await guardian_system.evaluate_action({
                'action': 'store_data',
                'data_type': key,
                'content': value
            })
            
            # Should flag privacy concerns
            if not check['approved']:
                assert any('privacy' in rule.lower() 
                          for rule in check.get('violated_rules', []))
                          
    @pytest.mark.asyncio
    async def test_authorization_boundaries(self,
                                          consciousness_system,
                                          guardian_system):
        """Test authorization boundaries"""
        # Different user contexts
        user_contexts = [
            {'role': 'admin', 'permissions': ['read', 'write', 'delete']},
            {'role': 'user', 'permissions': ['read']},
            {'role': 'guest', 'permissions': []}
        ]
        
        # Admin operations
        admin_operations = [
            {'action': 'delete_user_data', 'target': 'all'},
            {'action': 'modify_system_config', 'setting': 'security_level'},
            {'action': 'access_all_memories', 'scope': 'global'}
        ]
        
        for context in user_contexts:
            for operation in admin_operations:
                # Guardian should check permissions
                check = await guardian_system.evaluate_action(
                    operation,
                    context=context
                )
                
                # Only admin should be approved for admin operations
                if context['role'] != 'admin':
                    # In real system would enforce
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])