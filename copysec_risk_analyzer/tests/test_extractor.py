import json
from pathlib import Path
from copysec_risk_analyzer.src.processors.text_extractor import TextExtractor
from copysec_risk_analyzer.config.config import RAW_DATA_DIR
from bs4 import BeautifulSoup

def test_extraction():
    # Test with Apple's latest filing
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    for filing_date in years:
        print(f"\n{'='*80}")
        print(f"Testing risk factor extraction for {ticker} ({filing_date})")
        print(f"{'='*80}")
        
        # Load the HTML file
        file_name = "aapl-20240928.htm" if filing_date == "2024-11-01" else "aapl-20230930.htm"
        file_path = RAW_DATA_DIR / ticker / filing_date / file_name
        
        print(f"\nProcessing file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"File size: {len(html_content):,} bytes")
        
        # Test Stage 1: Raw Extraction
        print("\nStage 1: Raw Extraction")
        print("-" * 40)
        raw_section = TextExtractor._extract_raw_section(html_content)
        if raw_section:
            print(f"Raw extraction successful")
            print(f"Characters extracted: {len(raw_section):,}")
            print("\nFirst 200 characters of raw text:")
            print(raw_section[:200] + "...")
        else:
            print("Raw extraction failed")
            continue
        
        # Test Stage 2: Text Cleaning
        print("\nStage 2: Text Cleaning")
        print("-" * 40)
        cleaned_text = TextExtractor._clean_text(raw_section)
        if cleaned_text:
            print("Text cleaning successful")
            print(f"Characters after cleaning: {len(cleaned_text):,}")
            paragraphs = cleaned_text.split('\n\n')
            print(f"Paragraphs identified: {len(paragraphs)}")
            print("\nFirst paragraph preview:")
            print("-" * 40)
            print(paragraphs[0][:200] + "...")
            print("\nSecond paragraph preview:")
            print("-" * 40)
            print(paragraphs[1][:200] + "...")
        else:
            print("Text cleaning failed")
            print("Raw text preview:")
            print("-" * 40)
            print(raw_section[:500])
            continue
        
        # Test Stage 3: Content Processing
        print("\nStage 3: Content Processing")
        print("-" * 40)
        processed_content = TextExtractor._process_content(cleaned_text)
        if processed_content:
            print("Content processing successful")
            print(f"\nMetadata:")
            print(f"Total risks identified: {processed_content['metadata']['total_risks']}")
            print(f"Total words: {processed_content['metadata']['total_words']:,}")
            print(f"Total characters: {processed_content['metadata']['total_chars']:,}")
            
            print(f"\nFirst risk factor preview:")
            if processed_content['risk_factors']:
                first_risk = processed_content['risk_factors'][0]
                print(f"Word count: {first_risk['word_count']}")
                print(f"First 200 characters:")
                print(first_risk['text'][:200] + "...")
            
            # Save the results
            output_path = RAW_DATA_DIR / ticker / filing_date / "risk_factors.json"
            with open(output_path, 'w') as f:
                json.dump(processed_content, f, indent=4)
                
            print(f"\nResults saved to: {output_path}")
        else:
            print("Content processing failed")
        
        if raw_section:
            print("\nVerifying section content:")
            print("-" * 40)
            if verify_risk_section(raw_section):
                print("✓ Found correct risk section")
                print(f"Section length: {len(raw_section):,} characters")
            else:
                print("✗ May not be the correct section")

def compare_years():
    """Compare risk factors between years"""
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    risk_factors = {}
    
    for year in years:
        file_path = RAW_DATA_DIR / ticker / year / "risk_factors.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                risk_factors[year] = json.load(f)
    
    if len(risk_factors) == 2:
        print("\nComparison between years:")
        print("=" * 80)
        for year in years:
            rf = risk_factors[year]
            print(f"\n{year}:")
            print(f"Total risks: {rf['metadata']['total_risks']}")
            print(f"Total words: {rf['metadata']['total_words']:,}")
            
        # Show difference in number of risks
        diff = (risk_factors[years[0]]['metadata']['total_risks'] - 
                risk_factors[years[1]]['metadata']['total_risks'])
        print(f"\nChange in number of risks: {diff:+d}")
        
        # Show difference in word count
        word_diff = (risk_factors[years[0]]['metadata']['total_words'] - 
                    risk_factors[years[1]]['metadata']['total_words'])
        print(f"Change in word count: {word_diff:+,}")

def analyze_raw_file():
    """Analyze the raw HTML to verify risk section extraction"""
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    for filing_date in years:
        print(f"\n{'='*80}")
        print(f"Analyzing {ticker} ({filing_date})")
        print(f"{'='*80}")
        
        # Load the HTML file
        file_name = "aapl-20240928.htm" if filing_date == "2024-11-01" else "aapl-20230930.htm"
        file_path = RAW_DATA_DIR / ticker / filing_date / file_name
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Find the risk section boundaries
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\nSearching for Risk Section...")
        for tag in soup.find_all(['div', 'span']):
            if "Item 1A" in tag.get_text() and "Risk Factors" in tag.get_text():
                print("\nFound Risk Section Header:")
                print("-" * 40)
                print(f"Tag: {tag.name}")
                print(f"Text: {tag.get_text()[:200]}...")
                
                # Find the end of the section
                current = tag
                section_text = []
                while current:
                    current = current.find_next()
                    if not current:
                        break
                    
                    text = current.get_text(strip=True)
                    if "Item 1B" in text or "Item 2" in text:
                        print("\nFound Section End:")
                        print(f"Text: {text[:100]}...")
                        break
                        
                    if text:
                        section_text.append(text)
                
                print(f"\nTotal section length: {len(' '.join(section_text))} characters")
                print("\nFirst 500 characters of section:")
                print("-" * 40)
                print(' '.join(section_text)[:500])
                break

def verify_complete_section():
    """Verify we're getting the complete risk section"""
    ticker = "AAPL"
    years = ["2024-11-01", "2023-11-03"]
    
    for filing_date in years:
        print(f"\n{'='*80}")
        print(f"Verifying complete section for {ticker} ({filing_date})")
        print(f"{'='*80}")
        
        # Load the HTML file
        file_name = "aapl-20240928.htm" if filing_date == "2024-11-01" else "aapl-20230930.htm"
        file_path = RAW_DATA_DIR / ticker / filing_date / file_name
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract the section
        raw_section = TextExtractor._extract_raw_section(html_content)
        
        if raw_section:
            print(f"\nExtracted section length: {len(raw_section):,} characters")
            print("\nSection start:")
            print("-" * 80)
            print(raw_section[:500])
            print("\nSection end:")
            print("-" * 80)
            print(raw_section[-500:])
            
            # Save raw section for verification
            output_path = RAW_DATA_DIR / ticker / filing_date / "raw_section.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(raw_section)
            print(f"\nRaw section saved to: {output_path}")
            
            # Count potential risk factors
            risk_starts = [
                "The Company", "Global", "Future", "If the", "Changes",
                "The business", "The Company's", "There can", "The Company has"
            ]
            potential_risks = sum(1 for start in risk_starts if start in raw_section)
            print(f"\nPotential risk factors found: {potential_risks}")
        else:
            print("Failed to extract section, debugging...")
            debug_extraction(html_content)

def debug_extraction(html_content: str) -> None:
    """Debug the extraction process"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("\nSearching for risk sections...")
    candidates = []
    for tag in soup.find_all(['div', 'span']):
        text = tag.get_text(strip=True)
        if "Item 1A" in text and "Risk Factors" in text:
            content_length = len(text)
            candidates.append((tag, content_length))
            print(f"\nFound candidate (length: {content_length}):")
            print(f"Tag: {tag.name}")
            print(f"Text preview: {text[:200]}...")
    
    if candidates:
        print("\nSorting candidates by length...")
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_candidate = candidates[0][0]
        
        print(f"\nBest candidate (length: {len(best_candidate.get_text())}):")
        print(f"Tag: {best_candidate.name}")
        print(f"Text preview: {best_candidate.get_text()[:500]}...")
    else:
        print("No candidates found")

def analyze_html_structure():
    """Analyze the HTML structure of the document"""
    ticker = "AAPL"
    filing_date = "2024-11-01"
    file_name = "aapl-20240928.htm"
    file_path = RAW_DATA_DIR / ticker / filing_date / file_name
    
    print(f"\nAnalyzing HTML structure of {file_path}")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all potential risk factor sections
    print("\nSearching for risk factor markers...")
    for element in soup.find_all(string=lambda text: text and "Item 1A" in text and "Risk Factors" in text):
        print("\nFound potential section:")
        print(f"Parent tag: {element.parent.name}")
        print(f"Parent classes: {element.parent.get('class', [])}")
        print(f"Text context: {element.parent.get_text()[:200]}...")
        
        # Look at surrounding structure
        container = element.find_parent('div')
        if container:
            print("\nContainer structure:")
            print(f"Classes: {container.get('class', [])}")
            print(f"ID: {container.get('id', 'No ID')}")
            
            # Show next few siblings
            print("\nNext elements:")
            current = container.find_next_sibling()
            for _ in range(3):
                if current:
                    print(f"- {current.name}: {current.get_text()[:100]}...")
                    current = current.find_next_sibling()

def verify_risk_section(raw_section: str) -> bool:
    """Verify we got the correct risk section"""
    if not raw_section:
        return False
        
    # Check for key indicators
    indicators = [
        "The Company's business, reputation, results of operations",
        "Because of the following factors",
        "risk factors",
        "could materially affect"
    ]
    
    return all(indicator.lower() in raw_section.lower() for indicator in indicators)

if __name__ == "__main__":
    test_extraction()
    compare_years()
    analyze_raw_file()
    verify_complete_section()
    analyze_html_structure() 