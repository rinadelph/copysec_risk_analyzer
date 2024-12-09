"""Text extraction utilities for SEC filings"""
import re
import logging
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup, Comment
from typing import Optional, List, Dict, Tuple
import time

from copysec_risk_analyzer.config.config import RAW_DATA_DIR

logger = logging.getLogger(__name__)

class TextExtractor:
    """Extract and process text from SEC filings"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Luis Rincon (lrincon2019@gmail.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def download_10k(self, ticker: str, year: str) -> Optional[Path]:
        """Download 10-K filing for a specific year"""
        try:
            # Get CIK number
            cik = self._get_cik_number(ticker)
            if not cik:
                logger.error(f"Could not find CIK for {ticker}")
                return None
            
            # Add leading zeros to make it 10 digits
            cik = cik.zfill(10)
            
            # Get filing info
            filing_info = self._get_filing_info(cik, year)
            if not filing_info:
                logger.error(f"Could not find 10-K filing for {ticker} in {year}")
                return None
            
            filing_date, accession_number = filing_info
            
            # Create directory structure
            filing_dir = RAW_DATA_DIR / ticker / filing_date
            filing_dir.mkdir(parents=True, exist_ok=True)
            
            # Define file paths
            html_file = filing_dir / f"{ticker.lower()}-{filing_date}.htm"
            
            # Check if already downloaded
            if html_file.exists():
                logger.info(f"Using cached filing: {html_file}")
                return html_file
            
            # Download filing
            url = self._get_filing_url(cik, accession_number)
            logger.info(f"Downloading 10-K from {url}")
            
            # Add delay to comply with SEC rate limits
            time.sleep(0.1)  # 100ms delay between requests
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save HTML file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logger.info(f"Saved 10-K HTML to {html_file}")
            return html_file
            
        except Exception as e:
            logger.error(f"Error downloading 10-K: {e}")
            return None
    
    def _get_cik_number(self, ticker: str) -> Optional[str]:
        """Get CIK number for a ticker"""
        try:
            # First try the company tickers endpoint
            time.sleep(0.1)  # Rate limit
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            companies = response.json()
            for entry in companies.values():
                if entry['ticker'] == ticker.upper():
                    cik = str(entry['cik_str']).zfill(10)
                    logger.info(f"Found CIK {cik} for {ticker}")
                    return cik
            
            # If not found, try the company search endpoint
            time.sleep(0.1)  # Rate limit
            search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany&output=atom"
            logger.info(f"Trying company search: {search_url}")
            
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse XML response
            soup = BeautifulSoup(response.text, 'xml')
            company = soup.find('company-info')
            
            if company:
                cik = company.find('cik').text.zfill(10)
                logger.info(f"Found CIK {cik} for {ticker} using company search")
                return cik
            
            logger.error(f"Could not find CIK for {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting CIK number: {e}")
            return None
    
    def _get_filing_info(self, cik: str, year: str) -> Optional[Tuple[str, str]]:
        """Get filing date and accession number for 10-K"""
        try:
            # Add delay to comply with SEC rate limits
            time.sleep(0.1)  # 100ms delay between requests
            
            # Format CIK with exactly 10 digits
            cik_padded = str(int(cik)).zfill(10)
            
            # Use the EDGAR REST API
            url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
            logger.info(f"Fetching filing info from {url}")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            
            if not filings:
                logger.error("No filings found in response")
                return None
            
            # Find 10-K for the year
            forms = filings.get('form', [])
            dates = filings.get('filingDate', [])
            accessions = filings.get('accessionNumber', [])
            
            target_year = int(year)
            
            for i, (form, date) in enumerate(zip(forms, dates)):
                filing_year = int(date.split('-')[0])
                if form == '10-K' and filing_year == target_year:
                    logger.info(f"Found 10-K filing from {date}")
                    return date, accessions[i]
            
            # If not found in recent filings, try alternative API
            alt_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_padded}&type=10-K&dateb={target_year}-12-31&datea={target_year}-01-01&owner=exclude&count=10&output=atom"
            logger.info(f"Trying alternative API: {alt_url}")
            
            time.sleep(0.1)  # Rate limit
            response = requests.get(alt_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse XML response
            soup = BeautifulSoup(response.text, 'xml')
            entries = soup.find_all('entry')
            
            for entry in entries:
                filing_date = entry.find('filing-date').text
                filing_year = int(filing_date.split('-')[0])
                if filing_year == target_year:
                    accession = entry.find('accession-number').text
                    logger.info(f"Found 10-K filing from {filing_date} using alternative API")
                    return filing_date, accession
            
            logger.error(f"No 10-K filing found for {year}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting filing info: {e}")
            return None
    
    def _get_filing_url(self, cik: str, accession: str) -> str:
        """Generate URL for filing document"""
        # Format CIK without leading zeros for the URL
        cik_int = int(cik)
        # Format: 0000320193-23-000070 -> 000032019323000070
        accession_clean = accession.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/{accession}.txt"
    
    def extract_risk_section(self, html_file: Path) -> Optional[Path]:
        """Extract risk factors section from HTML file"""
        try:
            # Define output path
            raw_section_file = html_file.parent / "raw_section.txt"
            
            # Check if already extracted
            if raw_section_file.exists():
                logger.info(f"Using cached risk section: {raw_section_file}")
                return raw_section_file
            
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove scripts, styles, and comments
            for element in soup(['script', 'style']):
                element.decompose()
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Get text content
            text = soup.get_text()
            
            # Find risk factors section
            section = self._extract_risk_section(text)
            if not section:
                logger.error("Could not find risk factors section")
                return None
            
            # Save raw section
            with open(raw_section_file, 'w', encoding='utf-8') as f:
                f.write(section)
            
            logger.info(f"Saved raw risk section to {raw_section_file}")
            return raw_section_file
            
        except Exception as e:
            logger.error(f"Error extracting risk section: {e}")
            return None
    
    def clean_risk_section(self, raw_section_file: Path) -> Optional[Path]:
        """Clean and structure the raw risk section"""
        try:
            # Define output path
            clean_section_file = raw_section_file.parent / "clean_section.txt"
            
            # Check if already cleaned
            if clean_section_file.exists():
                logger.info(f"Using cached clean section: {clean_section_file}")
                return clean_section_file
            
            # Read raw section
            with open(raw_section_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean the text
            clean_text = self._clean_text(content)
            
            # Save cleaned section
            with open(clean_section_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            logger.info(f"Saved clean risk section to {clean_section_file}")
            return clean_section_file
            
        except Exception as e:
            logger.error(f"Error cleaning risk section: {e}")
            return None
    
    def _extract_risk_section(self, text: str) -> Optional[str]:
        """Extract risk factors section from text"""
        try:
            # Find start of risk section
            start_patterns = [
                r"Item[^\n]*1A[^\n]*Risk Factors",
                r"ITEM[^\n]*1A[^\n]*RISK FACTORS",
                r"Item[^\n]*1A\.",
                r"ITEM[^\n]*1A\."
            ]
            
            start_pos = -1
            for pattern in start_patterns:
                match = re.search(pattern, text)
                if match:
                    pos = match.start()
                    if start_pos == -1 or pos < start_pos:
                        start_pos = pos
            
            if start_pos == -1:
                logger.error("Could not find start of risk section")
                return None
            
            # Find end of risk section
            end_patterns = [
                r"Item[^\n]*1B",
                r"ITEM[^\n]*1B",
                r"Item[^\n]*2",
                r"ITEM[^\n]*2"
            ]
            
            text_after_start = text[start_pos:]
            end_pos = len(text_after_start)
            
            for pattern in end_patterns:
                match = re.search(pattern, text_after_start)
                if match:
                    pos = match.start()
                    if pos < end_pos:
                        end_pos = pos
            
            # Extract section
            section = text_after_start[:end_pos].strip()
            return section if section else None
            
        except Exception as e:
            logger.error(f"Error extracting risk section: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'Table of Contents', '', text)
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        # Clean each paragraph
        clean_paragraphs = []
        for para in paragraphs:
            # Remove leading/trailing whitespace
            para = para.strip()
            
            # Skip empty paragraphs
            if not para:
                continue
            
            # Skip table of contents references
            if re.search(r'^\s*\d+\s*$', para):
                continue
            
            clean_paragraphs.append(para)
        
        # Join paragraphs with double newlines
        return '\n\n'.join(clean_paragraphs)
    
    def analyze_risk_factors(self, ticker: str) -> Optional[Dict]:
        """Analyze risk factors for a company"""
        try:
            # Get CIK number
            cik = self.sec_client.get_cik_from_ticker(ticker)
            if not cik:
                logger.error(f"Could not find CIK for {ticker}")
                return None

            logger.info(f"Found CIK {cik} for {ticker}")
            
            # Get available filings first
            filings = self.sec_client.get_company_filings(cik)
            if not filings or not filings.get('filings'):
                logger.error(f"No filings found for {ticker}")
                return None
            
            # Get all available 10-K filings
            available_filings = []
            for filing in filings['filings']:
                if filing['filing_type'] == '10-K':
                    year = filing['date'].split('-')[0]
                    available_filings.append((year, filing['accession_number']))
            
            if not available_filings:
                logger.error(f"No 10-K filings found for {ticker}")
                return None
            
            # Sort by date (newest first)
            available_filings.sort(reverse=True)
            logger.info(f"Found {len(available_filings)} 10-K filings for {ticker}")
            
            # Process available filings
            risk_factors = []
            for year, accession in available_filings:
                try:
                    # Get filing URL
                    filing_url = self.sec_client._get_filing_url(cik, accession)
                    if not filing_url:
                        continue
                    
                    # Download and process filing
                    content = self.sec_client.download_filing(filing_url)
                    if not content:
                        continue
                    
                    # Extract risk factors section
                    risk_section = self._extract_risk_section(content)
                    if risk_section:
                        risk_factors.append({
                            'year': year,
                            'content': risk_section
                        })
                except Exception as e:
                    logger.error(f"Error processing filing for {year}: {str(e)}")
                    continue
            
            if not risk_factors:
                logger.error(f"Could not extract risk factors from any filings for {ticker}")
                return None
            
            # Analyze changes in risk factors
            return self._analyze_risk_changes(risk_factors)
            
        except Exception as e:
            logger.error(f"Error analyzing risk factors: {str(e)}")
            return None