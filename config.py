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
        "description": "Any instance where parents feel blocked from pursuing a goal and/or are treated unfairly.",
        "examples": [
            "i still pay 100% of the daycare fee per month regardless of whether my child attends daycare, and because of the setting, my child is sick at least for 1x week every month and my subsidy then gets reduced so it costs me more money when my child isn't even there", 
            "There is an extreme lack of availability for childcare in Ontario. To the point of where I am currently intending to change professions to become a childcare provider.",
            "It’s SO hard to get a spot. The wait list I’m on is 2 years!",
            "EXTREMELY difficult to find childcare. Me finding it was a total fluke."
        ],
        "chain_of_thought": """
            The excerpt is likely an expression of anger if the parent:
            1) exhibits emotions/behaviours that range dissatisfaction to strong forceful language/threats, or
            2) is triggered by one or more of the following: deliberate interference, injustice, an attempt to physically/psychologically hurt us or someone we love, someone else's anger, betrayal/abandonment/rejection, or observing someone breaking a law/rule. 
        """,

    },
    "fear": {
        "description": "Any instance where parents feel the threat of physical, emotional, or psychological harm (real or imagined).",
        "examples": [
            "Very difficult to get into daycares that are decent. Demand has shot up and wait lists are years long. We don’t know what we will do for our youngest child when we need it",
            "Worried that there will be such shortage of good quality childcare because of the influx of children.",
            "Teachers are not as attentive to my child. Complaints about the lower standard of care."
            ],
        "chain_of_thought": """
            The excerpt is likely an expression of fear if the parent:
            1) exhibits emotions/behaviours from worrying about the future to a sense of helplessness from threats, or
            2) is triggered by being afraid of a threat to the physical, emotional, or psychological well-being of themselves/others
        """
    },
    "disgust": {
        "description": "Any instances where parents feel aversion towards something offensive or socially/morally reprehensible (i.e., perceived with physical senses, actions of others, or ideas).",
        "examples": [
            "The arrangement is too confusing",
            "It’s too repetitive and people take advantage of it too much",
            "I dont trust child care facility owners. The ones I've heard of are cheap and cut corners and treat their employees terrible.",
            "Government programs always suck"
        ],
        "chain_of_thought": """
            The excerpt is likely an expression of disgust if the parent:
            1) exhibits emotions/behaviours from mild dislike to strong moral judgement and intense loathing, or
            2) is triggered by aversive/repulsive/toxic objects or perceived perversions or actions of other people
        """
    },
    "sadness": {
        "description": "Any instances where parents feel disappointment and longing or a sense of loss for someone or something.",
        "examples": [
            "Can't get into waiting list",
            "There are huge waitlists for spaces, I can't find spots for my younger children",
            "Can't find daycare for this price",
            "Cuts to resources, daycare centre considering not participating anymore because can't afford to keep running"
        ],
        "chain_of_thought": """
            The excerpt is likely an expression of sadness if the parent:
            1) exhibits emotions/behaviours that range from mild disappointment to longing for something missing to extreme despair or anguish, or
            2) is triggered by the loss of a valued person, object, or expectation (e.g., rejection, endings, sickness/death, transitions, unexpected/disappointing outcomes)
        """
    },
    "enjoyment": {
        "description": "Any instances where parents feel a sense of connection or pleasure. ",
        "examples": [
            "It’s quality child care program provide my children with opportunities for socialisation, cognitive development and early learning experiences"
            "It gives a children a good start in life",
            "More money",
            "It cut my daycare cost in half",
            "My baby's daycare is subsidised and this is a great relief to us"
        ],
        "chain_of_thought": """
           The excerpt is likely an expression of enjoyment if the parent:
           1) exhibits emotions/behaviours that range from pleasurable states of peace to ecstasy (i.e., often illustrated by positive language such as 'love' or 'great'), or
           2) is triggered by the senses, witnessing acts of goodness/kindness/compassion, relief from suffering, achievement by self/others, experiencing something beautiful/surprising/amazing, or feeling connected (i.e., to oneself, others, places, animals, nature, or a cause/spirit/religion)
        """
    },
    "surprise": {
        "description": "Any instances where parents encounter sudden and unexpected changes/occurrences.",
        "examples": [
            "This is the first time I have ever seen a few episodes of",
            "my fees are $183 a month which is unheard of from my friends in Ontario"
        ],
        "chain_of_thought": """
            The excerpt is likely an expression of surprise if the parent:
            1) exhibits emotions/behaviours of the sensation of a sudden change (i.e., before one figures out what is occurring) that may quickly transition into another emotion, or
            2) is triggered by sudden or unexpected sounds, movements, or events
        """
    },
    "neutral": {
        "description": "Any instances where parents state information without evidence of emotion.",
        "examples": [
            "not enough spaces", 
            "Staff shortages."
        ],
        "chain_of_thought": """
            The excerpt is likely an expression of surprise if the parent:
            1) provides factual information or observations, lacking any clear emotional tone, or
            2) is not triggered by or expresses any personal feelings, opinions, or judgements about the situation
        """
    }
}