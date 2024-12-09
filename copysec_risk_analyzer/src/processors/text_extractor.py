from typing import Optional, Dict, List
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class TextExtractor:
    @staticmethod
    def extract_risk_factors(html_content: str) -> Optional[Dict]:
        """Extract and process risk factors through multiple stages"""
        try:
            # Stage 1: Raw Extraction
            raw_section = TextExtractor._extract_raw_section(html_content)
            if not raw_section:
                return None

            # Stage 2: Clean Text
            cleaned_text = TextExtractor._clean_text(raw_section)
            if not cleaned_text:
                return None

            # Stage 3: Process into structured format
            processed_content = TextExtractor._process_content(cleaned_text)
            if not processed_content:
                return None

            return processed_content

        except Exception as e:
            logger.error(f"Error in risk factor extraction pipeline: {str(e)}")
            return None

    @staticmethod
    def _extract_raw_section(html_content: str) -> Optional[str]:
        """Extract complete risk factors section using multiple strategies"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.debug("Parsing HTML document...")

            # Strategy 1: Look for standard section markers
            risk_markers = [
                "Item 1A. Risk Factors",
                "ITEM 1A. RISK FACTORS",
                "Item 1A—Risk Factors",
                "Item 1A: Risk Factors",
                "Item 1A - Risk Factors"
            ]

            # Strategy 2: Look for content identifiers
            content_markers = [
                "The Company's business, reputation, results",
                "Because of the following factors",
                "The following risk factors",
                "Risks affecting our business"
            ]

            # Strategy 3: Look for section boundaries
            section_end_markers = [
                "Item 1B",
                "ITEM 1B",
                "Item 2",
                "ITEM 2",
                "Unresolved Staff Comments"
            ]

            def find_risk_section():
                """Try multiple strategies to find the risk section"""
                # Try each strategy in order
                for strategy in [
                    find_by_section_marker,
                    find_by_content,
                    find_by_structure
                ]:
                    result = strategy(soup)
                    if result:
                        return result
                return None

            def find_by_section_marker(soup):
                """Strategy 1: Find by section marker"""
                for marker in risk_markers:
                    elements = soup.find_all(string=lambda text: text and marker in text)
                    for element in elements:
                        # Verify it's not a reference
                        if not element.find_parent('a'):
                            container = element.find_parent(['div', 'section'])
                            if container:
                                # Verify it has content
                                next_content = container.find_next_siblings(['div', 'p'])
                                if next_content and any(
                                    cm in nc.get_text() for nc in next_content[:3]
                                    for cm in content_markers
                                ):
                                    return container
                return None

            def find_by_content(soup):
                """Strategy 2: Find by content markers"""
                for marker in content_markers:
                    elements = soup.find_all(string=lambda text: text and marker in text)
                    for element in elements:
                        container = element.find_parent(['div', 'section'])
                        if container:
                            # Look backwards for section header
                            prev_elements = container.find_previous_siblings(['div', 'p'])
                            if any(
                                "Risk Factors" in pe.get_text() 
                                for pe in prev_elements[:3]
                            ):
                                return container
                return None

            def find_by_structure(soup):
                """Strategy 3: Find by document structure"""
                # Look for typical 10-K structure
                for div in soup.find_all('div'):
                    text = div.get_text()
                    if "Item 1A" in text and "Risk Factors" in text:
                        next_divs = div.find_next_siblings('div', limit=3)
                        if any(
                            any(cm in nd.get_text() for cm in content_markers)
                            for nd in next_divs
                        ):
                            return div
                return None

            # Find the risk section using multiple strategies
            risk_section = find_risk_section()
            if not risk_section:
                logger.warning("Could not find risk factors section")
                return None

            # Extract content
            content = []
            seen_texts = set()  # Track unique texts to avoid duplicates
            current = risk_section

            def is_valid_content(text: str) -> bool:
                if not text or len(text) < 20:
                    return False
                # Skip navigation and metadata
                skip_markers = [
                    'table of contents', 'click here', 'jump to', 'page',
                    'form 10-k', 'apple inc.', 'forward-looking statements'
                ]
                return not any(marker in text.lower() for marker in skip_markers)

            # Collect content until end marker
            while current:
                current = current.find_next()
                if not current:
                    break

                text = current.get_text(strip=True)
                
                # Check for section end
                if any(marker in text for marker in section_end_markers):
                    break

                # Only add text if it's valid and not seen before
                if is_valid_content(text) and text not in seen_texts:
                    content.append(text)
                    seen_texts.add(text)

            if not content:
                logger.warning("No content found in risk section")
                return None

            # Combine and clean text, ensuring proper paragraph separation
            full_text = []
            current_section = None

            for text in content:
                # Check if this is a new section header
                is_header = any(text.startswith(marker) for marker in [
                    "Macroeconomic and Industry Risks",
                    "Legal and Regulatory Compliance Risks",
                    "Technology and Information Security Risks",
                    "Operational and Business Risks"
                ])

                if is_header:
                    if current_section:
                        full_text.append('\n'.join(current_section))
                    current_section = [text]
                elif current_section is not None:
                    current_section.append(text)
                else:
                    current_section = [text]

            # Add the last section
            if current_section:
                full_text.append('\n'.join(current_section))

            # Join all sections with double newlines
            final_text = '\n\n'.join(full_text)
            
            # Save raw text for verification
            output_path = Path('debug')
            output_path.mkdir(exist_ok=True)
            
            with open(output_path / 'raw_risk_section.txt', 'w', encoding='utf-8') as f:
                f.write("=== RISK FACTORS SECTION ===\n\n")
                f.write(f"Strategy used: {find_risk_section.__name__}\n")
                f.write(f"Total length: {len(final_text)} characters\n")
                f.write(f"Number of unique paragraphs: {len(content)}\n\n")
                f.write("=== START OF CONTENT ===\n")
                f.write(final_text)
                f.write("\n=== END OF CONTENT ===\n")
            
            logger.info(f"Successfully extracted {len(final_text)} characters")
            return final_text

        except Exception as e:
            logger.error(f"Error in raw extraction: {str(e)}")
            logger.error(f"Error details: {str(e.__class__.__name__)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    @staticmethod
    def _clean_text(raw_text: str) -> Optional[str]:
        """Stage 2: Clean and normalize the text"""
        try:
            logger.debug("Starting text cleaning")
            
            # Skip the header
            content_start = raw_text.find("Risk Factors")
            if content_start > -1:
                text = raw_text[content_start:]
            else:
                text = raw_text
            
            # Basic cleaning
            cleaned = text.replace('\r', ' ')
            cleaned = cleaned.replace('\n', ' ')
            
            # Remove XBRL artifacts
            cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Remove common artifacts
            cleaned = re.sub(r'Table of Contents', '', cleaned)
            cleaned = re.sub(r'Click here to view.*?\.', '', cleaned)
            cleaned = re.sub(r'Risk Factors\s+', '', cleaned, count=1)  # Remove initial header
            
            # Split into paragraphs based on sentence endings
            sentences = re.split(r'(?<=[.!?])\s+', cleaned)
            paragraphs = []
            current_para = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Start a new paragraph if sentence is long enough to be a header
                if len(sentence.split()) > 5 and len(current_para) > 0:
                    # Check if it looks like a new risk factor
                    if re.match(r'^(The Company|The business|If|Changes|Failure|Future|Global)', sentence):
                        if current_para:
                            paragraphs.append(' '.join(current_para))
                            current_para = []
                
                current_para.append(sentence)
                
                # Break paragraph if it's getting too long
                if len(' '.join(current_para)) > 1000:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
            
            if current_para:
                paragraphs.append(' '.join(current_para))
            
            # Filter paragraphs
            filtered_paragraphs = []
            for p in paragraphs:
                # Skip if too short or looks like a header/reference
                if len(p.split()) > 10 and not any(marker in p for marker in [
                    "Item", "ITEM", "Table of Contents", "Form 10-K"
                ]):
                    filtered_paragraphs.append(p.strip())
            
            if not filtered_paragraphs:
                logger.warning("No valid paragraphs found after cleaning")
                return None
            
            result = '\n\n'.join(filtered_paragraphs)
            logger.debug(f"Cleaning complete. Output length: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Error in text cleaning: {str(e)}")
            logger.error(f"Error details: {str(e.__class__.__name__)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    @staticmethod
    def _process_content(cleaned_text: str) -> Optional[Dict]:
        """Process text into individual risk factors"""
        try:
            # Split text into potential risk factors
            risk_starts = [
                "The Company", "Global", "Future", "If the", "Changes",
                "The business", "The Company's", "There can", "The Company has"
            ]
            
            # Initialize variables
            risk_factors = []
            current_text = []
            
            # Process each paragraph
            for paragraph in cleaned_text.split('\n\n'):
                # Check if this paragraph starts a new risk
                is_new_risk = any(paragraph.startswith(start) for start in risk_starts)
                
                if is_new_risk and current_text:
                    # Save previous risk factor
                    risk_factors.append(' '.join(current_text))
                    current_text = [paragraph]
                else:
                    current_text.append(paragraph)
            
            # Add the last risk factor
            if current_text:
                risk_factors.append(' '.join(current_text))
            
            # Create structured output
            result = {
                'section_title': "Item 1A. Risk Factors",
                'risk_factors': [
                    {
                        'text': rf.strip(),
                        'word_count': len(rf.split()),
                        'char_count': len(rf),
                        'summary': rf.split('.')[0]  # First sentence as summary
                    } for rf in risk_factors if len(rf.split()) > 50  # Minimum length check
                ],
                'metadata': {
                    'total_risks': len(risk_factors),
                    'total_words': sum(len(rf.split()) for rf in risk_factors),
                    'total_chars': sum(len(rf) for rf in risk_factors),
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing content: {str(e)}")
            return None 