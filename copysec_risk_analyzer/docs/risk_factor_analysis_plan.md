# Risk Factor Analysis Implementation Plan

## Objective
Create a system to extract, compare, and analyze risk factors from current and previous 10-K filings using the SEC EDGAR API and ChatGPT.

## Implementation Steps

### 1. Risk Factor Extraction Enhancement
1. Modify extraction to focus only on Item 1A (Risk Factors)
   - Start extraction at "Item 1A" or "ITEM 1A"
   - End extraction at "Item 1B" or "Item 2"
   - Remove XBRL markup and formatting
   - Store clean text only

2. Add historical filing retrieval
   - Modify `get_company_filings` to get last 2 years of 10-Ks
   - Add method to download specific historical filing
   - Store filings with clear year identification

### 2. Data Structure
1. Create organized storage structure: 