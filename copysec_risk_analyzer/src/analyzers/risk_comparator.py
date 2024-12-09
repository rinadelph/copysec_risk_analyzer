"""Risk factor comparison utilities"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from openai import OpenAI
from copysec_risk_analyzer.config.ai_config import (
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)

class RiskComparator:
    """Compare risk factors between years"""
    
    def __init__(self):
        self.client = OpenAI()
    
    def compare_years(self, ticker: str, year1: str, year2: str, base_path: Path) -> Optional[Dict]:
        """Compare risk factors between two years"""
        try:
            # Load risk factors for both years
            rf1 = self._load_risk_factors(base_path / ticker / year1)
            rf2 = self._load_risk_factors(base_path / ticker / year2)
            
            if not rf1 or not rf2:
                logger.error("Could not load risk factors for comparison")
                return None
            
            # Calculate similarity score
            similarity = self._calculate_similarity(rf1['content'], rf2['content'])
            
            # Get AI analysis
            analysis = self._analyze_changes(
                current_text=rf1['content'],
                previous_text=rf2['content'],
                ticker=ticker,
                current_year=year1,
                previous_year=year2
            )
            
            if not analysis:
                return None
            
            # Combine results
            result = {
                'ticker': ticker,
                'current_year': year1,
                'previous_year': year2,
                'similarity_score': similarity,
                'analysis': analysis,
                'comparison_timestamp': datetime.now().isoformat(),
                'metadata': {
                    'current_word_count': rf1['word_count'],
                    'previous_word_count': rf2['word_count'],
                    'word_count_change': rf1['word_count'] - rf2['word_count']
                }
            }
            
            # Save comparison results
            output_path = base_path / ticker / year1 / 'risk_comparison.json'
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=4)
            
            return result
            
        except Exception as e:
            logger.error(f"Error comparing risk factors: {e}")
            return None
    
    def _load_risk_factors(self, year_path: Path) -> Optional[Dict]:
        """Load risk factors from a specific year"""
        try:
            rf_path = year_path / 'risk_factors.json'
            if not rf_path.exists():
                logger.error(f"Risk factors file not found: {rf_path}")
                return None
                
            with open(rf_path, 'r') as f:
                data = json.load(f)
                
            # Combine all risk factors into one text
            content = "\n\n".join(f"{r['title']}\n{r['text']}" for r in data['risk_factors'])
            word_count = sum(r['word_count'] for r in data['risk_factors'])
            
            return {
                'content': content,
                'word_count': word_count
            }
                
        except Exception as e:
            logger.error(f"Error loading risk factors: {e}")
            return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity score"""
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    def _analyze_changes(self, current_text: str, previous_text: str, 
                        ticker: str, current_year: str, previous_year: str) -> Optional[Dict]:
        """Use OpenAI to analyze changes in risk factors"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                        ticker=ticker,
                        curr_year=current_year,
                        prev_year=previous_year,
                        curr_risks=current_text,
                        prev_risks=previous_text
                    )}
                ]
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return None