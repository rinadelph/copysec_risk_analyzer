"""Risk factor analysis utilities"""
import json
import logging
from datetime import datetime
from typing import Dict, List
from openai import OpenAI
from copysec_risk_analyzer.config.ai_config import (
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """Analyze changes in risk factors between years"""
    
    def __init__(self):
        self.client = OpenAI()
    
    def compare_years(self, current_year: Dict, previous_year: Dict) -> Dict:
        """Compare risk factors between years and generate analysis"""
        try:
            # Basic statistical comparison
            stats = self._compare_statistics(current_year, previous_year)
            
            # Detailed content analysis
            content_changes = self._analyze_content_changes(
                current_year['risk_factors'],
                previous_year['risk_factors']
            )
            
            # AI-powered analysis
            ai_analysis = self._get_ai_analysis(
                current_year['risk_factors'],
                previous_year['risk_factors']
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'statistics': stats,
                'content_changes': content_changes,
                'ai_analysis': ai_analysis
            }
            
        except Exception as e:
            logger.error(f"Error comparing years: {e}")
            return None
    
    def _compare_statistics(self, current: Dict, previous: Dict) -> Dict:
        """Compare basic statistics between years"""
        return {
            'total_risks_change': len(current['risk_factors']) - len(previous['risk_factors']),
            'word_count_change': sum(r['word_count'] for r in current['risk_factors']) - 
                               sum(r['word_count'] for r in previous['risk_factors']),
            'current_year': {
                'total_risks': len(current['risk_factors']),
                'total_words': sum(r['word_count'] for r in current['risk_factors']),
                'avg_words_per_risk': sum(r['word_count'] for r in current['risk_factors']) / 
                                    len(current['risk_factors'])
            },
            'previous_year': {
                'total_risks': len(previous['risk_factors']),
                'total_words': sum(r['word_count'] for r in previous['risk_factors']),
                'avg_words_per_risk': sum(r['word_count'] for r in previous['risk_factors']) / 
                                    len(previous['risk_factors'])
            }
        }
    
    def _analyze_content_changes(self, current_risks: List[Dict], previous_risks: List[Dict]) -> Dict:
        """Analyze specific changes in risk factor content"""
        # Match risk factors between years using similarity
        matched_risks = self._match_risk_factors(current_risks, previous_risks)
        
        # Analyze changes for each matched pair
        changes = []
        for curr, prev in matched_risks:
            if curr and prev:  # Modified risk
                similarity = self._calculate_similarity(curr['text'], prev['text'])
                changes.append({
                    'type': 'modified',
                    'similarity': similarity,
                    'current_summary': curr['title'],
                    'previous_summary': prev['title'],
                    'word_count_change': curr['word_count'] - prev['word_count']
                })
            elif curr:  # New risk
                changes.append({
                    'type': 'added',
                    'summary': curr['title'],
                    'word_count': curr['word_count']
                })
            else:  # Removed risk
                changes.append({
                    'type': 'removed',
                    'summary': prev['title'],
                    'word_count': prev['word_count']
                })
        
        return {
            'changes': changes,
            'summary': {
                'total_changes': len(changes),
                'added': len([c for c in changes if c['type'] == 'added']),
                'removed': len([c for c in changes if c['type'] == 'removed']),
                'modified': len([c for c in changes if c['type'] == 'modified'])
            }
        }
    
    def _match_risk_factors(self, current_risks: List[Dict], previous_risks: List[Dict]) -> List[tuple]:
        """Match risk factors between years based on similarity"""
        matches = []
        used_prev = set()
        
        # For each current risk, find best match in previous risks
        for curr in current_risks:
            best_match = None
            best_score = 0
            best_idx = -1
            
            for i, prev in enumerate(previous_risks):
                if i in used_prev:
                    continue
                    
                score = self._calculate_similarity(curr['text'], prev['text'])
                if score > best_score and score > 0.7:  # 70% similarity threshold
                    best_score = score
                    best_match = prev
                    best_idx = i
            
            if best_match:
                matches.append((curr, best_match))
                used_prev.add(best_idx)
            else:
                matches.append((curr, None))  # New risk
        
        # Add remaining unmatched previous risks
        for i, prev in enumerate(previous_risks):
            if i not in used_prev:
                matches.append((None, prev))  # Removed risk
        
        return matches
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity score"""
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    def _get_ai_analysis(self, current_risks: List[Dict], previous_risks: List[Dict]) -> Dict:
        """Get AI-powered analysis of risk changes"""
        try:
            # Format risks for comparison
            curr_text = "\n\n".join(f"{r['title']}\n{r['text']}" for r in current_risks)
            prev_text = "\n\n".join(f"{r['title']}\n{r['text']}" for r in previous_risks)
            
            # Get AI analysis
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                        curr_risks=curr_text,
                        prev_risks=prev_text
                    )}
                ]
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return {
                "error": str(e),
                "summary": "AI analysis failed",
                "key_insights": ["Analysis error occurred"]
            }