"""Configuration settings for the risk analyzer"""
import os
from pathlib import Path

# Base URLs
SEC_BASE_URL = "https://www.sec.gov"
SEC_API_URL = "https://data.sec.gov"

# User agent for SEC API
SEC_USER_AGENT = "CompanyName AdminContact@company.com"

# Rate limiting
SEC_RATE_LIMIT = 0.1  # seconds between requests

# Directory paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOG_DIR = ROOT_DIR / "logs"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Maximum number of years to compare
MAX_YEARS_COMPARISON = 3

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 