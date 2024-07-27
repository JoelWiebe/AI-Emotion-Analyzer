# AI-Emotion-Analyzer
This Python script leverages the power of Google's Gemini language model via Vertex AI to analyze the emotions conveyed in text excerpts from parent responses about a childcare program. It classifies excerpts into different emotions based on a predefined rubric and provides confidence scores with justifications for each classification.

## Features

- **Excel Spreadsheet Parsing:** Reads data from Excel spreadsheets (.xlsx), extracting relevant text excerpts from specified columns.
- **Gemini-Powered Emotion Classification:** Employs the Gemini model to classify the emotions expressed in text excerpts.
- **Customizable Emotion Rubric:**  Uses a predefined emotion rubric (based on Ekman's 6 basic emotions + neutral) that you can tailor to your specific needs.
- **Confidence Scores and Justifications:** Provides not only the predicted emotion but also a confidence score (0 to 1) and a brief justification for each classification.
- **Structured Output:** Generates new Excel spreadsheets with the original data plus columns for model response, AI-assigned emotion, confidence score, and justification.
- **Timestamped Results:** Appends a timestamp to the output file name for easy tracking.
- **Unit Tests:** Includes a test suite (test_ai_emotion_analyzer.py) to verify the script's core functionality.
  
## Prerequisites

- **Google Cloud Project:**  A Google Cloud project with Vertex AI enabled and the Gemini model available.
- **Python Environment:** Python 3.7 or higher with the following libraries installed:
    - `vertexai`
    - `pandas`
    - `openpyxl`
- **API Key:**  A valid API key for the Gemini model, obtained through your Google Cloud project.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/JoelWiebe/ai-emotion-analyzer.git
   cd ai-emotion-analyzer
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Log in to Google Cloud:** 
  ```bash
  gcloud auth application-default login
  ```

4. **Set Environment Variables:**
Create a file named .env in the project directory and add the following:
```
PROJECT_ID=your-project-id
LOCATION=your-project-location
GEMINI_MODEL=gemini-1.5-flash-001 # or your preferred model
```

## Usage
1. **Prepare Input Documents:**
- Place your Excel spreadsheet (.xlsx) in the input_data directory.
- Ensure it has sheets named "Challenges," "Benefits," and "Concerns."
- Verify it has columns: "ResponseID," "NewID," "Text," and "Manual_Coding."

2. **Customize Emotion Rubric (Optional):**
- Modify the EMOTION_RUBRIC in the ai_emotion_analyzer.py file to match your specific emotion categories and descriptions.

3. **Run the Script:**
   ```bash
   python ai-data-extractor.py
   ```

4. **View Results:**
- The analyzed data will be saved in new Excel files (e.g., analyzed_Challenges_2024-07-08_15-32-10.xlsx) in the output_data directory.

## Running Tests
To run the unit tests, use the following command:
```bash
python -m unittest -v -f test_ai_emotion_analyzer.py  
```
