# ai_emotion_analyzer.py

import os
import json
import pandas as pd
import datetime
import re
from math import ceil
import traceback # Import the traceback module for detailed error logging

# Import the Google GenAI library
from google import genai
from google.genai import types

# Import settings from the configuration file
from config import (
    PROJECT_ID,
    LOCATION,
    GEMINI_MODEL,
    QUESTION,
    SHEET_NAME,
    BATCH_SIZE,
    EMOTION_CODEBOOK,
    INPUT_DIR,
    OUTPUT_DIR,
    SPREADSHEET_FILENAME
)

class EmotionClassifierClient:
    """
    A client to classify emotions in text batches using the Google GenAI library for Vertex AI,
    following the provided exemplar for API calls.
    """
    def __init__(self, log_file_path):
        """
        Initializes the unified client for Vertex AI and sets up the log file path.
        """
        try:
            # Initialize the client as shown in the exemplar.
            self.client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location=LOCATION,
            )
            self.log_file_path = log_file_path
            print(f"✅ Client initialized for project '{PROJECT_ID}' in location '{LOCATION}'.")
            print(f"📝 Logging prompts and responses to: {self.log_file_path}")

        except Exception as e:
            print("\n❌ Client Initialization Failed.")
            print(f"  - Project ID: '{PROJECT_ID}'")
            print(f"  - Location: '{LOCATION}'")
            print("\nPlease check your .env file, authentication, and Google Cloud project settings.\n")
            raise e


    def classify_batch(self, excerpts_batch, batch_num, total_batches):
        """
        Classifies a batch of text excerpts for emotions using a streaming API call.

        Args:
            excerpts_batch (list): A list of dictionaries for the batch.
            batch_num (int): The current batch number.
            total_batches (int): The total number of batches.

        Returns:
            list: A list of dictionaries with the emotion analysis for each excerpt,
                  or an empty list if an error occurs.
        """
        print(f"\nProcessing a batch of {len(excerpts_batch)} excerpts...")

        payload = {
            "question_asked": QUESTION,
            "excerpts_to_classify": excerpts_batch
        }
        json_payload = json.dumps(payload, indent=2)

        prompt = (
            "The following JSON object contains a batch of excerpts from parent responses. "
            "Analyze each excerpt individually.\n\n"
            f"{json_payload}\n\n"
            f"CODEBOOK:\n{json.dumps(EMOTION_CODEBOOK, indent=2)}\n\n"
            "For EACH excerpt, provide your analysis as a JSON object. Return your complete analysis as a single, "
            "valid JSON list, where each object corresponds to one input excerpt and uses the following format:\n\n"
            "[\n"
            "  {\n"
            "    \"NewID\": \"(The ID of the first excerpt)\",\n"
            "    \"analysis\": {\n"
            "      \"anger\": {\"score\": 0.xx, \"justification\": \"...\"},\n"
            "      \"fear\": {\"score\": 0.xx, \"justification\": \"...\"},\n"
            "      \"disgust\": {\"score\": 0.xx, \"justification\": \"...\"},\n"
            "      \"sadness\": {\"score\": 0.xx, \"justification\": \"...\"},\n"
            "      \"enjoyment\": {\"score\": 0.xx, \"justification\": \"...\"},\n"
            "      \"surprise\": {\"score\": 0.xx, \"justification\": \"...\"}\n"
            "    }\n"
            "  }\n"
            "]\n\n"
            "Ensure the output is ONLY the JSON list, without any surrounding text or markdown."
        )

        contents = [prompt]

        system_instruction = types.Content(
            parts=[
                types.Part(text=(
                    "You are an expert research assistant specializing in the analysis of emotions in text. "
                    "Your task is to meticulously classify the specific emotions conveyed in excerpts from parent responses. "
                    "For each excerpt, you must provide a confidence score and a detailed justification for each emotion listed in the provided codebook. "
                    "Adhere strictly to the codebook definitions and the required JSON output format."
                ))
            ]
        )

        generation_config = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=8192,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
            ],
            system_instruction=system_instruction
        )

        log_header = f"""
{'='*80}
BATCH {batch_num}/{total_batches} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

---------- PROMPT SENT TO MODEL ----------
"""
        print(log_header)
        print(prompt)
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_header)
            f.write(prompt + '\n')

        try:
            response_chunks = self.client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=contents,
                config=generation_config
            )
            
            full_response_text = "".join(chunk.text for chunk in response_chunks)
            
            response_header = "\n---------- FULL RESPONSE FROM MODEL ----------\n"
            print(response_header)
            print(full_response_text)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(response_header)
                f.write(full_response_text + '\n')

            clean_response = re.sub(r'```json\s*(.*)\s*```', r'\1', full_response_text, flags=re.DOTALL)
            return json.loads(clean_response)
            
        except Exception as e:
            print("\n" + "="*80)
            print("❌ AN UNEXPECTED ERROR OCCURRED".center(80))
            print("="*80)
            print("\n[ERROR DETAILS]")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {e}")
            print("\n[FULL TRACEBACK]")
            traceback.print_exc()
            print("\n" + "="*80)
            return []


def process_spreadsheet(file_path, classifier_client):
    """Loads a spreadsheet, processes texts in batches, and saves the raw model output."""
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error reading spreadsheet: {e}")
        return

    base_columns = ["ResponseID", "NewID", "Text"]
    all_required_columns = base_columns
    for col in all_required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in sheet '{SHEET_NAME}'")

    df_to_process = df[pd.notna(df['Text']) & (df['Text'] != "")]
    excerpt_list = df_to_process[all_required_columns].to_dict('records')
    
    results_map = {}
    total_batches = ceil(len(excerpt_list) / BATCH_SIZE)
    print(f"Beginning processing for {len(excerpt_list)} excerpts in {total_batches} batches.")

    for i in range(0, len(excerpt_list), BATCH_SIZE):
        batch_records = excerpt_list[i:i + BATCH_SIZE]
        
        model_batch_payload = []
        for record in batch_records:
            payload_item = record.copy()
            payload_item.pop("ResponseID", None)
            model_batch_payload.append(payload_item)
            
        batch_num = (i // BATCH_SIZE) + 1
        print(f"--- Processing Batch {batch_num}/{total_batches} ---")
        
        results = classifier_client.classify_batch(model_batch_payload, batch_num, total_batches)
        for result in results:
            if result.get("NewID") and result.get("analysis"):
                results_map[result["NewID"]] = json.dumps(result["analysis"])

    output_df = df[all_required_columns].copy()
    output_df['Model_Response'] = output_df['NewID'].map(results_map)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"llm_raw_output_{SHEET_NAME.replace(' ', '_')}_{timestamp}.xlsx"
    output_file_path = os.path.join(OUTPUT_DIR, output_filename)
    
    output_df.to_excel(output_file_path, sheet_name='LLM_Raw_Output', index=False)
    print(f"\n✅ Processing complete. Raw model results saved to: {output_file_path}")


def main():
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"prompt_log_{timestamp}.txt"
        log_file_path = os.path.join(OUTPUT_DIR, log_filename)

        classifier_client = EmotionClassifierClient(log_file_path=log_file_path)
        file_path = os.path.join(INPUT_DIR, SPREADSHEET_FILENAME)
        process_spreadsheet(file_path, classifier_client)
    except Exception as e:
        print(f"\nScript terminated due to a critical error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
