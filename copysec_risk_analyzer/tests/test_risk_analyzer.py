import json
from pathlib import Path
from copysec_risk_analyzer.src.analyzers.risk_analyzer import RiskAnalyzer
from copysec_risk_analyzer.config.config import RAW_DATA_DIR

def test_risk_analysis():
    """Test risk factor analysis between years"""
    analyzer = RiskAnalyzer()
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    # Load risk factors for both years
    risk_factors = {}
    for year in years:
        file_path = RAW_DATA_DIR / ticker / year / "risk_factors.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                risk_factors[year] = json.load(f)
    
    if len(risk_factors) == 2:
        # Run analysis
        analysis = analyzer.compare_years(
            risk_factors[years[0]],  # Current year
            risk_factors[years[1]]   # Previous year
        )
        
        # Save analysis results
        output_path = RAW_DATA_DIR / ticker / "risk_analysis.json"
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Print summary
        print("\nRisk Analysis Results:")
        print("=" * 80)
        print(f"\nStatistics:")
        print(f"Total risks change: {analysis['statistics']['total_risks_change']:+d}")
        print(f"Word count change: {analysis['statistics']['word_count_change']:+,}")
        
        print(f"\nContent Changes:")
        print(f"Total changes: {analysis['content_changes']['summary']['total_changes']}")
        print(f"Added risks: {analysis['content_changes']['summary']['added']}")
        print(f"Removed risks: {analysis['content_changes']['summary']['removed']}")
        print(f"Modified risks: {analysis['content_changes']['summary']['modified']}")
        
        print(f"\nAI Analysis Summary:")
        print(f"{analysis['ai_analysis']['summary']}")
        
        print(f"\nKey Insights:")
        for insight in analysis['ai_analysis']['key_insights']:
            print(f"- {insight}")

if __name__ == "__main__":
    test_risk_analysis() 