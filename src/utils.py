"""
Utility functions for Job Ad Analyzer
"""

import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from logging.handlers import RotatingFileHandler
import config


def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def ensure_directories():
    """Create all necessary directories"""
    directories = [
        config.DATA_DIR / "input",
        config.RAW_DATA_DIR,
        config.PROCESSED_DATA_DIR,
        config.OUTPUT_DIR,
        config.LOGS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Ensured directory exists: {directory}")


def load_text_file(file_path: str) -> str:
    """Load text content from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to load file {file_path}: {e}")
        raise


def save_text_file(content: str, file_path: Path, encoding: str = 'utf-8'):
    """Save text content to file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logging.debug(f"Saved text file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to save file {file_path}: {e}")
        raise


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON file {file_path}: {e}")
        raise


def save_json_file(data: Any, file_path: Path, indent: int = 2):
    """Save data as JSON file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logging.debug(f"Saved JSON file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to save JSON file {file_path}: {e}")
        raise


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove HTML entities that might have been missed
    import html
    text = html.unescape(text)
    
    return text.strip()


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length, preserving word boundaries"""
    if len(text) <= max_length:
        return text
    
    # Find last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we found a space in the last 20%
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return "unknown"


def validate_json_structure(data: Dict[str, Any], required_fields: List[str] = None) -> bool:
    """Validate JSON data structure"""
    if not isinstance(data, dict):
        return False
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                logging.warning(f"Missing required field: {field}")
                return False
    
    return True


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary value"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def normalize_salary(salary_str: str) -> Optional[float]:
    """Normalize salary string to float"""
    if not salary_str:
        return None
    
    try:
        # Remove common currency symbols and text
        import re
        cleaned = re.sub(r'[^\d.,k]', '', str(salary_str).lower())
        
        # Handle 'k' notation
        if 'k' in cleaned:
            cleaned = cleaned.replace('k', '')
            multiplier = 1000
        else:
            multiplier = 1
        
        # Convert to float
        if cleaned:
            # Handle comma as decimal separator (European format)
            if ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
            elif ',' in cleaned and '.' in cleaned:
                # Assume comma is thousands separator
                cleaned = cleaned.replace(',', '')
            
            return float(cleaned) * multiplier
    
    except (ValueError, AttributeError):
        logging.debug(f"Could not normalize salary: {salary_str}")
    
    return None


def create_sample_files():
    """Create sample input files for testing"""
    ensure_directories()
    
    # Sample URLs
    sample_urls = [
        "https://example-job-site.com/job/1",
        "https://another-job-site.com/listing/123",
        "# This is a comment - will be ignored",
        "https://third-site.com/careers/456"
    ]
    
    urls_file = config.DATA_DIR / "input" / "urls.txt"
    if not urls_file.exists():
        with open(urls_file, 'w') as f:
            f.write('\n'.join(sample_urls))
        logging.info(f"Created sample URLs file: {urls_file}")
    
    # Sample master prompt
    sample_prompt = """You are an expert career advisor and technical recruiter with deep knowledge of the AI, IoT, and Robotics industries. Your task is to analyze a job advertisement based on the provided candidate's profile and a specific set of criteria.

First, carefully review the candidate's profile to understand their skills, experience, and seniority level.
Then, analyze the provided job advertisement.

Finally, provide a detailed analysis in a single, comprehensive JSON format. Do not add any text or explanations outside of the JSON object.

The candidate's profile is as follows:
The candidate is a Ph.D. in Electrical Engineering specializing in full-stack AI and IoT systems. He possesses senior-level, end-to-end project experience, from custom PCB design (Altium) and embedded firmware (C++, STM32, ESP32, RTOS) to high-level application development.

Core Strengths:

AI/ML: Expert in modern AI stacks including LangChain, RAG architectures, Vector Databases, and Computer Vision (YOLOv4).

IoT & Hardware: Proven experience in designing and deploying safety-critical IoT control systems, including custom PCB and firmware for commercial products.

Leadership: Has served as a Product Manager and Technical Lead, managing cross-functional teams and overseeing the entire product lifecycle.

Full-Stack Capability: Proficient in building complete solutions with FastAPI backends and Streamlit frontends.

He is an ideal candidate for senior or lead roles requiring a deep, first-principles understanding of both hardware and intelligent software, particularly in AI-driven IoT, robotics, and complex data analysis platforms.
Based on this profile, analyze the job advertisement below and return the results in the specified JSON format, including both the standard data extraction and the personalized analysis.

{
    "standard_extraction": {
    "job_title": "The exact job title",
    "position_level": "Junior",
    "company": "The company name",
    "salary_min": 50000,
    "salary_max": 70000,
    "employment_type": "full-time/part-time/contract",
    "experience_years": 3,
    "remote_work": true,
    "required_skills": ["skill1", "skill2"],
    "education_level": "bachelor's/master's/etc",
    "industry": "The company's industry",
    "benefits": ["benefit1", "benefit2"]
    },
    "payment_analysis": {
        "estimated_range_IRR": "40.000.000.0 to 70.000.000.0 IRR",
        "reasoning": "Based on the senior-level requirements and location, company size, quality of the app, and company reputation, this is the likely range for a candidate with a Ph.D. and relevant leadership experience."
    },
    "candidate_fit": {
        "tier": "A",
        "summary": "A very strong fit. The role's focus on AI-driven IoT systems aligns perfectly with the candidate's core expertise in both hardware and ML.",
        "strengths": ["Deep experience with full-stack IoT solutions.", "Leadership experience as a Technical Lead matches seniority.", "Proficiency in the required Python and C++ stacks."],
        "gaps": ["The ad mentions Kubernetes, which is not explicitly listed on the candidate's profile."]
    },
    "is_overqualified": {
        "value": false,
        "reasoning": "The role appears to be a senior or lead position, which is appropriate for the candidate's Ph.D. and project management experience."
    },
    "growth_potential": {
        "summary": "The ad suggests strong growth potential by mentioning the opportunity to 'build and lead a new AIoT division'.",
        "evidence": ["build and lead a new AIoT division", "opportunity to define the technical roadmap"]
    }
}

Important:
- Use null for missing information
- Extract salary as numbers only (no currency symbols)
- Keep required_skills as a list of strings
- Put any unique job features in misc_features
- Be as accurate as possible
"""
    
    prompt_file = config.DATA_DIR / "input" / "master_prompt.txt"
    if not prompt_file.exists():
        with open(prompt_file, 'w') as f:
            f.write(sample_prompt)
        logging.info(f"Created sample master prompt file: {prompt_file}")


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes"""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"