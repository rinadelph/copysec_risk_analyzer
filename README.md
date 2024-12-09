# SEC Risk Factor Analyzer

A Python tool for analyzing and comparing risk factors in SEC 10-K filings using AI.

## Features

- Fetch and analyze risk factors from SEC 10-K filings
- Compare risk factors between years
- AI-powered analysis of risk changes
- Support for multiple companies
- Detailed reporting and insights

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/copysec_risk_analyzer.git
cd copysec_risk_analyzer
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Create a `.env` file in the root directory with your API keys:
```
SEC_USER_AGENT="Your Name (your.email@example.com)"
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the risk analyzer:
```bash
python -m copysec_risk_analyzer.analyze_risks
```

This will:
1. Prompt for a company ticker
2. Fetch the company's 10-K filings from SEC EDGAR
3. Extract risk factors from the filings
4. Analyze changes between years
5. Generate a detailed report

## Project Structure

```
copysec_risk_analyzer/
├── data/               # Data storage
│   ├── raw/           # Raw SEC filings
│   └── processed/     # Processed risk factors
├── src/               # Source code
│   ├── collectors/    # SEC API interaction
│   ├── processors/    # Text processing
│   ├── analyzers/     # AI analysis
│   └── extractors/    # Text extraction
├── config/            # Configuration files
├── tests/             # Test files
└── docs/              # Documentation
```

## Requirements

- Python 3.8+
- beautifulsoup4
- requests
- yfinance
- python-dotenv
- openai
- tqdm
- lxml

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- SEC EDGAR for providing access to filings
- OpenAI for GPT-4 API
- Yahoo Finance for company data 