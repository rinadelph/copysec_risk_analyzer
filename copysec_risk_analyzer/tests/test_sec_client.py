import logging
import json
from datetime import datetime
from pathlib import Path
from copysec_risk_analyzer.src.collectors.sec_client import SECClient
from pprint import pprint

def test_full_pipeline():
    client = SECClient()
    
    # Test with Apple Inc.
    ticker = "AAPL"
    
    print(f"\n{'='*80}")
    print(f"Testing full pipeline for {ticker}")
    print(f"{'='*80}\n")
    
    # Get and save the latest 10-K with risk factors
    result = client.get_and_save_latest_10k(ticker)
    
    if result:
        print("\nDownload Summary:")
        print(f"Filing Date: {result.get('filing_date')}")
        print(f"Document: {result.get('primary_doc')}")
        print(f"File Size: {result.get('size'):,} bytes")
        
        # Check if risk factors were extracted
        if result.get('risk_factors_extracted'):
            print(f"\nRisk Factors Extracted: Yes")
            print(f"Word Count: {result.get('risk_factors_word_count'):,} words")
            
            # Read and display part of the risk factors
            save_path = Path(result.get('ticker')) / result.get('filing_date')
            risk_factors_path = save_path / 'risk_factors.json'
            
            if risk_factors_path.exists():
                with open(risk_factors_path, 'r') as f:
                    risk_data = json.load(f)
                    
                print("\nRisk Factors Preview:")
                print(f"Section Title: {risk_data.get('section_title')}")
                print("\nFirst 500 characters of content:")
                print("-" * 80)
                print(risk_data.get('content', '')[:500])
                print("-" * 80)
        else:
            print("\nRisk Factors Extracted: No")
        
        # Show file locations
        print("\nSaved Files:")
        print(f"Main Document: {result.get('primary_doc')}")
        print(f"Metadata: metadata.json")
        if result.get('risk_factors_extracted'):
            print(f"Risk Factors: risk_factors.json")
            
    else:
        print("Failed to process 10-K filing")

def test_multiple_companies():
    """Test the pipeline with multiple companies"""
    companies = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
    
    print(f"\n{'='*80}")
    print(f"Testing multiple companies")
    print(f"{'='*80}\n")
    
    client = SECClient()
    
    for ticker in companies:
        print(f"\nProcessing {ticker}...")
        result = client.get_and_save_latest_10k(ticker)
        
        if result:
            print(f"Success - Filing Date: {result.get('filing_date')}")
            print(f"Risk Factors Extracted: {result.get('risk_factors_extracted')}")
            if result.get('risk_factors_extracted'):
                print(f"Risk Factor Word Count: {result.get('risk_factors_word_count'):,}")
        else:
            print(f"Failed to process {ticker}")
        print("-" * 40)

def test_historical_filings():
    """Test retrieving and processing multiple years of filings"""
    client = SECClient()
    
    # Test with Apple Inc.
    ticker = "AAPL"
    
    print(f"\n{'='*80}")
    print(f"Testing historical filings for {ticker}")
    print(f"{'='*80}\n")
    
    results = client.get_historical_filings(ticker)
    
    if results:
        print(f"\nProcessed {len(results)} filings:")
        for result in results:
            print(f"\nFiling Date: {result['filing_date']}")
            print(f"Risk Factors Extracted: {result['risk_factors_extracted']}")
            if result['risk_factors_extracted']:
                rf_path = RAW_DATA_DIR / ticker / result['filing_date'] / 'risk_factors.json'
                with open(rf_path, 'r') as f:
                    rf_data = json.load(f)
                print(f"Word Count: {rf_data['word_count']:,}")
    else:
        print("Failed to process filings")

if __name__ == "__main__":
    # Test single company in detail
    test_full_pipeline()
    
    # Uncomment to test multiple companies
    # test_multiple_companies() 
    
    test_historical_filings()