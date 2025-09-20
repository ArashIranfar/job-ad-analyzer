#!/usr/bin/env python3
"""
Job Ad Analyzer - Main Pipeline
Orchestrates the complete pipeline from URLs to structured output
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import time
from tqdm import tqdm

from src.scraper import WebScraper
from src.llm_client import LLMClient
from src.processor import DataProcessor
from src.utils import setup_logging, load_text_file, ensure_directories
import config


def load_urls(file_path: str) -> List[str]:
    """Load URLs from input file"""
    urls = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
    except FileNotFoundError:
        logging.error(f"URLs file not found: {file_path}")
        raise
    
    logging.info(f"Loaded {len(urls)} URLs")
    return urls


def load_master_prompt(file_path: str) -> str:
    """Load master prompt template"""
    try:
        prompt = load_text_file(file_path)
        logging.info(f"Loaded master prompt ({len(prompt)} characters)")
        return prompt
    except FileNotFoundError:
        logging.error(f"Master prompt file not found: {file_path}")
        raise


# def process_single_url(url: str, url_id: str, scraper: WebScraper, 
#                       llm_client: LLMClient, master_prompt: str) -> Dict[str, Any]:
#     """Process a single URL through the complete pipeline"""
    
#     logging.info(f"Processing {url_id}: {url}")
    
#     try:
#         # Step 1: Scrape content
#         logging.debug(f"Scraping content for {url_id}")
#         content = scraper.scrape_url(url, url_id)
        
#         if not content:
#             logging.warning(f"No content extracted from {url_id}")
#             return {"url": url, "url_id": url_id, "error": "No content extracted", "data": None}
        
#         # Step 2: Send to LLM
#         logging.debug(f"Sending to LLM for analysis: {url_id}")
#         llm_response = llm_client.analyze_job_ad(content, master_prompt, url_id)

def check_existing_result(url_id: str) -> Optional[Dict[str, Any]]:
    """Check if we already have a processed result for this URL"""
    result_file = Path(config.PROCESSED_DATA_DIR) / f"{url_id}.json"
    
    if result_file.exists():
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            # Check if it's a successful result (has data)
            if cached_data.get("data") is not None:
                logging.info(f"Found cached successful result for {url_id}")
                return cached_data
            else:
                logging.info(f"Found cached failed result for {url_id}, will retry")
                return None
                
        except Exception as e:
            logging.warning(f"Error reading cached result for {url_id}: {e}")
            return None
    
    return None

def process_single_url(url: str, url_id: str, scraper: WebScraper, 
                      llm_client: LLMClient, master_prompt: str, force: bool = False) -> Dict[str, Any]:
    """Process a single URL through the complete pipeline"""
    
    logging.info(f"Processing {url_id}: {url}")
    
    # CHECK CACHE FIRST (unless force=True)
    if not force:
        cached_result = check_existing_result(url_id)
        if cached_result:
            logging.info(f"Using cached result for {url_id}")
            return cached_result
    
    try:
        # Step 1: Scrape content (check cache first)
        logging.debug(f"Scraping content for {url_id}")
        content = scraper.scrape_url(url, url_id, force=force)  # Pass force to scraper
        
        if not content:
            logging.warning(f"No content extracted from {url_id}")
            return {"url": url, "url_id": url_id, "error": "No content extracted", "data": None}
        
        # Step 2: Send to LLM (check cache first)
        logging.debug(f"Sending to LLM for analysis: {url_id}")
        llm_response = llm_client.analyze_job_ad(content, master_prompt, url_id, force=force)
        
        if not llm_response:
            logging.warning(f"No response from LLM for {url_id}")
            return {"url": url, "url_id": url_id, "error": "No LLM response", "data": None}
        
        # Step 3: Save individual result
        result = {
            "url": url,
            "url_id": url_id,
            "timestamp": time.time(),
            "content_length": len(content),
            "data": llm_response,
            "error": None
        }
        
        # Save individual JSON
        output_file = Path(config.PROCESSED_DATA_DIR) / f"{url_id}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logging.info(f"Successfully processed {url_id}")
        return result
        
    except Exception as e:
        logging.error(f"Error processing {url_id}: {str(e)}")
        error_result = {
            "url": url,
            "url_id": url_id,
            "error": str(e),
            "data": None
        }
        
        # Save error result
        output_file = Path(config.PROCESSED_DATA_DIR) / f"{url_id}.json"
        with open(output_file, 'w') as f:
            json.dump(error_result, f, indent=2)
        
        return error_result


def main(force: bool = False):
    """Main pipeline execution"""
    
    # Setup logging
    setup_logging()
    logging.info("Starting Job Ad Analyzer Pipeline")
    
    try:
        # Ensure directory structure exists
        ensure_directories()
        
        # Load inputs
        urls = load_urls(config.URLS_FILE)
        master_prompt = load_master_prompt(config.PROMPT_FILE)
        
        # Initialize components
        scraper = WebScraper()
        llm_client = LLMClient()
        processor = DataProcessor()
        
        # Process all URLs
        results = []
        total_urls = len(urls)
        
        # for i, url in enumerate(urls, 1):
        #     url_id = f"url_{i:03d}"
        #     logging.info(f"Processing {i}/{total_urls}: {url_id}")
            
        #     result = process_single_url(url, url_id, scraper, llm_client, master_prompt)
        #     results.append(result)
            
        #     # Add delay between requests to be respectful
        #     if i < total_urls:  # Don't delay after last URL
        #         time.sleep(config.RATE_LIMIT_DELAY)
        for i, url in enumerate(tqdm(urls, desc="Processing URLs", unit="url"), 1):
            url_id = f"url_{i:03d}"
            
            result = process_single_url(url, url_id, scraper, llm_client, master_prompt, force=force)
            results.append(result)
            
            # Respectful delay
            if i < total_urls:
                time.sleep(config.RATE_LIMIT_DELAY)
        
        # Generate summary
        successful = [r for r in results if r["error"] is None]
        failed = [r for r in results if r["error"] is not None]
        
        logging.info(f"Pipeline completed: {len(successful)} successful, {len(failed)} failed")
        
        # Process results into final table
        if successful:
            logging.info("Creating final structured output...")
            processor.create_final_table(successful)
            logging.info("Final table created successfully")
        
        # Generate processing report
        report = {
            "total_urls": total_urls,
            "successful": len(successful),
            "failed": len(failed),
            "failed_urls": [{"url_id": r["url_id"], "error": r["error"]} for r in failed],
            "timestamp": time.time()
        }
        
        report_file = Path(config.OUTPUT_DIR) / "processing_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Processing report saved to {report_file}")
        logging.info("Pipeline execution completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Pipeline failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    force = False
    main(force)