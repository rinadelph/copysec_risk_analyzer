"""SEC risk factor analysis script"""
import logging
from pathlib import Path
import yfinance as yf
from datetime import datetime
from copysec_risk_analyzer.src.extractors.text_extractor import TextExtractor
from copysec_risk_analyzer.src.analyzers.gpt_analyzer import GPTAnalyzer
from copysec_risk_analyzer.config.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_company_risks():
    """Main function to analyze company risk factors"""
    print("\n=== Risk Analysis ===\n")
    
    # Get company ticker
    ticker = input("Enter ticker to analyze: ").strip().upper()
    logger.info(f"Starting analysis for {ticker}")
    
    # Verify company
    print(f"\nSearching for {ticker}...")
    try:
        company = yf.Ticker(ticker)
        info = company.info
        logger.info(f"Company found: {info['longName']}")
        
        print("\nCompany Found:")
        print(f"Name: {info['longName']}")
        print(f"Industry: {info.get('industry', 'N/A')}")
        print(f"Sector: {info.get('sector', 'N/A')}")
        print(f"Market Cap: ${info.get('marketCap', 0):,.2f}")
        
    except Exception as e:
        logger.error(f"Error finding company: {e}")
        print("Could not verify company. Please try again.")
        return
    
    # Initialize extractors and analyzers
    extractor = TextExtractor()
    analyzer = GPTAnalyzer()
    
    # Step 1: Download 10-K filings
    print("\nFetching SEC filings...")
    logger.info(f"Found CIK number for {ticker}")
    
    # Get available years
    current_year = datetime.now().year
    available_years = []
    
    for year in range(current_year, current_year - 3, -1):
        filing = extractor.download_10k(ticker, str(year))
        if filing:
            available_years.append(str(year))
    
    if len(available_years) < 2:
        logger.error(f"Not enough 10-K filings found for {ticker}")
        print("\nCould not find enough 10-K filings for analysis")
        return
    
    logger.info(f"Found {len(available_years)} years with 10-K filings for {ticker}")
    print(f"\nAvailable years for comparison:")
    for i, year in enumerate(available_years, 1):
        print(f"{i}. {year}")
    
    # Get years to compare
    while True:
        try:
            years = input("\nSelect two years to compare (e.g., '1 2' for first and second years): ")
            idx1, idx2 = map(int, years.split())
            if 1 <= idx1 <= len(available_years) and 1 <= idx2 <= len(available_years) and idx1 != idx2:
                year1, year2 = available_years[idx1-1], available_years[idx2-1]
                break
        except:
            print("Invalid input. Please try again.")
    
    logger.info(f"User selected years {year1} and {year2} for comparison")
    
    # Step 2: Extract risk sections
    print(f"\nAnalyzing risk factors between {year1} and {year2}...")
    
    # Get filings
    filing1 = extractor.download_10k(ticker, year1)
    filing2 = extractor.download_10k(ticker, year2)
    
    if not filing1 or not filing2:
        logger.error("Could not download both 10-K filings")
        print("\nError downloading 10-K filings")
        return
    
    # Extract risk sections
    section1 = extractor.extract_risk_section(filing1)
    section2 = extractor.extract_risk_section(filing2)
    
    if not section1 or not section2:
        logger.error("Could not extract risk sections")
        print("\nError extracting risk sections")
        return
    
    # Clean risk sections
    clean1 = extractor.clean_risk_section(section1)
    clean2 = extractor.clean_risk_section(section2)
    
    if not clean1 or not clean2:
        logger.error("Could not clean risk sections")
        print("\nError cleaning risk sections")
        return
    
    # Step 3: Analyze with GPT-4
    print("\nAnalyzing changes with GPT-4...")
    analysis = analyzer.analyze_changes(clean1, clean2)
    
    if not analysis:
        logger.error("Could not analyze risk factors")
        print("\nError analyzing risk factors")
        return
    
    # Step 4: Display results
    print("\nAnalysis Results:")
    print("=" * 80)
    
    try:
        # Parse and display the analysis in a readable format
        analysis_dict = json.loads(analysis)
        
        # Overall assessment
        overall = analysis_dict['overall_assessment']
        print(f"\nOverall Risk Trend: {overall['risk_trend'].title()}")
        print(f"Confidence: {overall['confidence'].title()}")
        print(f"\nSummary: {overall['summary']}")
        
        # Key findings
        findings = analysis_dict['key_findings']
        print("\nKey Findings:")
        print("\nMajor Changes:")
        for change in findings['major_changes']:
            print(f"- {change}")
        
        print("\nEmerging Risks:")
        for risk in findings['emerging_risks']:
            print(f"- {risk}")
        
        print("\nReduced Risks:")
        for risk in findings['reduced_risks']:
            print(f"- {risk}")
        
        # Detailed risk changes
        print("\nDetailed Risk Changes:")
        for risk in analysis_dict['risk_changes']:
            print(f"\nRisk Area: {risk['risk_area']}")
            print(f"Change Type: {risk['change_type'].title()}")
            print(f"Severity Change: {risk['severity_change'].title()}")
            print(f"Significance: {risk['significance'].title()}")
            print(f"Description: {risk['description']}")
            print(f"Implications: {risk['implications']}")
        
    except Exception as e:
        logger.error(f"Error displaying analysis: {e}")
        print("\nError displaying analysis results")
        return
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_company_risks() 