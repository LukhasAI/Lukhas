import asyncio
import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


async def ask_ai(question):
    response = client.post("/api/v1/emotion/analyze", json={"content": question})
    if response.status_code == 200:
        data = response.json()
        if data["data"]["dominant_emotion"]:
            return data["data"]["dominant_emotion"]
    return "I don't know"


class TestGeneralization(unittest.TestCase):
    def setUp(self):
        self.novel_tasks = [
            {"task": "I feel very happy and joyful.", "expected_answer": "joy"},
            {"task": "I'm so angry I could scream.", "expected_answer": "anger"},
            {"task": "I'm feeling down and sad.", "expected_answer": "sadness"},
            {"task": "I'm scared of the dark.", "expected_answer": "fear"},
            {
                "task": "I'm amazed by the beauty of the sunset.",
                "expected_answer": "wonder",
            },
            {
                "task": "I'm curious about how this AI works.",
                "expected_answer": "curiosity",
            },
            {
                "task": "I feel a sense of unity with the universe.",
                "expected_answer": "unity",
            },
            {
                "task": "I've had a moment of enlightenment.",
                "expected_answer": "enlightenment",
            },
            {
                "task": "I feel like I'm transcending my physical body.",
                "expected_answer": "transcendence",
            },
            {
                "task": "I'm fully aware and conscious in this moment.",
                "expected_answer": "lucid",
            },
        ]
        self.success_count = 0

    async def run_test(self):
        for task in self.novel_tasks:
            answer = await ask_ai(task["task"])
            if answer == task["expected_answer"]:
                self.success_count += 1

    def test_generalization_success_rate(self):
        asyncio.run(self.run_test())
        success_rate = (self.success_count / len(self.novel_tasks)) * 100
        print(f"Success rate on novel tasks: {success_rate:.2f}%")
        self.assertGreaterEqual(
            success_rate, 85, "Generalization success rate is below 85%"
        )


if __name__ == "__main__":
    unittest.main()
