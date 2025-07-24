# AI Emotion Analyzer

This Python project leverages Google's Gemini large language model via Vertex AI to perform detailed emotion analysis on text data. The workflow consists of two main scripts:

1.  **`ai_emotion_analyzer.py`**: Reads text excerpts from a local Excel file, sends them in batches to the Gemini model for emotion classification, and saves the raw JSON responses back into a new timestamped Excel file.
2.  **`results_processor.py`**: Takes the raw output file from the first script and processes the JSON responses into two user-friendly summary sheets within the same Excel file.

## Features

-   **Batch Processing**: Efficiently processes large datasets by sending text excerpts to the Gemini API in customizable batches.
-   **Advanced Emotion Analysis**: Utilizes a detailed `EMOTION_CODEBOOK` in `config.py`, complete with descriptions, examples, and chain-of-thought instructions to guide the model's classification process.
-   **System Instructions**: Provides the Gemini model with a high-level "persona" as an expert research assistant to improve the quality and consistency of its analysis.
-   **Robust Logging**: Creates a timestamped log file for every run, recording the exact prompts sent to the model and the full, raw responses received. This is invaluable for debugging and auditing.
-   **Two-Step Analysis**:
    -   Generates a raw data file with the model's complete JSON output.
    -   Processes the raw data to create a **Detailed Analysis** sheet with binary classifications and a **Top Emotion Summary** sheet for quick insights.
-   **Configurability**: Centralizes all key parameters—such as project IDs, model names, file paths, and processing settings—in a single `config.py` file for easy modification.

## Prerequisites

-   A Google Cloud project with the Vertex AI API enabled.
-   Python 3.7 or higher.
-   `gcloud` CLI authenticated to your Google Cloud account.

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/JoelWiebe/ai-emotion-analyzer.git](https://github.com/JoelWiebe/ai-emotion-analyzer.git)
    cd ai-emotion-analyzer
    ```

2.  **Install Dependencies:**
    Create a virtual environment (recommended) and install the required packages from `requirements.txt`.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Authenticate with Google Cloud:**
    If you haven't already, log in with the `gcloud` CLI.
    ```bash
    gcloud auth application-default login
    ```

4.  **Set Environment Variables:**
    Create a file named `.env` in the root of the project directory. This file will securely store your project-specific credentials. Add the following variables:
    ```
    PROJECT_ID="your-gcp-project-id"
    LOCATION="your-gcp-project-location" # e.g., us-central1
    GEMINI_MODEL="gemini-1.5-flash-001" # or your preferred model
    ```

## Workflow / Usage

The analysis is a two-step process.

### Step 1: Generate Raw Emotion Analysis

This step uses `ai_emotion_analyzer.py` to communicate with the Gemini API.

1.  **Prepare Input File:**
    -   Place your source Excel spreadsheet in the `input_files/` directory.
    -   Update `config.py` to specify the correct `SPREADSHEET_FILENAME` and the `SHEET_NAME` within that file you wish to process.
    -   Ensure your spreadsheet has the required columns: `ResponseID`, `NewID`, and `Text`.

2.  **Run the Analyzer:**
    Execute the script from your terminal.
    ```bash
    python3 ai_emotion_analyzer.py
    ```
    The script will print its progress, including which batch is being processed. A new Excel file with a timestamp (e.g., `llm_raw_output_Validation_Set_2024-07-23_10-30-00.xlsx`) will be created in the `output_files/` directory. This file contains the raw JSON output from the model in a `Model_Response` column.

### Step 2: Process Raw Results into Summaries

This step uses `results_processor.py` to parse the raw JSON from the previous step and create readable summary sheets.

1.  **Run the Processor:**
    Execute the script from your terminal, providing the path to the output file from Step 1 and a confidence threshold. The threshold (a value between 0.0 and 1.0) determines the cutoff score for classifying an emotion as present.
    ```bash
    python3 results_processor.py --file "output_files/llm_raw_output_Validation_Set_2024-07-23_10-30-00.xlsx" --threshold 0.6
    ```

2.  **View Results:**
    Open the same Excel file. Two new sheets will have been added:
    -   `Detailed_Analysis_T06`: Shows a binary (1/0) classification for every emotion based on the `--threshold` you provided, along with the model's justification for each.
    -   `Top_Emotion_Summary`: Shows only the single emotion with the highest confidence score for each text excerpt.

## Configuration

All major settings are controlled in `config.py`:

-   `PROJECT_ID`, `LOCATION`, `GEMINI_MODEL`: Your Google Cloud and model settings (loaded from `.env`).
-   `INPUT_DIR`, `OUTPUT_DIR`: Specify the directories for input and output files.
-   `SPREADSHEET_FILENAME`, `SHEET_NAME`: Define the source Excel file and the specific sheet to analyze.
-   `QUESTION`: The research question associated with the text responses. This is included in the payload sent to the model.
-   `BATCH_SIZE`: The number of text excerpts to process in a single API call. Adjust based on excerpt length and model context window limits.
-   `EMOTION_CODEBOOK`: A critical dictionary where you define the emotions to be classified. For each emotion, you can provide a `description`, `examples`, and a detailed `chain_of_thought` to guide the model's reasoning process.

## Testing

The project includes a test suite, `test_emotion_analysis_workflow.py`, which verifies the end-to-end functionality of both scripts. It uses mock objects to simulate API calls, so it can be run offline without incurring any costs. The tests create temporary input/output directories and files, and automatically clean them up upon completion.

To run the tests, execute the following command from the root of the project directory:

```bash
python3 -m unittest -v test_ai_emotion_analyzer.py
```