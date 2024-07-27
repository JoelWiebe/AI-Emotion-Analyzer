import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Project Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# Directory Setup
INPUT_DIR = "input_files"
OUTPUT_DIR = "output_files"
SPREADSHEET_FILENAME = "EmotionAnalysis_26Jul24_ValidationData.xlsx" #Modify as needed

# Data Extraction Targets (modify as needed)
EMOTION_RUBRIC = {
    "anger": {
        "description": "Any instances when parents were annoyed or were showing dissatisfaction.",
        "examples": [
            "i still pay 100% of the daycare fee per month regardless of whether my child attends daycare, and because of the setting, my child is sick at least for 1x week every month and my subsidy then gets reduced so it costs me more money when my child isn't even there", 
            "There is an extreme lack of availability for childcare in Ontario. To the point of where I am currently intending to change professions to become a childcare provider.",
            "It’s SO hard to get a spot. The wait list I’m on is 2 years!",
            "EXTREMELY difficult to find childcare. Me finding it was a total fluke."
        ],
        "chain_of_thought": """
            [Not available]
        """
    },
    "fear": {
        "description": "Any instances when parents showed concerns or worries",
        "examples": [
            "Very difficult to get into daycares that are decent. Demand has shot up and wait lists are years long. We don’t know what we will do for our youngest child when we need it",
            "Worried that there will be such shortage of good quality childcare because of the influx of children.",
            "Teachers are not as attentive to my child. Complaints about the lower standard of care."
            ],
        "chain_of_thought": """
            [Not available]
        """
    },
    "disgust": {
        "description": "Any instances when parents showed a feeling of aversion towards something offensive or socially/morally reprehensible",
        "examples": [
            "The arrangement is too confusing",
            "It’s too repetitive and people take advantage of it too much",
            "I dont trust child care facility owners. The ones I've heard of are cheap and cut corners and treat their employees terrible.",
            "Government programs always suck"
        ],
        "chain_of_thought": """
            [Not available]
        """
    },
    "sadness": {
        "description": "Any instances when parents showed a lack of hope or deep disappointment",
        "examples": [
            "Can't get into waiting list",
            "There are huge waitlists for spaces, I can't find spots for my younger children",
            "Can't find daycare for this price",
            "Cuts to resources, daycare centre considering not participating anymore because can't afford to keep running"
        ],
        "chain_of_thought": """
            [Not available]
        """
    },
    "enjoyment": {
        "description": "Participant ethnicity distribution by frequency or percentage.",
        "examples": [
            "It’s quality child care program provide my children with opportunities for socialisation, cognitive development and early learning experiences"
            "It gives a children a good start in life",
            "More money",
            "It cut my daycare cost in half",
            "My baby's daycare is subsidised and this is a great relief to us"
        ],
        "chain_of_thought": """
           [Not available]
        """
    },
    "surprise": {
        "description": "Any instances when parent indicated expression of unexpectedness",
        "examples": [
            "This is the first time I have ever seen a few episodes of",
            "my fees are $183 a month which is unheard of from my friends in Ontario"
        ],
        "chain_of_thought": """
            [Not available]
        """
    },
    "neutral": {
        "description": "No evidence of any emotion. Any instances when parents were simply stating information would be classified as neutral. ",
        "examples": [
            "not enough spaces", 
            "Staff shortages."
        ],
        "chain_of_thought": """
            - Look for sections titled 'Methods', 'Materials', or 'Procedure'.
            - Look for terms like 'device', 'hardware', 'platform', or specific device names.
            - If multiple devices are used, extract all relevant ones.
        """
    }
}