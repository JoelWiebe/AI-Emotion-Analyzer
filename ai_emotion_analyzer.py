import os
import json
import pandas as pd
import vertexai
import datetime
from config import *
import re
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models




class EmotionClassifierClient:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL,
            system_instruction="""You are a research assistant specializing in emotion analysis in text. Your task is to classify the emotion conveyed in excerpts from parent responses about a childcare program and provide a confidence score with justification for each emotion. You will be provided with a rubric describing various emotions to guide your classification."""
        )

    def classify_excerpt(self, excerpt, question):
        print(f"\nProcessing excerpt: {excerpt}")

        # Create JSON payload for Gemini with the excerpt and question
        payload = {
            "excerpt": excerpt,
            "question": question
        }

        json_payload = json.dumps(payload, indent=2)

        # Prompt template with emotion rubric and classification request
        prompt = (
            "The following is a JSON object containing an excerpt from a parent's response about a childcare program, along with the question they were responding to:\n\n"
            f"{json_payload}\n\n"
            f"Please use the following rubric to classify the emotion expressed in the excerpt:\n\n"
            f"{EMOTION_RUBRIC}\n\n"
            "Provide your classification as a JSON object. For each emotion, assess the confidence score (0 to 1) reflecting the degree to which the excerpt expresses that emotion, along with a brief justification for the score. The format should be:\n\n"
            "{\n  \"anger\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"fear\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"disgust\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"sadness\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"enjoyment\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"surprise\": {\"score\": 0.xx, \"justification\": \"...\"},\n  \"neutral\": {\"score\": 0.xx, \"justification\": \"...\"}\n}\n\n"
            "Do not include any Markdown formatting in your response. Ensure the JSON is valid and does not contain any extra characters or formatting.\n"
        )
        print(f"\nClassify excerpt prompt:\n\n{prompt}")

        # Generate classifications 
        generation_config = {
            "max_output_tokens": 1024,
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Call the model to predict and get results in string format
        response = self.model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings).text
        print(f"\nClassify excerpt response:\n\n{response}")

        clean_response = remove_json_markdown(response) 

        print(f"Classify exerpt response:\n\n{clean_response}")
        
        # convert the results to a python dictionary
        response_dict = json.loads(clean_response)

        return response_dict
    

def remove_json_markdown(text):
    pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    return pattern.sub(r'\1', text)

    
def process_spreadsheet(file_path, classifier_client):
    # Load Excel workbook
    with pd.ExcelFile(file_path) as xls:
        sheets = ["Challenges", "Benefits", "Concerns"]  
        required_columns = ["ResponseID", "NewID", "Text", "Manual_Coding"]

        # Check if the spreadsheet has the correct sheets and columns
        for sheet_name in sheets:
            if sheet_name not in xls.sheet_names:
                raise ValueError(f"Missing sheet: {sheet_name}")

            df = pd.read_excel(xls, sheet_name)
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing column '{col}' in sheet '{sheet_name}'")

        # Process each sheet
        for sheet_name in sheets:
            print(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(xls, sheet_name)
            
            # Create new columns if they don't exist
            new_columns = ["Model_Response", "AI_Coding", "AI_Confidence", "AI_Justification"]
            for col in new_columns:
                if col not in df.columns:
                    df[col] = ""  # Initialize with empty strings

            # Iterate through rows and classify excerpts
            for idx, row in df.iterrows():
                question = sheet_name  # The question is the sheet name
                text_excerpt = row["Text"]
                
                if not pd.isna(text_excerpt) and isinstance(text_excerpt, str):
                    emotion_scores = classifier_client.classify_excerpt(text_excerpt, question)
                    
                    # Get highest scoring emotion directly
                    highest_emotion = max(emotion_scores, key=lambda emotion: emotion_scores[emotion]["score"])
                    highest_score = emotion_scores[highest_emotion]

                    # Get justification (if available) - may need adjustment depending on exact response
                    justification = emotion_scores.get(highest_emotion, {}).get("justification", "")

                    # Store results in the DataFrame
                    df.at[idx, "Model_Response"] = json.dumps(emotion_scores)
                    df.at[idx, "AI_Coding"] = highest_emotion
                    df.at[idx, "AI_Confidence"] = highest_score
                    df.at[idx, "AI_Justification"] = justification 

            # Save updated DataFrame back to Excel
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            output_file = os.path.join(OUTPUT_DIR, f"analyzed_{sheet_name}_{timestamp}.xlsx")
            df.to_excel(output_file, index=False)
            print(f"Results for '{sheet_name}' saved to: {output_file}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    classifier_client = EmotionClassifierClient()

    file_path = os.path.join(INPUT_DIR, SPREADSHEET_FILENAME)
    process_spreadsheet(file_path, classifier_client)

if __name__ == "__main__":
    main()