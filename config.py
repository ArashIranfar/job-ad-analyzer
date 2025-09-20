# """
# Configuration settings for Job Ad Analyzer
# """

# import os
# from pathlib import Path
# from dotenv import load_dotenv 

# load_dotenv()

# # Base directories
# BASE_DIR = Path(__file__).parent
# DATA_DIR = BASE_DIR / "data"
# LOGS_DIR = BASE_DIR / "logs"

# # LLM Settings
# LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5-mini")
# LLM_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this in your environment
# LLM_BASE_URL = os.getenv("LLM_BASE_URL")  # Optional: for custom endpoints
# MAX_RETRIES = 3
# RETRY_DELAY = 2  # seconds
# RATE_LIMIT_DELAY = 1  # seconds between requests

# # LLM Request Settings
# MAX_TOKENS = 2000
# TEMPERATURE = 0.1  # Low temperature for more consistent structured output
# TIMEOUT = 120  # seconds

# # Scraping Settings
# REQUEST_TIMEOUT = 30
# USER_AGENT = "Mozilla/5.0 (JobAdAnalyzer/1.0)"
# MAX_CONTENT_LENGTH = 50000  # characters
# SCRAPING_DELAY = 1  # seconds between requests

# # Processing Settings
# MIN_FIELD_FREQUENCY = 0.1  # Include field if present in >10% of ads
# MISC_COLUMN_NAME = "misc_features"
# MAX_MISC_ITEMS = 10  # Maximum items to include in misc column per ad

# # File Paths
# URLS_FILE = DATA_DIR / "input" / "urls.txt"
# PROMPT_FILE = DATA_DIR / "input" / "master_prompt.txt"
# RAW_DATA_DIR = DATA_DIR / "raw"
# PROCESSED_DATA_DIR = DATA_DIR / "processed"
# OUTPUT_DIR = DATA_DIR / "output"
# LOG_FILE = LOGS_DIR / "app.log"

# # Output Settings
# OUTPUT_FORMATS = ["csv", "json"]  # Supported output formats
# CSV_ENCODING = "utf-8"
# EXCEL_SHEET_NAME = "Job_Ads"

# # Logging Settings
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
# LOG_BACKUP_COUNT = 5

# # Error Handling
# MAX_CONTENT_ERRORS = 5  # Max content extraction errors before stopping
# MAX_LLM_ERRORS = 10  # Max LLM errors before stopping
# CONTINUE_ON_ERROR = True  # Continue pipeline even if some URLs fail

# # Data Validation
# REQUIRED_JSON_FIELDS = []  # Fields that must be present in LLM response
# EXPECTED_DATA_TYPES = {
#     "job_title": str,
#     "company": str,
#     "location": str,
#     "salary_min": (int, float, type(None)),
#     "salary_max": (int, float, type(None)),
#     "experience_years": (int, float, type(None)),
#     "remote_work": bool
# }

# # Development/Debug Settings
# SAVE_RAW_HTML = True  # Save raw HTML for debugging
# SAVE_CLEANED_TEXT = True  # Save cleaned text for debugging
# VERBOSE_LOGGING = os.getenv("DEBUG", "False").lower() == "true"
# SAMPLE_SIZE = None  # Set to int to process only first N URLs (for testing)

# # API Rate Limiting
# REQUESTS_PER_MINUTE = 60
# REQUESTS_PER_HOUR = 1000

# def validate_config():
#     """Validate configuration settings"""
#     errors = []
    
#     if not LLM_API_KEY and LLM_MODEL.startswith("gpt"):
#         errors.append("LLM_API_KEY environment variable is required for OpenAI models")
    
#     if MIN_FIELD_FREQUENCY < 0 or MIN_FIELD_FREQUENCY > 1:
#         errors.append("MIN_FIELD_FREQUENCY must be between 0 and 1")
    
#     if MAX_RETRIES < 0:
#         errors.append("MAX_RETRIES must be non-negative")
    
#     if REQUEST_TIMEOUT <= 0:
#         errors.append("REQUEST_TIMEOUT must be positive")
    
#     if errors:
#         raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

# def get_headers():
#     """Get HTTP headers for web requests"""
#     return {
#         "User-Agent": USER_AGENT,
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate",
#         "Connection": "keep-alive",
#         "Cache-Control": "no-cache",
#     }

# # Validate config on import
# validate_config()

"""
Configuration settings for Job Ad Analyzer
"""

import os
from pathlib import Path
from dotenv import load_dotenv 

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# LLM Settings
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this in your environment
LLM_BASE_URL = os.getenv("LLM_BASE_URL")  # Optional: for custom endpoints
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RATE_LIMIT_DELAY = 1  # seconds between requests

# LLM Request Settings
MAX_TOKENS = 2000
TEMPERATURE = 0.1  # Low temperature for more consistent structured output
TIMEOUT = 120  # seconds

# Scraping Settings
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (JobAdAnalyzer/1.0)"
MAX_CONTENT_LENGTH = 50000  # characters
SCRAPING_DELAY = 1  # seconds between requests

# Processing Settings
MIN_FIELD_FREQUENCY = 0 #0.1  # Include field if present in >10% of ads
MISC_COLUMN_NAME = "misc_features"
MAX_MISC_ITEMS = 10  # Maximum items to include in misc column per ad

# File Paths
URLS_FILE = DATA_DIR / "input" / "urls.txt"
PROMPT_FILE = DATA_DIR / "input" / "master_prompt.txt"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"
LOG_FILE = LOGS_DIR / "app.log"

# Output Settings
OUTPUT_FORMATS = ["csv", "json"]  # Supported output formats
CSV_ENCODING = "utf-8-sig"  # UTF-8 with BOM for better Farsi/Unicode support
EXCEL_SHEET_NAME = "Job_Ads"

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Error Handling
MAX_CONTENT_ERRORS = 5  # Max content extraction errors before stopping
MAX_LLM_ERRORS = 10  # Max LLM errors before stopping
CONTINUE_ON_ERROR = True  # Continue pipeline even if some URLs fail

# Data Validation
REQUIRED_JSON_FIELDS = []  # Fields that must be present in LLM response
EXPECTED_DATA_TYPES = {
    # Standard extraction
    "job_title": str,
    "company": str,
    "location": str,
    "salary_min": (int, float, type(None)),
    "salary_max": (int, float, type(None)),
    "experience_years": (int, float, type(None)),
    "remote_work": bool,
    
    # Payment analysis
    "estimated_salary_irr": str,
    "salary_reasoning": str,
    
    # Candidate fit
    "fit_tier": str,
    "fit_summary": str,
    "fit_strengths": str,
    "fit_gaps": str,
    
    # Overqualified assessment
    "is_overqualified": bool,
    "overqualified_reasoning": str,
    
    # Growth potential
    "growth_potential": str,
}
# Development/Debug Settings
SAVE_RAW_HTML = True  # Save raw HTML for debugging
SAVE_CLEANED_TEXT = True  # Save cleaned text for debugging
VERBOSE_LOGGING = os.getenv("DEBUG", "False").lower() == "true"
SAMPLE_SIZE = None  # Set to int to process only first N URLs (for testing)

# API Rate Limiting
REQUESTS_PER_MINUTE = 60
REQUESTS_PER_HOUR = 1000

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not LLM_API_KEY and LLM_MODEL.startswith("gpt"):
        errors.append("LLM_API_KEY environment variable is required for OpenAI models")
    
    if MIN_FIELD_FREQUENCY < 0 or MIN_FIELD_FREQUENCY > 1:
        errors.append("MIN_FIELD_FREQUENCY must be between 0 and 1")
    
    if MAX_RETRIES < 0:
        errors.append("MAX_RETRIES must be non-negative")
    
    if REQUEST_TIMEOUT <= 0:
        errors.append("REQUEST_TIMEOUT must be positive")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

def get_headers():
    """Get HTTP headers for web requests"""
    return {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

# Validate config on import
validate_config()