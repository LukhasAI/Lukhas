#!/usr/bin/env python3
import sys

sys.path.append(".")

print("🎨 REAL CREATIVITY FUNCTIONAL TEST")
print("Testing actual creative problem-solving capabilities...")

# Test 1: Creative Problem Solving with Real Scenario
print("\n📋 Test 1: Creative Problem Solving")
try:
    from creativity.creative_engine import CreativeEngine

    engine = CreativeEngine()

    # Real problem scenario
    problem = {
        "type": "resource_optimization",
        "description": "A city needs to reduce traffic congestion during rush hour",
        "constraints": [
            "limited budget",
            "existing infrastructure",
            "public acceptance",
        ],
        "context": {
            "population": 500000,
            "peak_traffic_hours": ["7-9am", "5-7pm"],
            "current_solutions": ["bus lanes", "traffic lights"],
        },
    }

    solutions = engine.generate_creative_solutions(problem, num_solutions=5)

    print(f"✅ Generated {len(solutions)} creative solutions:")
    for i, solution in enumerate(solutions, 1):
        print(f'   Solution {i}: {solution["title"]}')
        print(f'   Innovation Score: {solution["innovation_score"]}/10')
        print(f'   Feasibility: {solution["feasibility"]}/10')

    print("\n📊 Creativity Metrics:")
    print(
        f'   Average Innovation Score: {sum(s["innovation_score"] for s in solutions) / len(solutions):.1f}/10'
    )
    print(
        f'   Solutions Above 7.0 Innovation: {sum(1 for s in solutions if s["innovation_score"] >= 7.0)}'
    )

except Exception as e:
    print(f"❌ Creative Engine not available: {e}")

    # Fallback: Test with available creativity modules
    try:
        import creativity

        print("✅ Creativity module imported successfully")

        # Test if there are any actual creative generation functions
        creativity_funcs = [
            attr for attr in dir(creativity) if not attr.startswith("_")
        ]
        print(f"   Available functions: {creativity_funcs}")

        if hasattr(creativity, "generate"):
            print("🎯 Testing real creative generation...")
            result = creativity.generate("Design an innovative transportation system")
            print(f"   Generated: {result}")
        else:
            print("❌ No creative generation functions found")

    except ImportError:
        print("❌ No creativity modules found for functional testing")

# Test 2: Bio-Symbolic Real Problem Solving
print("\n📋 Test 2: Bio-Symbolic Real Problem Solving")
try:
    from core.bio_symbolic import BioSymbolicProcessor

    processor = BioSymbolicProcessor()

    # Real biological scenarios for symbolic processing
    bio_scenarios = [
        {
            "type": "ecosystem_balance",
            "data": {
                "predators": 50,
                "prey": 500,
                "vegetation": "declining",
                "season": "winter",
                "human_impact": "moderate",
            },
            "question": "Predict ecosystem stability and recommend interventions",
        },
        {
            "type": "genetic_expression",
            "data": {
                "gene_sequence": "ATCGATCGATCG",
                "environment": "high_stress",
                "mutations": ["point_mutation_at_5"],
                "phenotype": "unknown",
            },
            "question": "Predict phenotype expression and evolutionary fitness",
        },
    ]

    for i, scenario in enumerate(bio_scenarios, 1):
        print(f'\n🧬 Bio-Symbolic Scenario {i}: {scenario["type"]}')
        print(f'   Data: {scenario["data"]}')
        print(f'   Challenge: {scenario["question"]}')

        # Test real bio-symbolic reasoning
        result = processor.process_biological_scenario(scenario)
        print(f'   ✅ Analysis: {result["analysis"]}')
        print(f'   🎯 Recommendation: {result["recommendation"]}')
        print(f'   📊 Confidence: {result["confidence"]:.2f}')

except Exception as e:
    print(f"❌ Bio-Symbolic real scenario testing failed: {e}")

# Test 3: Memory System with Real Learning Scenarios
print("\n📋 Test 3: Memory System Real Learning Scenarios")
try:
    from memory import MemoryManager

    memory = MemoryManager()

    # Real learning scenarios
    learning_scenarios = [
        {
            "task": "language_learning",
            "input_data": [
                "hello",
                "world",
                "good",
                "morning",
                "hello",
                "good",
                "world",
            ],
            "expected_pattern": "greeting_patterns",
            "complexity": "basic",
        },
        {
            "task": "pattern_recognition",
            "input_data": [1, 1, 2, 3, 5, 8, 13, 21],
            "expected_pattern": "fibonacci_sequence",
            "complexity": "intermediate",
        },
        {
            "task": "causal_reasoning",
            "input_data": [
                {"event": "rain", "result": "wet_ground"},
                {"event": "sun", "result": "dry_ground"},
                {"event": "rain", "result": "wet_ground"},
            ],
            "expected_pattern": "weather_causation",
            "complexity": "advanced",
        },
    ]

    for i, scenario in enumerate(learning_scenarios, 1):
        print(f'\n🧠 Memory Learning Scenario {i}: {scenario["task"]}')
        print(f'   Input: {scenario["input_data"]}')
        print(f'   Expected Pattern: {scenario["expected_pattern"]}')

        # Store learning data
        memory_id = memory.remember(
            content=scenario["input_data"],
            context={
                "task_type": scenario["task"],
                "complexity": scenario["complexity"],
                "timestamp": "2025-07-29T03:05:00",
            },
        )

        # Test pattern recognition and recall
        if hasattr(memory, "find_patterns"):
            patterns = memory.find_patterns(scenario["input_data"])
            print(f"   ✅ Detected Patterns: {patterns}")

        if hasattr(memory, "predict_next"):
            prediction = memory.predict_next(scenario["input_data"])
            print(f"   🎯 Next Item Prediction: {prediction}")

        print(f"   💾 Stored as memory ID: {memory_id}")

except Exception as e:
    print(f"❌ Memory real learning scenarios failed: {e}")

print("\n============================================================")
print("📊 REAL FUNCTIONAL TEST SUMMARY")
print("============================================================")
print("🎯 These tests require actual problem-solving capabilities")
print("📋 Status: TESTING REAL FUNCTIONAL REQUIREMENTS")
print("✅ SUCCESS: Tests that solve actual problems with real data")
print("❌ LIMITATION: Depends on actual implementation depth")
