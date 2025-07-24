# result_processor.py

import pandas as pd
import json
import argparse
from config import EMOTION_CODEBOOK

def process_results(file_path, threshold):
    """
    Reads a file with raw LLM output, processes it, and adds two new sheets:
    1. A detailed analysis with binary classifications for all emotions.
    2. A summary sheet with only the top-scoring emotion.
    
    Args:
        file_path (str): The path to the input .xlsx file.
        threshold (float): The cutoff score for classifying an emotion as present (1) or not (0)
                         in the detailed analysis sheet.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='LLM_Raw_Output')
        print(f"✅ Successfully loaded '{file_path}'. Processing {len(df)} rows.")
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error reading the Excel file or sheet: {e}")
        return

    # Lists to hold the data for our new sheets
    detailed_data = []
    summary_data = []
    
    base_cols = ["ResponseID", "NewID", "Text"]
    
    for index, row in df.iterrows():
        if pd.isna(row['Model_Response']):
            continue

        try:
            analysis = json.loads(row['Model_Response'])
            
            # --- Prepare data for the Detailed_Analysis sheet ---
            detailed_row = {col: row[col] for col in base_cols}
            emotions_present = []
            
            for emotion in EMOTION_CODEBOOK.keys():
                emotion_data = analysis.get(emotion, {"score": 0.0, "justification": "N/A"})
                score = float(emotion_data.get("score", 0.0))
                
                is_present = 1 if score >= threshold else 0
                detailed_row[f"{emotion}_binary"] = is_present
                detailed_row[f"{emotion}_justification"] = emotion_data.get("justification", "N/A")
                
                if is_present == 1:
                    emotions_present.append(emotion)
            
            if not emotions_present:
                detailed_row['Final_Classification'] = 'neutral'
                detailed_row['is_neutral'] = 1
            else:
                detailed_row['Final_Classification'] = ", ".join(emotions_present)
                detailed_row['is_neutral'] = 0

            detailed_data.append(detailed_row)

            # --- Prepare data for the Top_Emotion_Summary sheet ---
            summary_row = {col: row[col] for col in base_cols}
            top_emotion = 'neutral'
            top_score = 0.0
            top_justification = 'No dominant emotion found.'

            if analysis: # Ensure analysis dictionary is not empty
                # Find the emotion with the highest score
                max_emotion_item = max(analysis.items(), key=lambda item: item[1].get('score', 0.0), default=(None, None))
                
                if max_emotion_item[0] is not None:
                    top_emotion = max_emotion_item[0]
                    top_score = max_emotion_item[1].get('score', 0.0)
                    top_justification = max_emotion_item[1].get('justification', 'N/A')

            summary_row['Top_Emotion'] = top_emotion
            summary_row['Top_Score'] = top_score
            summary_row['Top_Justification'] = top_justification
            summary_data.append(summary_row)
            
        except (json.JSONDecodeError, TypeError) as e:
            print(f"⚠️ Could not parse JSON for NewID {row.get('NewID', 'N/A')}: {e}")
            continue

    if not detailed_data:
        print("No data was processed. Exiting.")
        return

    # Create DataFrames for the new sheets
    detailed_df = pd.DataFrame(detailed_data)
    summary_df = pd.DataFrame(summary_data)
    
    # Organize columns for clarity in the detailed sheet
    final_cols_order = base_cols + ['Final_Classification', 'is_neutral'] + \
                       [col for col in detailed_df.columns if col not in base_cols + ['Final_Classification', 'is_neutral']]
    detailed_df = detailed_df[final_cols_order]

    try:
        # Use ExcelWriter to add multiple sheets to the same file
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write the detailed analysis sheet
            detailed_sheet_name = f'Detailed_Analysis_T{str(threshold).replace(".", "")}'
            detailed_df.to_excel(writer, sheet_name=detailed_sheet_name, index=False)
            print(f"✅ Successfully added '{detailed_sheet_name}' sheet.")

            # Write the top emotion summary sheet
            summary_sheet_name = 'Top_Emotion_Summary'
            summary_df.to_excel(writer, sheet_name=summary_sheet_name, index=False)
            print(f"✅ Successfully added '{summary_sheet_name}' sheet.")

        print(f"\nProcessing complete. All sheets saved to '{file_path}'.")
    except Exception as e:
        print(f"❌ An error occurred while writing the new sheets to the Excel file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Process LLM raw output to create detailed analysis and summary sheets.")
    parser.add_argument("--file", type=str, required=True, help="Path to the Excel file with LLM raw output.")
    parser.add_argument("--threshold", type=float, required=True, help="A cutoff score (e.g., 0.6) to classify an emotion as present.")
    
    args = parser.parse_args()
    
    process_results(args.file, args.threshold)

if __name__ == "__main__":
    main()
