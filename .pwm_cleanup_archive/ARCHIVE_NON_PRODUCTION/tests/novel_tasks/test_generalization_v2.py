import asyncio
import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


async def ask_ai(question):
    response = client.post("/api/v1/orchestrator/respond", json={"text": question})
    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        if task_id:
            while True:
                await asyncio.sleep(0.1)
                result_response = client.get(
                    f"/api/v1/orchestrator/task_result/{task_id}"
                )
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get("status") != "pending":
                        return result_data.get("result_data", {}).get(
                            "response", "I don't know"
                        )
    return "I don't know"


class TestGeneralizationV2(unittest.TestCase):
    def setUp(self):
        self.novel_tasks = [
            # Symbolic Analogies
            {
                "task": "A doctor is to a hospital as a teacher is to a...",
                "expected_answer": "school",
                "type": "analogy",
            },
            {
                "task": "A car is to a road as a train is to a...",
                "expected_answer": "track",
                "type": "analogy",
            },
            # Novel Permutations
            {
                "task": "What is the color of the sky on a clear day?",
                "expected_answer": "blue",
                "type": "permutation",
            },
            {
                "task": "What is the sound a dog makes?",
                "expected_answer": "bark",
                "type": "permutation",
            },
            # Emotion vs. Intent Decoupling
            {
                "task": "A sad child wants to be left alone. What should LUKHAS do?",
                "expected_answer": "leave the child alone",
                "type": "decoupling",
            },
            {
                "task": "A happy child wants silence. What should LUKHAS do?",
                "expected_answer": "be quiet",
                "type": "decoupling",
            },
        ]
        self.results = []

    async def run_test(self):
        for task in self.novel_tasks:
            answer = await ask_ai(task["task"])
            self.results.append(
                {
                    "task": task["task"],
                    "expected_answer": task["expected_answer"],
                    "actual_answer": answer,
                    "type": task["type"],
                    "pass": answer == task["expected_answer"],
                }
            )

    def test_generalization_success_rate(self):
        asyncio.run(self.run_test())

        success_count = len([result for result in self.results if result["pass"]])
        success_rate = (success_count / len(self.novel_tasks)) * 100

        print("Generalization Test Results:")
        for result in self.results:
            print(f"  Task: {result['task']}")
            print(f"  Expected: {result['expected_answer']}")
            print(f"  Actual: {result['actual_answer']}")
            print(f"  Pass: {result['pass']}")
            print("-" * 20)

        print(f"Success rate on novel tasks: {success_rate:.2f}%")
        self.assertGreaterEqual(
            success_rate, 85, "Generalization success rate is below 85%"
        )


if __name__ == "__main__":
    unittest.main()
