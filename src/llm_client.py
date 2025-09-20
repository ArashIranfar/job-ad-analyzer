# """
# LLM client for Job Ad Analyzer
# """

# import logging
# import json
# import time
# from typing import Optional, Dict, Any
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# import config
# from src.utils import save_json_file, validate_json_structure


# class LLMClient:
#     """Client for interacting with Language Models"""
    
#     def __init__(self):
#         if config.LLM_MODEL.startswith("gpt"):
#             self.client = ChatOpenAI(
#                 api_key=config.LLM_API_KEY,
#                 base_url=config.LLM_BASE_URL,
#                 model=config.LLM_MODEL,
#                 temperature=config.TEMPERATURE,
#                 max_tokens=config.MAX_TOKENS,
#                 timeout=config.TIMEOUT
#             )
#         else:
#             # Add support for other LLM providers here
#             raise ValueError(f"Unsupported LLM model: {config.LLM_MODEL}")
        
#         self.model = config.LLM_MODEL
#         logging.debug(f"LLMClient initialized with model: {self.model}")
    
#     @retry(
#         stop=stop_after_attempt(config.MAX_RETRIES),
#         wait=wait_exponential(multiplier=config.RETRY_DELAY, min=1, max=60),
#         retry=retry_if_exception_type((Exception,))  # Catch all exceptions for retry
#     )
#     def analyze_job_ad(self, content: str, master_prompt: str, url_id: str) -> Optional[Dict[str, Any]]:
#         """
#         Send job ad content to LLM for analysis
        
#         Args:
#             content: Job ad text content
#             master_prompt: Master prompt with instructions
#             url_id: Unique identifier for debugging
        
#         Returns:
#             Parsed JSON response or None if failed
#         """
#         try:
#             # Prepare the full prompt
#             full_prompt = f"{master_prompt}\n\nJob Advertisement Content:\n{content}"
            
#             logging.debug(f"Sending request to LLM for {url_id}")
            
#             # Create messages
#             messages = [
#                 SystemMessage(content="You are a job advertisement analyzer. Extract structured information from job postings and return valid JSON only."),
#                 HumanMessage(content=full_prompt)
#             ]
            
#             # Make API request
#             response = self.client.invoke(messages)
            
#             # Extract response content
#             response_text = response.content.strip()
            
#             # Log the raw response for debugging
#             if config.VERBOSE_LOGGING:
#                 logging.debug(f"Raw LLM response for {url_id}: {response_text[:500]}...")
            
#             # Parse JSON response
#             parsed_response = self._parse_json_response(response_text, url_id)
            
#             if parsed_response:
#                 # Save individual response for debugging
#                 response_file = config.PROCESSED_DATA_DIR / f"{url_id}_llm_response.json"
#                 debug_data = {
#                     "url_id": url_id,
#                     "model": self.model,
#                     "prompt_length": len(full_prompt),
#                     "response_length": len(response_text),
#                     "raw_response": response_text,
#                     "parsed_response": parsed_response,
#                     "usage": getattr(response, 'usage_metadata', None)  # LangChain usage info if available
#                 }
#                 save_json_file(debug_data, response_file)
                
#                 logging.info(f"Successfully analyzed {url_id}")
#                 return parsed_response
#             else:
#                 logging.error(f"Failed to parse JSON response for {url_id}")
#                 return None
                
#         except Exception as e:
#             logging.error(f"Error analyzing {url_id}: {e}")
#             raise  # Let tenacity handle the retry
    
#     def _parse_json_response(self, response_text: str, url_id: str) -> Optional[Dict[str, Any]]:
#         """Parse JSON from LLM response"""
#         try:
#             # Clean the response text
#             response_text = response_text.strip()
            
#             # Find JSON in response (sometimes LLM adds extra text)
#             json_start = response_text.find('{')
#             json_end = response_text.rfind('}')
            
#             if json_start == -1 or json_end == -1:
#                 logging.error(f"No JSON found in response for {url_id}")
#                 return None
            
#             json_text = response_text[json_start:json_end + 1]
            
#             # Parse JSON
#             parsed = json.loads(json_text)
            
#             # Validate structure
#             if not validate_json_structure(parsed, config.REQUIRED_JSON_FIELDS):
#                 logging.warning(f"Invalid JSON structure for {url_id}")
            
#             # Clean and normalize the data
#             cleaned_data = self._clean_parsed_data(parsed)
            
#             return cleaned_data
            
#         except json.JSONDecodeError as e:
#             logging.error(f"JSON parsing failed for {url_id}: {e}")
#             logging.debug(f"Raw response: {response_text[:1000]}")
            
#             # Try to fix common JSON issues
#             fixed_response = self._fix_common_json_issues(response_text)
#             if fixed_response != response_text:
#                 try:
#                     return json.loads(fixed_response)
#                 except json.JSONDecodeError:
#                     pass
            
#             return None
        
#         except Exception as e:
#             logging.error(f"Unexpected error parsing response for {url_id}: {e}")
#             return None
    
#     def _fix_common_json_issues(self, json_text: str) -> str:
#         """Attempt to fix common JSON formatting issues"""
#         import re
        
#         # Remove trailing commas
#         json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
#         # Fix unquoted keys (basic attempt)
#         json_text = re.sub(r'(\w+):', r'"\1":', json_text)
        
#         # Fix single quotes to double quotes
#         json_text = json_text.replace("'", '"')
        
#         return json_text
    
#     def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         """Clean and normalize parsed data"""
#         cleaned = {}
        
#         for key, value in data.items():
#             # Clean key names
#             clean_key = key.strip().lower().replace(' ', '_').replace('-', '_')
            
#             # Handle None/null values
#             if value in [None, "null", "None", "", "N/A", "n/a"]:
#                 cleaned[clean_key] = None
            
#             # Handle salary values
#             elif "salary" in clean_key and isinstance(value, str):
#                 from src.utils import normalize_salary
#                 cleaned[clean_key] = normalize_salary(value)
            
#             # Handle boolean values
#             elif isinstance(value, str) and value.lower() in ["true", "false", "yes", "no"]:
#                 cleaned[clean_key] = value.lower() in ["true", "yes"]
            
#             # Handle lists
#             elif isinstance(value, list):
#                 cleaned[clean_key] = [str(item).strip() for item in value if item]
            
#             # Handle nested dictionaries
#             elif isinstance(value, dict):
#                 cleaned[clean_key] = self._clean_parsed_data(value)
            
#             # Handle strings
#             elif isinstance(value, str):
#                 cleaned[clean_key] = value.strip()
            
#             else:
#                 cleaned[clean_key] = value
        
#         return cleaned
    
#     def test_connection(self) -> bool:
#         """Test LLM connection"""
#         try:
#             logging.info("Testing LLM connection...")
            
#             test_message = HumanMessage(content="Hello, please respond with 'OK'")
#             test_response = self.client.invoke([test_message])
            
#             response_text = test_response.content.strip()
#             success = "OK" in response_text.upper()
            
#             if success:
#                 logging.info("LLM connection test successful")
#             else:
#                 logging.error(f"LLM connection test failed: {response_text}")
            
#             return success
            
#         except Exception as e:
#             logging.error(f"LLM connection test failed: {e}")
#             return False
    
#     def estimate_tokens(self, text: str) -> int:
#         """Rough estimation of token count"""
#         # Very rough approximation: ~4 characters per token
#         return len(text) // 4
    
#     def get_model_info(self) -> Dict[str, Any]:
#         """Get information about the current model"""
#         return {
#             "model": self.model,
#             "max_tokens": config.MAX_TOKENS,
#             "temperature": config.TEMPERATURE,
#             "timeout": config.TIMEOUT
#         }

"""
LLM client for Job Ad Analyzer
"""

import logging
import json
import time
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config
from src.utils import save_json_file, validate_json_structure


class LLMClient:
    """Client for interacting with Language Models"""
    
    def __init__(self):
        # if config.LLM_MODEL.startswith("gpt"):
        self.client = ChatOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            model=config.LLM_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            timeout=config.TIMEOUT
        )
        # else:
        #     # Add support for other LLM providers here
        #     raise ValueError(f"Unsupported LLM model: {config.LLM_MODEL}")
        
        self.model = config.LLM_MODEL
        logging.debug(f"LLMClient initialized with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=config.RETRY_DELAY, min=1, max=60),
        retry=retry_if_exception_type((Exception,))  # Catch all exceptions for retry
    )
    # def analyze_job_ad(self, content: str, master_prompt: str, url_id: str) -> Optional[Dict[str, Any]]:
    #     """
    #     Send job ad content to LLM for analysis
        
    #     Args:
    #         content: Job ad text content
    #         master_prompt: Master prompt with instructions
    #         url_id: Unique identifier for debugging
        
    #     Returns:
    #         Parsed JSON response or None if failed
    #     """

    def _check_cached_llm_response(self, url_id: str) -> Optional[Dict[str, Any]]:
        """Check if we have a cached LLM response"""
        
        response_file = config.PROCESSED_DATA_DIR / f"{url_id}_llm_response.json"
        if response_file.exists():
            try:
                with open(response_file, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)
                
                parsed_response = debug_data.get('parsed_response')
                if parsed_response:
                    logging.debug(f"Found cached LLM response for {url_id}")
                    return parsed_response
                    
            except Exception as e:
                logging.warning(f"Error reading cached LLM response for {url_id}: {e}")
        
        return None

    def analyze_job_ad(self, content: str, master_prompt: str, url_id: str, force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Send job ad content to LLM for analysis with caching support
        """
        
        # Check cache first (unless force=True)
        if not force:
            cached_response = self._check_cached_llm_response(url_id)
            if cached_response:
                logging.info(f"Using cached LLM response for {url_id}")
                return cached_response
            
        try:
            # Prepare the full prompt
            full_prompt = f"{master_prompt}\n\nJob Advertisement Content:\n{content}"
            
            logging.debug(f"Sending request to LLM for {url_id}")
            
            # Create messages
            messages = [
                SystemMessage(content="You are a job advertisement analyzer. Extract structured information from job postings and return valid JSON only."),
                HumanMessage(content=full_prompt)
            ]
            
            # Make API request
            response = self.client.invoke(messages)
            
            # Extract response content
            response_text = response.content.strip()
            # print("raw response: " + response_text)
            
            # Log the raw response for debugging
            if config.VERBOSE_LOGGING:
                logging.debug(f"Raw LLM response for {url_id}: {response_text[:500]}...")
            
            # Parse JSON response
            parsed_response = self._parse_json_response(response_text, url_id)
            
            if parsed_response:
                # Save individual response for debugging
                response_file = config.PROCESSED_DATA_DIR / f"{url_id}_llm_response.json"
                debug_data = {
                    "url_id": url_id,
                    "model": self.model,
                    "prompt_length": len(full_prompt),
                    "response_length": len(response_text),
                    "raw_response": response_text,
                    "parsed_response": parsed_response,
                    "usage": getattr(response, 'usage_metadata', None)  # LangChain usage info if available
                }
                save_json_file(debug_data, response_file)
                
                logging.info(f"Successfully analyzed {url_id}")
                return parsed_response
            else:
                logging.error(f"Failed to parse JSON response for {url_id}")
                return None
                
        except Exception as e:
            logging.error(f"Error analyzing {url_id}: {e}")
            raise  # Let tenacity handle the retry
    
    def _parse_json_response(self, response_text: str, url_id: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response with improved extraction"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Strategy 1: Try to parse the whole response
            try:
                parsed = json.loads(response_text)
                logging.debug(f"Parsed entire response as JSON for {url_id}")
                return self._clean_parsed_data(parsed)
            except json.JSONDecodeError:
                pass
            
            # Strategy 2: Find JSON block within the response
            json_patterns = [
                (r'\{.*\}', 0),  # Find outermost braces
                (r'```json\s*(\{.*?\})\s*```', 1),  # JSON code block
                (r'```\s*(\{.*?\})\s*```', 1),  # Generic code block
            ]
            
            for pattern, group in json_patterns:
                import re
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    json_text = match.group(group) if group else match.group(0)
                    try:
                        parsed = json.loads(json_text)
                        logging.debug(f"Extracted JSON using pattern for {url_id}")
                        return self._clean_parsed_data(parsed)
                    except json.JSONDecodeError:
                        continue
            
            # Strategy 3: Manual brace matching for nested JSON
            json_start = response_text.find('{')
            if json_start != -1:
                brace_count = 0
                json_end = json_start
                
                for i, char in enumerate(response_text[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i
                            break
                
                if brace_count == 0:  # Found matching braces
                    json_text = response_text[json_start:json_end + 1]
                    try:
                        parsed = json.loads(json_text)
                        logging.debug(f"Extracted JSON using brace matching for {url_id}")
                        return self._clean_parsed_data(parsed)
                    except json.JSONDecodeError:
                        pass
            
            logging.error(f"No valid JSON found in response for {url_id}")
            logging.debug(f"Response preview: {response_text[:500]}...")
            
            # Save the problematic response for debugging
            debug_file = config.PROCESSED_DATA_DIR / f"{url_id}_failed_response.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Failed to parse JSON for {url_id}\n")
                f.write("="*50 + "\n")
                f.write(response_text)
            
            return None
            
        except Exception as e:
            logging.error(f"Unexpected error parsing response for {url_id}: {e}")
            return None
    
    def _fix_common_json_issues(self, json_text: str) -> str:
        """Attempt to fix common JSON formatting issues"""
        import re
        
        # Remove trailing commas
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix unquoted keys (basic attempt)
        json_text = re.sub(r'(\w+):', r'"\1":', json_text)
        
        # Fix single quotes to double quotes
        json_text = json_text.replace("'", '"')
        
        return json_text
    
    def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize parsed data"""
        cleaned = {}
        
        for key, value in data.items():
            # Clean key names
            clean_key = key.strip().lower().replace(' ', '_').replace('-', '_')
            
            # Handle None/null values
            if value in [None, "null", "None", "", "N/A", "n/a"]:
                cleaned[clean_key] = None
            
            # Handle salary values
            elif "salary" in clean_key and isinstance(value, str):
                from src.utils import normalize_salary
                cleaned[clean_key] = normalize_salary(value)
            
            # Handle boolean values
            elif isinstance(value, str) and value.lower() in ["true", "false", "yes", "no"]:
                cleaned[clean_key] = value.lower() in ["true", "yes"]
            
            # Handle lists
            elif isinstance(value, list):
                cleaned[clean_key] = [str(item).strip() for item in value if item]
            
            # Handle nested dictionaries
            elif isinstance(value, dict):
                cleaned[clean_key] = self._clean_parsed_data(value)
            
            # Handle strings
            elif isinstance(value, str):
                cleaned[clean_key] = value.strip()
            
            else:
                cleaned[clean_key] = value
        
        return cleaned
    
    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            logging.info("Testing LLM connection...")
            
            test_message = HumanMessage(content="Hello, please respond with 'OK'")
            test_response = self.client.invoke([test_message])
            
            response_text = test_response.content.strip()
            success = "OK" in response_text.upper()
            
            if success:
                logging.info("LLM connection test successful")
            else:
                logging.error(f"LLM connection test failed: {response_text}")
            
            return success
            
        except Exception as e:
            logging.error(f"LLM connection test failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        # Very rough approximation: ~4 characters per token
        return len(text) // 4
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model": self.model,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.TEMPERATURE,
            "timeout": config.TIMEOUT
        }