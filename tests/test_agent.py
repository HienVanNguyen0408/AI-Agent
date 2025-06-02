import unittest
import sys
sys.path.append("src")
from src.agent.agent import get_ai_answer
from src.agent.utils import detect_intent

class TestAgent(unittest.TestCase):
    def test_get_ai_answer(self):
        prompt = "What is the best investment?"
        answer = get_ai_answer(prompt)
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer) > 0)

    def test_detect_intent(self):
        question = "What is the best investment?"
        intent, entities = detect_intent(question)
        self.assertIsInstance(intent, str)
        self.assertIsInstance(entities, dict)

if __name__ == '__main__':
    unittest.main()
