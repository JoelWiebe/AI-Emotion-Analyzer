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
EMOTION_CODEBOOK = {
    "anger": {
        "description": "Any instance where parents feel blocked from their goal and/or are treated unfairly.",
        "examples": [
            "i still pay 100% of the daycare fee per month regardless of whether my child attends daycare, and because of the setting, my child is sick at least for 1x week every month and my subsidy then gets reduced so it costs me more money when my child isn't even there", 
            "There is an extreme lack of availability for childcare in Ontario. To the point of where I am currently intending to change professions to become a childcare provider.",
            "It’s SO hard to get a spot. The wait list I’m on is 2 years!",
            "EXTREMELY difficult to find childcare. Me finding it was a total fluke."
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
        "description": "Any instance where parents feel the threat or worry of physical, emotional, or psychological harm (real or imagined).",
        "examples": [
            "Very difficult to get into daycares that are decent. Demand has shot up and wait lists are years long. We don’t know what we will do for our youngest child when we need it",
            "Worried that there will be such shortage of good quality childcare because of the influx of children.",
            "leaving my kids with strangers constant worrying about my kids"
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
        "description": "Any instances where parents feel aversion towards something offensive or socially/morally reprehensible.",
        "examples": [
            "The arrangement is too confusing",
            "It’s too repetitive and people take advantage of it too much",
            "I dont trust child care facility owners. The ones I've heard of are cheap and cut corners and treat their employees terrible.",
            "Government programs always suck"
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
        "description": "Any instances where parents feel disappointment or a sense of loss for someone or something.",
        "examples": [
            "Can't get into waiting list",
            "There are huge waitlists for spaces, I can't find spots for my younger children",
            "Cuts to resources, daycare centre considering not participating anymore because can't afford to keep running",
            "We did not qualify the second year because we had financial difficulties and had to cash in our RSVPs so it looked like our yearly income far exceeded the  maximum income for the rebate"
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
        "description": "Any instances where parents feel a sense of connection or pleasure. ",
        "examples": [
            "Daycare costs are lower, allowing us to spend more money on paying down our mortgage, increase retirement savings, etc.",
            "It gives a children a good start in life",
            "More money",
            "It cut my daycare cost in half",
            "My baby's daycare is subsidised and this is a great relief to us"
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
        "description": "Any instances where parents encounter sudden and unexpected changes/occurrences.",
        "examples": [
            "This is the first time I have ever seen a few episodes of",
            "my fees are $183 a month which is unheard of from my friends in Ontario"
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
        "description": "Any instances where parents state information without evidence of emotion.",
        "examples": [
            "nothing", 
            "Staff shortages.",
            "Space",
            "I have heard from parents that there is a long waiting list to the program.",
            "Cost of living"
        ],
        "chain_of_thought": """
            To classify the excerpt as neutral, ensure the following conditions are met:

            1. **Lack of Emotional Expression:** The parent does not express any clear emotion. The tone is factual, objective, or informational.

            2. **Focus on Facts:** The excerpt focuses on providing information, stating facts, or asking questions without expressing personal feelings or opinions.

            3. **Language Clues:** The excerpt lacks any words or phrases typically associated with specific emotions or is incomprehensible (i.e., missing words such as the subject/object of the sentence).
        """
    }
}