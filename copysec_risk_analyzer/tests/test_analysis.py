import json
from pathlib import Path
from copysec_risk_analyzer.src.analyzers.gpt_analyzer import GPTAnalyzer
from copysec_risk_analyzer.config.config import RAW_DATA_DIR

def test_full_analysis():
    """Test complete risk factor extraction and analysis"""
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    # First, verify we have the complete risk sections
    print("\nVerifying Risk Section Extraction:")
    print("=" * 80)
    
    risk_sections = {}
    for year in years:
        file_path = RAW_DATA_DIR / ticker / year / "risk_factors.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                risk_sections[year] = data
                print(f"\n{year}:")
                print(f"Total risks: {data['metadata']['total_risks']}")
                print(f"Total words: {data['metadata']['total_words']:,}")
                print(f"First risk preview: {data['risk_factors'][0]['header'][:200]}...")
    
    if len(risk_sections) == 2:
        print("\nAnalyzing Changes with GPT O1:")
        print("=" * 80)
        
        analyzer = GPTAnalyzer()
        analysis = analyzer.analyze_risk_factors(
            current_year_risks=risk_sections[years[0]]['risk_factors'],
            previous_year_risks=risk_sections[years[1]]['risk_factors']
        )
        
        if analysis:
            print("\nAnalysis Results:")
            print(json.dumps(analysis, indent=2))
        else:
            print("Analysis failed")

if __name__ == "__main__":
    test_full_analysis() 