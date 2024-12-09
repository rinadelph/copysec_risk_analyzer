"""OpenAI configuration settings"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-1106-preview"  # GPT-4 Turbo
OPENAI_TEMPERATURE = 0.7

# Prompts
SYSTEM_PROMPT = """You are an expert financial analyst specializing in risk assessment."""

USER_PROMPT_TEMPLATE = """Compare the following risk factors from {ticker}'s 10-K filings.

Previous Year ({prev_year}):
{prev_risks}

Current Year ({curr_year}):
{curr_risks}

Analyze the changes in risk factors between these years. Focus on:
1. New risks that have emerged
2. Risks that have been removed
3. Changes in existing risks
4. Overall shifts in risk emphasis

Provide your analysis in JSON format with the following structure:
{
    "structural_analysis": {
        "organization_changes": [
            {
                "type": "addition|removal|modification",
                "location": "section or area affected",
                "description": "what changed",
                "significance": "high|medium|low"
            }
        ],
        "metrics": {
            "paragraph_changes": "number of changed paragraphs",
            "complexity_shifts": "increased|decreased|unchanged",
            "section_reorganization": "extensive|moderate|minimal"
        }
    },
    "content_changes": {
        "major_modifications": [
            {
                "topic": "risk area",
                "change_type": "intensified|reduced|reframed",
                "potential_implications": "business impact"
            }
        ],
        "sentiment_shifts": [
            {
                "risk_area": "specific risk",
                "direction": "more|less severe",
                "significance": "high|medium|low"
            }
        ]
    },
    "key_findings": {
        "emerging_threats": ["list of new threats"],
        "underlying_challenges": ["list of persistent issues"],
        "recommended_focus": ["areas needing attention"]
    }
}"""