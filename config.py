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
SPREADSHEET_FILENAME = "Full Data Uncoded.xlsx" # The name of your input spreadsheet

# Data Processing Settings
# The single question that all the text responses in the sheet are answering.
QUESTION = "Are you satisfied with the current care arrangements? Please explain your response"
# The name of the sheet within the spreadsheet to process.
SHEET_NAME = "Validation Set" # Modify as needed (e.g., "Concerns", "Challenges")
# Number of text excerpts to process in a single API call.
BATCH_SIZE = 5

# Data Extraction Targets (modify as needed)
EMOTION_CODEBOOK = {
    "anger": {
        "description": "Parents feel blocked from pursuing a goal and/or are treated unfairly.",
        "examples": [
            "It is too difficult to handle work while having a child at home full time.",
            "I’m a stay at home mom I don’t go nowhere they got me 24/7",
            "It’s very hard to work or even just to do something small. I feel very exhausted, lonely, and like almost crazy.",
            "Constant turn over. Quality is lacking.",
            "Her parents are raising her. Not the government ",
            "3 year wait list"
        ],
        "chain_of_thought": """
            To classify the excerpt as anger, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses emotions ranging from dissatisfaction to strong negative emotions (e.g., frustration, resentment, outrage). Look for forceful language, exclamations, or threats.

            2. **Triggering Events:** The excerpt references one or more common triggers for anger:
                * Injustice: Unfair treatment, unequal distribution of resources, violation of rights.
                * Blocked Goals: Obstacles preventing the parent from achieving their desired outcomes.
                * Betrayal/Abandonment: Feelings of being let down or unsupported by systems or individuals.
                * Harm: Perceived threats to the parent's well-being, their child's well-being, or their family.

            3. **Language Clues:** The excerpt contains words or phrases indicative of anger:
                * Strong negative adjectives: "horrible", "terrible", "disgusting"
                * Accusatory language: "they should", "it's not fair", "they're wrong"
                * Expressions of frustration: "I can't believe", "I'm so tired of", "this is ridiculous"
        """
    },
    "fear": {
        "description": "Parents feel the threat of physical, emotional, or psychological harm (real or imagined).",
        "examples": [
            "I am very concerned that I will not be able to find two daycare spots when I need to return to work. ",
            "That so scary"
        ],
        "chain_of_thought": """
            To classify the excerpt as fear, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses worry, anxiety, apprehension, or a sense of threat.

            2. **Focus of Concern:** The excerpt focuses on potential negative outcomes, risks, or dangers related to childcare. This could include concerns about:
                * Child safety
                * Quality of care
                * Availability of care
                * Financial implications

            3. **Language Clues:** The excerpt contains words or phrases indicative of fear:
                * "Worried", "concerned", "afraid"
                * "What if...?" questions
                * Expressions of uncertainty or doubt
        """
    },
    "disgust": {
        "description": "Parents feel aversion towards something offensive or socially/morally reprehensible (i.e., perceived physical senses, actions of others, or ideas).",
        "examples": [
            "I dont trust in child care programs"
        ],
        "chain_of_thought": """
            To classify the excerpt as disgust, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses revulsion, aversion, or strong disapproval.

            2. **Object of Disgust:** The excerpt identifies something the parent finds repulsive, offensive, or morally objectionable. This could include:
                * Aspects of childcare policies or practices
                * Specific behaviors of individuals or organizations
                * Perceived injustices or unfairness

            3. **Language Clues:** The excerpt contains words or phrases indicative of disgust:
                * "Disgusting", "repulsive", "sickening"
                * "I can't stand", "I hate"
                * Expressions of contempt or disdain
        """
    },
    "sadness": {
        "description": "Parents feel disappointment and longing or a sense of loss for someone or something.",
        "examples": [
            "I am not at all satisfied with the quality of care but it is the only childcare option in my area",
            "I have nobody to watch my child in order for one of us to find a job so that we can qualify for more assistance."
        ],
        "chain_of_thought": """
            To classify the excerpt as sadness, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses disappointment, discouragement, hopelessness, or a sense of loss.

            2. **Focus of Sadness:** The excerpt focuses on something the parent has lost, is missing, or is unable to attain. This could include:
                * Missed opportunities for childcare
                * Lack of access to desired programs
                * Financial burdens related to childcare
                * Feelings of being overwhelmed or unsupported

            3. **Language Clues:** The excerpt contains words or phrases indicative of sadness:
                * "Sad", "disappointed", "heartbroken"
                * "I wish" or "I can't"
                * Expressions of longing or regret
        """
    },
    "enjoyment": {
        "description": "Parents feel a sense of connection or pleasure.",
        "examples": [
            "They are very good with my child. The area is clean and they have the appropriate caregivers.",
            "My child is more independent, and he enjoys going daycare. The staff are amazing.",
            "It having amazing impact on my mental peace",
            "Its good to have this programm so that low income family like us can survive in the country."
        ],
        "chain_of_thought": """
            To classify the excerpt as enjoyment, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses happiness, satisfaction, relief, or a sense of pleasure.

            2. **Source of Enjoyment:** The excerpt focuses on something the parent finds positive or beneficial. This could include:
                * Positive experiences with childcare providers
                * Child's development and learning
                * Financial benefits or support
                * Feeling appreciated or supported

            3. **Language Clues:** The excerpt contains words or phrases indicative of enjoyment:
                * "Happy", "grateful", "relieved"
                * "I love", "it's great", "I'm so glad"
                * Expressions of enthusiasm or excitement
        """
    },
    "surprise": {
        "description": "Parents encounter sudden and unexpected changes/occurrences.",
        "examples": [
            "This is the first time I have ever seen a few episodes"
        ],
        "chain_of_thought": """
            To classify the excerpt as surprise, ensure the following conditions are met:

            1. **Emotional State:** The parent expresses astonishment, shock, or unexpectedness.

            2. **Unexpected Event:** The excerpt refers to something that happened suddenly or was not anticipated by the parent. This could include:
                * Unexpected policy changes
                * Unexpectedly high or low costs
                * Unexpected behaviors or outcomes related to childcare

            3. **Language Clues:** The excerpt contains words or phrases indicative of surprise:
                * "Surprised", "shocked", "amazed"
                * "I can't believe", "I didn't expect"
                * Exclamations: "Wow!", "Oh my gosh!"
        """
    },
    "neutral": {
        "description": "Parents state information without evidence of emotion.",
        "examples": [
            "My mum takes care of my kid"
        ],
        "chain_of_thought": """
            To classify the excerpt as neutral, ensure the following conditions are met:

            1. **Lack of Emotional Expression:** The parent does not express any clear emotion. The tone is factual, objective, or informational.

            2. **Focus on Facts:** The excerpt focuses on providing information, stating facts, or asking questions without expressing personal feelings or opinions.

            3. **Language Clues:** The excerpt lacks any words or phrases typically associated with specific emotions or is incomprehensible (i.e., missing words such as the subject/object of the sentence).
        """
    }
}