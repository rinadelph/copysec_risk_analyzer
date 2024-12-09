import requests
import time
from typing import Optional, Dict, List
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta
import random
from copysec_risk_analyzer.config.config import SEC_BASE_URL, SEC_USER_AGENT, SEC_RATE_LIMIT, RAW_DATA_DIR, SEC_API_URL, MAX_YEARS_COMPARISON
from bs4 import BeautifulSoup
from copysec_risk_analyzer.src.processors.text_extractor import TextExtractor

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SECClient:
    def __init__(self):
        self.base_url = SEC_BASE_URL
        self.api_url = SEC_API_URL
        self.headers = {
            "User-Agent": SEC_USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        self.web_headers = {
            "User-Agent": SEC_USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self.last_request_time = 0
        self.request_count = 0
        self.window_start = time.time()
        self.max_requests_per_window = 10
        self.window_duration = 1

    def _enforce_rate_limit(self):
        """Enhanced rate limiting with safety measures"""
        current_time = time.time()
        
        # Add a small random delay (0.1 to 0.3 seconds)
        time.sleep(random.uniform(0.1, 0.3))
        
        # Check if we're in a new window
        if current_time - self.window_start >= self.window_duration:
            self.window_start = current_time
            self.request_count = 0
        
        # If we've made too many requests in this window, wait
        if self.request_count >= self.max_requests_per_window:
            sleep_time = self.window_duration - (current_time - self.window_start) + 0.1
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self.window_start = time.time()
                self.request_count = 0
        
        self.request_count += 1
        self.last_request_time = time.time()

    def _make_request(self, url: str, max_retries: int = 3, use_api: bool = False) -> Optional[requests.Response]:
        """Make a request with retry logic and error handling"""
        headers = self.headers if use_api else self.web_headers
        
        for attempt in range(max_retries):
            try:
                self._enforce_rate_limit()
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                wait_time = (attempt + 1) * 2
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                logger.warning(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return None

    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Look up CIK number from ticker symbol"""
        self._enforce_rate_limit()
        try:
            response = requests.get(
                f"{self.base_url}/files/company_tickers.json",
                headers=self.web_headers
            )
            response.raise_for_status()
            data = response.json()
            
            for entry in data.values():
                if entry["ticker"].upper() == ticker.upper():
                    return str(entry["cik_str"]).zfill(10)
            return None
            
        except Exception as e:
            logging.error(f"Error fetching CIK for ticker {ticker}: {str(e)}")
            return None 

    def get_company_filings(self, cik: str) -> Optional[Dict]:
        """Get the company's filing metadata using SEC's EDGAR API"""
        try:
            logger.debug(f"Fetching filing metadata for CIK: {cik}")
            # Use the correct API endpoint
            url = f"{self.api_url}/submissions/CIK{cik.zfill(10)}.json"
            
            response = self._make_request(url, use_api=True)
            if not response:
                return None
            
            submissions_data = response.json()
            recent_filings = submissions_data.get('filings', {}).get('recent', [])
            
            entries = []
            for idx, form in enumerate(recent_filings.get('form', [])):
                if form == '10-K':
                    entries.append({
                        'filing_type': form,
                        'date': recent_filings.get('filingDate', [])[idx],
                        'accession_number': recent_filings.get('accessionNumber', [])[idx].replace('-', ''),
                        'primary_doc': recent_filings.get('primaryDocument', [])[idx],
                        'file_number': recent_filings.get('fileNumber', [])[idx]
                    })
            
            logger.debug(f"Found {len(entries)} 10-K filings")
            return {'filings': entries}
            
        except Exception as e:
            logger.error(f"Error fetching filing metadata: {str(e)}")
            return None

    def get_latest_10k_url(self, cik: str) -> Optional[str]:
        """Get the URL of the latest 10-K filing"""
        filings = self.get_company_filings(cik)
        if not filings:
            return None

        try:
            logger.debug("Searching for latest 10-K filing")
            # Filter for 10-K filings
            ten_k_filings = [
                filing for filing in filings['filings']
                if filing['filing_type'].upper() == '10-K'
            ]

            if not ten_k_filings:
                logger.warning(f"No 10-K filings found for CIK: {cik}")
                return None

            # Sort by date (newest first) and get the latest
            latest_10k = sorted(
                ten_k_filings,
                key=lambda x: x['date'],
                reverse=True
            )[0]

            # Construct the URL using the primary document name
            accession_number = latest_10k['accession_number']
            primary_doc = latest_10k['primary_doc']
            filing_url = f"{self.base_url}/Archives/edgar/data/{cik}/{accession_number}/{primary_doc}"
            logger.debug(f"Found latest 10-K URL: {filing_url}")
            return filing_url

        except Exception as e:
            logger.error(f"Error finding latest 10-K: {str(e)}")
            return None

    def download_filing(self, url: str, save_path: Optional[Path] = None) -> Optional[str]:
        """Download and save a filing"""
        try:
            logger.debug(f"Downloading filing from URL: {url}")
            response = self._make_request(url, use_api=False)  # Use web headers for archive access
            if not response:
                return None
            
            content = response.text

            if save_path:
                logger.debug(f"Saving filing to: {save_path}")
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            return content

        except Exception as e:
            logger.error(f"Error downloading filing: {str(e)}")
            return None

    def get_and_save_latest_10k(self, ticker: str) -> Optional[Dict]:
        """Complete pipeline to get and save the latest 10-K and extract risk factors"""
        try:
            # Get CIK
            logger.info(f"Starting download process for ticker: {ticker}")
            cik = self.get_cik_from_ticker(ticker)
            if not cik:
                logger.error(f"Could not find CIK for ticker: {ticker}")
                return None

            # Get filings to get metadata
            filings = self.get_company_filings(cik)
            if not filings or not filings.get('filings'):
                return None
            
            # Get the latest filing
            latest_filing = sorted(
                filings['filings'],
                key=lambda x: x['date'],
                reverse=True
            )[0]

            # Get latest 10-K URL
            filing_url = self.get_latest_10k_url(cik)
            if not filing_url:
                logger.error(f"Could not find latest 10-K URL for CIK: {cik}")
                return None

            # Create save path with more metadata
            filing_date = latest_filing['date']
            save_path = RAW_DATA_DIR / f"{ticker}" / f"{filing_date}"
            save_path.mkdir(parents=True, exist_ok=True)
            
            file_path = save_path / f"{latest_filing['primary_doc']}"

            # Download and save
            content = self.download_filing(filing_url, file_path)
            if content:
                # Extract risk factors
                risk_factors = self.extract_risk_factors(content)
                
                # Save metadata
                metadata = {
                    'ticker': ticker,
                    'cik': cik,
                    'filing_type': latest_filing['filing_type'],
                    'filing_date': filing_date,
                    'accession_number': latest_filing['accession_number'],
                    'file_number': latest_filing['file_number'],
                    'primary_doc': latest_filing['primary_doc'],
                    'url': filing_url,
                    'size': len(content),
                    'download_timestamp': datetime.now().isoformat()
                }
                
                if risk_factors:
                    # Save risk factors to separate file
                    risk_factors_path = save_path / 'risk_factors.json'
                    with open(risk_factors_path, 'w') as f:
                        json.dump(risk_factors, f, indent=4)
                    metadata['risk_factors_extracted'] = True
                    metadata['risk_factors_word_count'] = risk_factors['word_count']
                else:
                    metadata['risk_factors_extracted'] = False
                
                # Save metadata to JSON file
                metadata_path = save_path / 'metadata.json'
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                    
                logger.info(f"Successfully saved 10-K and metadata to: {save_path}")
                return metadata
                
            return None

        except Exception as e:
            logger.error(f"Error in download pipeline: {str(e)}")
            return None

    def extract_risk_factors(self, html_content: str) -> Optional[Dict]:
        """
        Extract risk factors section from 10-K filing with XBRL support.
        Returns a dictionary with the complete risk factors text and metadata.
        """
        try:
            logger.debug("Starting risk factors extraction")
            # Parse with 'lxml' to better handle XBRL
            soup = BeautifulSoup(html_content, 'lxml')
            
            # XBRL specific patterns
            risk_patterns = [
                # Standard patterns
                "Item 1A", "Item 1A.", "ITEM 1A", "ITEM 1A.",
                "Risk Factors", "RISK FACTORS",
                # XBRL specific patterns
                "RiskFactors", "risk-factors"
            ]
            
            # Method 1: Try finding by XBRL tags
            risk_section = None
            
            # Look for XBRL elements with specific attributes
            xbrl_candidates = soup.find_all(['ix:nonnumeric', 'ix:nonFraction'],
                attrs={'name': lambda x: x and 'risk' in x.lower()})
            
            if xbrl_candidates:
                for candidate in xbrl_candidates:
                    text = candidate.get_text(strip=True)
                    if any(pattern in text for pattern in risk_patterns):
                        risk_section = candidate
                        break
            
            # Method 2: Look for specific div structure in XBRL docs
            if not risk_section:
                candidates = soup.find_all('div', attrs={
                    'style': lambda x: x and 'display:none' not in str(x).lower()
                })
                for div in candidates:
                    text = div.get_text(strip=True)
                    if any(pattern in text for pattern in risk_patterns):
                        risk_section = div
                        break
            
            if not risk_section:
                logger.warning("Could not find risk factors section header")
                return None
            
            logger.debug("Found risk factors section header")
            
            # Extract content considering XBRL structure
            risk_text = []
            
            # Get the parent container that holds the actual content
            content_container = risk_section
            while content_container and not content_container.find_all(['p', 'div'], recursive=False):
                content_container = content_container.parent
            
            if content_container:
                # Collect all text elements
                for elem in content_container.find_all(['p', 'div', 'span', 'ix:nonnumeric']):
                    # Skip hidden elements and navigation
                    if elem.get('style') and 'display:none' in elem['style'].lower():
                        continue
                    
                    text = elem.get_text(strip=True)
                    # Filter out short texts and navigation elements
                    if text and len(text) > 20 and not any(nav in text.lower() 
                        for nav in ['table of contents', 'jump to', 'click here']):
                        risk_text.append(text)
            
            if not risk_text:
                logger.warning("No risk factor content found")
                return None
            
            # Clean and combine text
            full_text = '\n\n'.join(risk_text)
            
            # Remove duplicate paragraphs (sometimes XBRL has duplicates)
            unique_paragraphs = list(dict.fromkeys(full_text.split('\n\n')))
            full_text = '\n\n'.join(unique_paragraphs)
            
            # Create structured output
            result = {
                'section_title': risk_section.get_text(strip=True),
                'content': full_text,
                'word_count': len(full_text.split()),
                'char_count': len(full_text),
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_status': 'success',
                'format': 'xbrl'
            }
            
            logger.info(f"Successfully extracted risk factors ({result['word_count']} words)")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting risk factors: {str(e)}")
            return None

    def get_historical_filings(self, ticker: str, num_years: int = MAX_YEARS_COMPARISON) -> List[Dict]:
        """Get and process multiple years of 10-K filings"""
        try:
            # Get CIK
            cik = self.get_cik_from_ticker(ticker)
            if not cik:
                return None
            
            # Get all filings
            filings = self.get_company_filings(cik)
            if not filings or not filings.get('filings'):
                return None
            
            # Sort by date and get the most recent num_years
            sorted_filings = sorted(
                filings['filings'],
                key=lambda x: x['date'],
                reverse=True
            )[:num_years]
            
            results = []
            for filing in sorted_filings:
                # Create save path
                filing_date = filing['date']
                save_path = RAW_DATA_DIR / ticker / filing_date
                save_path.mkdir(parents=True, exist_ok=True)
                
                file_path = save_path / filing['primary_doc']
                
                # Download filing
                url = f"{self.base_url}/Archives/edgar/data/{cik}/{filing['accession_number']}/{filing['primary_doc']}"
                content = self.download_filing(url, file_path)
                
                if content:
                    # Extract risk factors using the new extractor
                    risk_factors = TextExtractor.extract_risk_factors(content)
                    
                    if risk_factors:
                        # Save risk factors
                        risk_factors_path = save_path / 'risk_factors.json'
                        with open(risk_factors_path, 'w') as f:
                            json.dump(risk_factors, f, indent=4)
                    
                    # Save metadata
                    metadata = {
                        'ticker': ticker,
                        'cik': cik,
                        'filing_type': filing['filing_type'],
                        'filing_date': filing_date,
                        'accession_number': filing['accession_number'],
                        'file_number': filing['file_number'],
                        'primary_doc': filing['primary_doc'],
                        'url': url,
                        'size': len(content),
                        'risk_factors_extracted': bool(risk_factors),
                        'download_timestamp': datetime.now().isoformat()
                    }
                    
                    metadata_path = save_path / 'metadata.json'
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=4)
                    
                    results.append(metadata)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing historical filings: {str(e)}")
            return None