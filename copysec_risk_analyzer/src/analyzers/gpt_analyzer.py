"""GPT-based risk factor analysis"""
import logging
from pathlib import Path
from typing import Dict, Optional
from openai import OpenAI
from copysec_risk_analyzer.config.ai_config import OPENAI_MODEL

logger = logging.getLogger(__name__)

class GPTAnalyzer:
    """Analyze risk factors using GPT-4"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def analyze_changes(self, current_file: Path, previous_file: Path) -> Optional[Dict]:
        """Compare risk factors between years using GPT-4"""
        try:
            # Read the cleaned risk sections
            with open(current_file, 'r', encoding='utf-8') as f:
                current_risks = f.read()
            with open(previous_file, 'r', encoding='utf-8') as f:
                previous_risks = f.read()
                
            # Create analysis prompt
            prompt = f"""You are an expert financial analyst specializing in SEC risk factor analysis.
            
Task: Analyze the changes in risk factor disclosures between two consecutive years' 10-K filings.

Current Year Risk Factors:
{current_risks}

Previous Year Risk Factors:
{previous_risks}

Provide a detailed analysis in the following JSON format:
{{
    "risk_changes": [
        {{
            "risk_area": "Name of risk area",
            "change_type": "new|removed|modified|unchanged",
            "severity_change": "increased|decreased|unchanged",
            "description": "Detailed description of the change",
            "significance": "high|medium|low",
            "implications": "Business implications of this change"
        }}
    ],
    "key_findings": {{
        "major_changes": ["List of most significant changes"],
        "emerging_risks": ["New risks that have emerged"],
        "reduced_risks": ["Risks that have decreased in severity"],
        "persistent_concerns": ["Ongoing significant risks"]
    }},
    "overall_assessment": {{
        "risk_trend": "increasing|decreasing|stable",
        "confidence": "high|medium|low",
        "summary": "Brief summary of overall risk profile changes"
    }}
}}

Focus on material changes that could significantly impact the business. Identify shifts in:
1. Strategic risks
2. Operational risks
3. Financial risks
4. Regulatory risks
5. Market risks
6. Technology risks
7. Competitive risks"""

            # Get analysis from GPT-4
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst specializing in SEC risk factor analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={ "type": "json_object" },
                temperature=0.2
            )
            
            # Extract and return the analysis
            analysis = response.choices[0].message.content
            logger.info("Successfully analyzed risk factors with GPT-4")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing risk factors with GPT-4: {e}")
            return None 