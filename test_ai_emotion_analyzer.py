import unittest
import os
import pandas as pd
import json
from unittest.mock import patch, MagicMock

# Import the functions to be tested
# Note: To make these imports work, ensure your config.py and other scripts are in the same directory
# or accessible via your PYTHONPATH.
from ai_emotion_analyzer import process_spreadsheet
from results_processor import process_results
import config

class TestEmotionAnalysisWorkflow(unittest.TestCase):

    def setUp(self):
        """Set up a testing environment before each test."""
        # Create mock directories
        self.input_dir = 'test_input'
        self.output_dir = 'test_output'
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Override config directories for the test
        config.INPUT_DIR = self.input_dir
        config.OUTPUT_DIR = self.output_dir

        # Create a dummy input spreadsheet
        self.test_spreadsheet_path = os.path.join(self.input_dir, config.SPREADSHEET_FILENAME)
        dummy_data = {
            "ResponseID": [101],
            "NewID": ["test_id_01"],
            "Text": ["I am so happy with the new program, it's a huge relief!"]
        }
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_excel(self.test_spreadsheet_path, sheet_name=config.SHEET_NAME, index=False)

    def tearDown(self):
        """Clean up the testing environment after each test."""
        # Remove created files and directories
        for root, dirs, files in os.walk(self.input_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.input_dir)

        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.output_dir)

    @patch('ai_emotion_analyzer.EmotionClassifierClient')
    def test_01_raw_data_generation(self, MockEmotionClassifierClient):
        """
        Test the first script (ai_emotion_analyzer.py).
        It should process a spreadsheet, call the (mocked) API, and save the raw results.
        """
        # --- Mocking Setup ---
        # Define the fake response the mock API client should return
        mock_api_response = [
            {
                "NewID": "test_id_01",
                "analysis": {
                    "anger": {"score": 0.1, "justification": "No anger detected."},
                    "fear": {"score": 0.0, "justification": "No fear detected."},
                    "disgust": {"score": 0.0, "justification": "No disgust detected."},
                    "sadness": {"score": 0.1, "justification": "No sadness detected."},
                    "enjoyment": {"score": 0.9, "justification": "Expresses happiness and relief."},
                    "surprise": {"score": 0.2, "justification": "Slight surprise at the benefit."},
                    "neutral": {"score": 0.0, "justification": "Clearly expresses emotion."}
                }
            }
        ]
        
        # Configure the mock instance to return our fake response
        mock_instance = MockEmotionClassifierClient.return_value
        mock_instance.classify_batch.return_value = mock_api_response

        # --- Execution ---
        # Run the spreadsheet processing function
        process_spreadsheet(self.test_spreadsheet_path, mock_instance)

        # --- Assertions ---
        # Check that the output directory contains exactly one file
        output_files = os.listdir(self.output_dir)
        self.assertEqual(len(output_files), 1, "There should be one output file.")
        
        # Load the generated output file
        output_file_path = os.path.join(self.output_dir, output_files[0])
        self.assertTrue(os.path.exists(output_file_path))
        
        # Check the contents of the output file
        df_out = pd.read_excel(output_file_path, sheet_name='LLM_Raw_Output')
        self.assertEqual(len(df_out), 1)
        self.assertIn('Model_Response', df_out.columns)
        
        # Verify the model response was written correctly
        model_response_json = json.loads(df_out.iloc[0]['Model_Response'])
        self.assertEqual(model_response_json, mock_api_response[0]['analysis'])

    def test_02_results_processing(self):
        """
        Test the second script (results_processor.py).
        It should read a raw output file and generate summary sheets.
        """
        # --- Test Setup ---
        # Create a dummy raw output file for this test
        raw_output_path = os.path.join(self.output_dir, "test_raw_output.xlsx")
        raw_data = {
            "ResponseID": [101],
            "NewID": ["test_id_01"],
            "Text": ["I am so happy with the new program, it's a huge relief!"],
            "Model_Response": [
                json.dumps({
                    "anger": {"score": 0.1, "justification": "No anger."},
                    "enjoyment": {"score": 0.9, "justification": "Expresses happiness."},
                    "sadness": {"score": 0.0, "justification": "No sadness."}
                })
            ]
        }
        pd.DataFrame(raw_data).to_excel(raw_output_path, sheet_name='LLM_Raw_Output', index=False)

        # --- Execution ---
        # Run the results processing function with a threshold
        test_threshold = 0.5
        process_results(raw_output_path, test_threshold)

        # --- Assertions ---
        # Load the processed file and check the new sheets
        xls = pd.ExcelFile(raw_output_path)
        self.assertIn(f'Detailed_Analysis_T05', xls.sheet_names)
        self.assertIn('Top_Emotion_Summary', xls.sheet_names)

        # Check the Detailed_Analysis sheet
        df_detailed = pd.read_excel(xls, sheet_name=f'Detailed_Analysis_T05')
        self.assertEqual(df_detailed.iloc[0]['Final_Classification'], 'enjoyment')
        self.assertEqual(df_detailed.iloc[0]['enjoyment_binary'], 1)
        self.assertEqual(df_detailed.iloc[0]['anger_binary'], 0) # Below threshold

        # Check the Top_Emotion_Summary sheet
        df_summary = pd.read_excel(xls, sheet_name='Top_Emotion_Summary')
        self.assertEqual(df_summary.iloc[0]['Top_Emotion'], 'enjoyment')
        self.assertEqual(df_summary.iloc[0]['Top_Score'], 0.9)


if __name__ == '__main__':
    unittest.main()
