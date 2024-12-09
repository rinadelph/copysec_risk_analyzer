# Risk Factor Sentiment Analysis for Large-Cap Companies

## Project Overview
Create a system to analyze and rank companies with >$500M market cap based on negative changes in their 10-K risk factor disclosures year-over-year. This tool will help identify companies experiencing the most significant increases in risk disclosure severity.

## Core Functionalities
1. **Market Data Collection**
   - Fetch list of companies >$500M market cap
   - Get current market cap data
   - Track company identifiers (CIK, ticker)

2. **SEC Filing Collection**
   - Retrieve 10-K filings for qualified companies
   - Extract risk factor sections
   - Store historical data for comparison

3. **Sentiment Analysis**
   - Compare YoY risk factor changes
   - Analyze sentiment shifts
   - Quantify risk severity changes

4. **Ranking & Reporting**
   - Rank companies by risk sentiment deterioration
   - Generate detailed analysis reports
   - Provide drill-down capabilities

## Implementation Plan

### 1.0 Data Source Setup
1.1. Market Data API Integration
   - Use Financial Modeling Prep API (free tier) for market cap data
   - Alternative: Alpha Vantage API for company fundamentals
   - Backup: Yahoo Finance API through yfinance package

1.2. SEC Data Integration
   - SEC EDGAR API for filing retrieval
   - Store CIK to ticker mappings
   - Track filing dates and document types

### 2.0 Data Collection Pipeline
2.1. Company Screening
   - Fetch all listed companies
   - Filter by market cap threshold
   - Store qualified company list

2.2. Filing Retrieval
   - Get latest 10-K for each company
   - Get previous year's 10-K
   - Extract Item 1A (Risk Factors)

### 3.0 Analysis Engine
3.1. Text Processing
   - Clean and normalize text
   - Split into comparable sections
   - Remove boilerplate content

3.2. Sentiment Analysis
   - Use O1 API for deep semantic analysis
   - Compare YoY changes in risk language
   - Quantify severity changes

3.3. Scoring System
   - Develop risk change metrics
   - Weight different risk categories
   - Calculate composite score

### 4.0 Results & Interface
4.1. Database Structure
   - Store company profiles
   - Track historical analyses
   - Cache API responses

4.2. Command Line Interface
   ```
   Usage:
   risk-analyzer [command] [options]

   Commands:
   analyze         Run full analysis on all companies
   search <query>  Search companies by name/ticker
   report          Generate ranked report of risk changes
   details <tick>  Show detailed analysis for one company
   ```

## Free API Resources
1. **Market Data**
   - Financial Modeling Prep (500 requests/day)
   - Alpha Vantage (500 requests/day)
   - yfinance (unlimited, unofficial)

2. **SEC Data**
   - SEC EDGAR API (no limits)
   - SEC Company Index (daily updates)

3. **Text Analysis**
   - O1 API (with limits)
   - NLTK (local processing)
   - TextBlob (local processing)

## Next Steps
1. Set up data collection pipeline for market caps
2. Implement SEC filing retrieval system
3. Create text extraction and comparison logic
4. Develop sentiment analysis integration
5. Build ranking and reporting system
6. Create command-line interface
7. Add caching and optimization
8. Implement error handling and logging

## Success Metrics
- Successfully analyze >90% of qualified companies
- Process new 10-K filings within 24 hours
- Generate actionable insights about risk changes
- Provide both high-level rankings and detailed analysis