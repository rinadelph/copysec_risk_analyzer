import json
from pathlib import Path
from copysec_risk_analyzer.src.analyzers.gpt_analyzer import GPTAnalyzer

def test_risk_factor_analysis():
    analyzer = GPTAnalyzer()
    
    # Load current and previous risk factors
    current_year = "2024-11-01"
    previous_year = "2023-11-03"
    ticker = "AAPL"
    
    base_path = Path("data/raw") / ticker
    
    # Load current year risk factors
    current_rf_path = base_path / current_year / "risk_factors.json"
    with open(current_rf_path, 'r') as f:
        current_rf = json.load(f)
    
    # Load previous year risk factors
    previous_rf_path = base_path / previous_year / "risk_factors.json"
    with open(previous_rf_path, 'r') as f:
        previous_rf = json.load(f)
    
    # Analyze changes
    analysis = analyzer.analyze_risk_factors(
        current_rf['content'],
        previous_rf['content']
    )
    
    if analysis:
        print("\nRisk Factor Analysis Results:")
        print("=" * 80)
        print(json.dumps(analysis, indent=2))
        
        # Save analysis results
        analysis_path = base_path / current_year / "risk_analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=4)
            
        print(f"\nAnalysis saved to: {analysis_path}")
    else:
        print("Analysis failed")

if __name__ == "__main__":
    test_risk_factor_analysis() 