import json
from pathlib import Path
from copysec_risk_analyzer.src.analyzers.risk_comparator import RiskComparator
from copysec_risk_analyzer.config.config import RAW_DATA_DIR
from typing import Dict

def display_analysis(analysis: Dict):
    """Display the analysis results in a readable format"""
    print("\nStructural Changes:")
    print("=" * 80)
    for change in analysis['structural_analysis']['organization_changes']:
        print(f"\n• {change['type'].title()} in {change['location']}")
        print(f"  Description: {change['description']}")
        print(f"  Significance: {change['significance']}")

    print("\nMetrics:")
    print("=" * 80)
    metrics = analysis['structural_analysis']['metrics']
    print(f"Paragraph Changes: {metrics['paragraph_changes']}")
    print(f"Complexity Shifts: {metrics['complexity_shifts']}")
    print(f"Section Reorganization: {metrics['section_reorganization']}")

    print("\nMajor Content Changes:")
    print("=" * 80)
    for mod in analysis['content_changes']['major_modifications']:
        print(f"\n• {mod['topic']}")
        print(f"  Change: {mod['change_type']}")
        print(f"  Implications: {mod['potential_implications']}")

    print("\nSentiment Shifts:")
    print("=" * 80)
    for shift in analysis['content_changes']['sentiment_shifts']:
        print(f"\n• {shift['risk_area']}")
        print(f"  Direction: {shift['direction']}")
        print(f"  Significance: {shift['significance']}")

    print("\nKey Findings:")
    print("=" * 80)
    findings = analysis['key_findings']
    print("\nEmerging Threats:")
    for threat in findings['emerging_threats']:
        print(f"- {threat}")
    print("\nUnderlying Challenges:")
    for challenge in findings['underlying_challenges']:
        print(f"- {challenge}")
    print("\nRecommended Focus Areas:")
    for focus in findings['recommended_focus']:
        print(f"- {focus}")

def test_risk_comparison():
    comparator = RiskComparator()
    
    # Test with Apple Inc.
    ticker = "AAPL"
    current_year = "2024-11-01"
    previous_year = "2023-11-03"
    
    print(f"\n{'='*80}")
    print(f"Comparing risk factors for {ticker}")
    print(f"Current Year: {current_year}")
    print(f"Previous Year: {previous_year}")
    print(f"{'='*80}\n")
    
    result = comparator.compare_years(
        ticker=ticker,
        year1=current_year,
        year2=previous_year,
        base_path=RAW_DATA_DIR
    )
    
    if result:
        print("\nComparison Results:")
        print(f"Similarity Score: {result['similarity_score']:.2%}")
        print(f"Word Count Change: {result['metadata']['word_count_change']:+,} words")
        
        print("\nDetailed Analysis:")
        display_analysis(json.loads(result['analysis']))
        
        print(f"\nResults saved to: {RAW_DATA_DIR}/{ticker}/{current_year}/risk_comparison.json")
    else:
        print("Comparison failed")

if __name__ == "__main__":
    test_risk_comparison() 