import unittest
from ai_emotion_analyzer import EmotionClassifierClient
from config import *

class TestClassifyEmotion(unittest.TestCase):
    @classmethod  
    def setUpClass(cls):  
        pass

    def setUp(self):
        self.classifier = EmotionClassifierClient()
        self.example_excerpt = "I'm so relieved! The subsidy has cut our daycare costs in half. It's such a huge help for our family."  # Example
        self.example_question = "Benefits: Parents’ responses for the question “Please describe the benefits you experienced/noticed since the introduction of the low cost child care program?"  # Example question type

    def test_classify_excerpt(self):
        result = self.classifier.classify_excerpt(self.example_excerpt, self.example_question)

        # Check the type of the result
        self.assertIsInstance(result, dict, "The result should be a dictionary.")

        # Check that all emotions are present
        expected_emotions = ["anger", "fear", "disgust", "sadness", "enjoyment", "surprise", "neutral"]
        for emotion in expected_emotions:
            self.assertIn(emotion, result, f"Emotion '{emotion}' should be in the result.")

        # Check that scores are floats within 0-1 range AND justifications are strings
        for emotion, data in result.items():
            self.assertIsInstance(data, dict, f"Data for '{emotion}' should be a dictionary.")  # Ensure nested dict
            self.assertIn("score", data, f"Data for '{emotion}' should have a 'score' key.")  
            self.assertIn("justification", data, f"Data for '{emotion}' should have a 'justification' key.")

            score = data["score"]
            justification = data["justification"]
            self.assertIsInstance(score, float, f"Score for '{emotion}' should be a float.")
            self.assertTrue(0 <= score <= 1, f"Score for '{emotion}' should be between 0 and 1.")
            self.assertIsInstance(justification, str, f"Justification for '{emotion}' should be a string.")

        # Example of specific assertions (adapt to your test data)
        self.assertGreater(result["enjoyment"]["score"], 0.5, "Enjoyment score should be high.")
        self.assertIn("relief", result["enjoyment"]["justification"].lower(),  # Case-insensitive check
                    "Justification for enjoyment should mention relief.")

        
if __name__ == '__main__':
    unittest.main()