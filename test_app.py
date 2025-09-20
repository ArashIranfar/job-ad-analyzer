# #!/usr/bin/env python3
# """
# Quick test script for Job Ad Analyzer
# """

# import logging
# import os
# import sys
# from pathlib import Path

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent / "src"))

# from src.scraper import WebScraper
# from src.llm_client import LLMClient
# from src.utils import setup_logging, create_sample_files
# import config


# def test_environment():
#     """Test environment setup"""
#     print("🔍 Testing environment setup...")
    
#     issues = []
    
#     # Check API key
#     if not config.LLM_API_KEY:
#         issues.append("❌ OPENAI_API_KEY not set in environment")
#     else:
#         print("✅ API key found")
    
#     # Check directories
#     try:
#         from src.utils import ensure_directories
#         ensure_directories()
#         print("✅ Directory structure OK")
#     except Exception as e:
#         issues.append(f"❌ Directory setup failed: {e}")
    
#     # Check sample files
#     if not config.URLS_FILE.exists():
#         issues.append("❌ URLs file missing: data/input/urls.txt")
#     else:
#         print("✅ URLs file found")
        
#     if not config.PROMPT_FILE.exists():
#         issues.append("❌ Prompt file missing: data/input/master_prompt.txt") 
#     else:
#         print("✅ Master prompt file found")
    
#     return issues


# def test_scraper():
#     """Test web scraper"""
#     print("\n🕷️ Testing web scraper...")
    
#     # Test with a real website
#     test_url = "https://httpbin.org/html"  # Simple test page
    
#     try:
#         scraper = WebScraper()
#         result = scraper.test_scraping(test_url)
        
#         if result["success"]:
#             print("✅ Scraper working")
#             print(f"   Status: {result['status_code']}")
#             print(f"   Title: {result['title']}")
#             print(f"   Content length: {result['content_length']}")
#         else:
#             print(f"❌ Scraper failed: {result['error']}")
#             return False
            
#     except Exception as e:
#         print(f"❌ Scraper test failed: {e}")
#         return False
    
#     return True


# def test_llm_client():
#     """Test LLM client"""
#     print("\n🤖 Testing LLM client...")
    
#     if not config.LLM_API_KEY:
#         print("❌ Cannot test LLM - no API key")
#         return False
    
#     try:
#         client = LLMClient()
        
#         # Test connection
#         if client.test_connection():
#             print("✅ LLM connection working")
            
#             # Test with sample job ad
#             sample_content = """
#             Software Engineer Position
            
#             We are looking for a skilled Software Engineer to join our team.
            
#             Requirements:
#             - 3+ years of Python experience
#             - Experience with web frameworks
#             - Bachelor's degree in Computer Science
            
#             Location: San Francisco, CA
#             Salary: $100,000 - $130,000
#             Type: Full-time
#             """
            
#             sample_prompt = """Extract job information as JSON:
#             {
#                 "job_title": "title",
#                 "location": "location", 
#                 "salary_min": 0,
#                 "salary_max": 0
#             }"""
            
#             response = client.analyze_job_ad(sample_content, sample_prompt, "test")
            
#             if response:
#                 print("✅ LLM analysis working")
#                 print(f"   Sample response: {response}")
#             else:
#                 print("❌ LLM analysis failed")
#                 return False
                
#         else:
#             print("❌ LLM connection failed")
#             return False
            
#     except Exception as e:
#         print(f"❌ LLM test failed: {e}")
#         return False
    
#     return True


# def run_mini_pipeline():
#     """Run a mini version of the pipeline"""
#     print("\n🚀 Running mini pipeline test...")
    
#     try:
#         # Use httpbin for a predictable test
#         test_urls = ["https://httpbin.org/html"]
        
#         # Create test prompt
#         test_prompt = """Please analyze this content and return JSON:
#         {"content_type": "description of content", "success": true}"""
        
#         scraper = WebScraper()
#         llm_client = LLMClient()
        
#         for i, url in enumerate(test_urls):
#             print(f"Processing test URL {i+1}: {url}")
            
#             # Scrape
#             content = scraper.scrape_url(url, f"test_{i+1}")
#             if not content:
#                 print("❌ Scraping failed")
#                 continue
                
#             print(f"✅ Scraped {len(content)} characters")
            
#             # Analyze with LLM
#             if config.LLM_API_KEY:
#                 response = llm_client.analyze_job_ad(content, test_prompt, f"test_{i+1}")
#                 if response:
#                     print(f"✅ LLM analysis successful: {response}")
#                 else:
#                     print("❌ LLM analysis failed")
#             else:
#                 print("⚠️ Skipping LLM test - no API key")
        
#         print("✅ Mini pipeline test completed")
#         return True
        
#     except Exception as e:
#         print(f"❌ Mini pipeline failed: {e}")
#         return False


# def main():
#     """Run all tests"""
#     print("🧪 Job Ad Analyzer - Quick Test\n")
    
#     # Setup logging
#     setup_logging()
    
#     # Create sample files if they don't exist
#     create_sample_files()
    
#     # Run tests
#     all_passed = True
    
#     # Test environment
#     issues = test_environment()
#     if issues:
#         print("\n❌ Environment issues:")
#         for issue in issues:
#             print(f"  {issue}")
#         all_passed = False
    
#     # Test scraper
#     if not test_scraper():
#         all_passed = False
    
#     # Test LLM (optional)
#     if config.LLM_API_KEY:
#         if not test_llm_client():
#             all_passed = False
#     else:
#         print("\n⚠️ Skipping LLM tests - set OPENAI_API_KEY to test")
    
#     # Run mini pipeline
#     if all_passed and config.LLM_API_KEY:
#         run_mini_pipeline()
    
#     # Summary
#     print(f"\n{'='*50}")
#     if all_passed:
#         print("🎉 All tests passed! Your app is ready to use.")
#         print("\nTo run the full pipeline:")
#         print("1. Add real job URLs to data/input/urls.txt") 
#         print("2. Run: python main.py")
#     else:
#         print("❌ Some tests failed. Fix the issues above before running the full pipeline.")
    
#     print(f"{'='*50}")


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Debug LLM responses to see what's going wrong
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import config
from src.utils import setup_logging, load_text_file
from src.scraper import WebScraper
from src.llm_client import LLMClient


def debug_llm_response():
    """Debug what the LLM is actually returning"""
    
    setup_logging()
    
    # Check if we have a saved LLM response file
    response_files = list(config.PROCESSED_DATA_DIR.glob("*_llm_response.json"))
    
    if response_files:
        print("🔍 Found LLM response files:")
        for file in response_files:
            print(f"  - {file.name}")
        
        # Load the most recent one
        latest_file = max(response_files, key=lambda x: x.stat().st_mtime)
        print(f"\n📄 Analyzing: {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                debug_data = json.load(f)
            
            print(f"\n📊 Response Details:")
            print(f"  URL ID: {debug_data.get('url_id')}")
            print(f"  Model: {debug_data.get('model')}")
            print(f"  Prompt Length: {debug_data.get('prompt_length')} chars")
            print(f"  Response Length: {debug_data.get('response_length')} chars")
            
            raw_response = debug_data.get('raw_response', '')
            print(f"\n📝 Raw LLM Response:")
            print("="*60)
            print(raw_response)
            print("="*60)
            
            # Try to find JSON manually
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}')
            
            if json_start != -1 and json_end != -1:
                potential_json = raw_response[json_start:json_end + 1]
                print(f"\n🔧 Extracted JSON (chars {json_start}-{json_end}):")
                print("-"*40)
                print(potential_json)
                print("-"*40)
                
                # Try to parse it
                try:
                    parsed = json.loads(potential_json)
                    print("\n✅ JSON is valid!")
                    print("🗂️ Keys found:", list(parsed.keys()))
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON parsing failed: {e}")
                    print("🔧 Trying to fix common issues...")
                    
                    # Try basic fixes
                    fixed_json = fix_json_issues(potential_json)
                    try:
                        parsed = json.loads(fixed_json)
                        print("✅ Fixed JSON is valid!")
                        print("🗂️ Keys found:", list(parsed.keys()))
                        return True
                    except json.JSONDecodeError as e2:
                        print(f"❌ Still couldn't fix JSON: {e2}")
                        return False
            else:
                print("\n❌ No JSON brackets found in response")
                print("🤔 The LLM might be returning explanation text instead of JSON")
                return False
                
        except Exception as e:
            print(f"❌ Error reading debug file: {e}")
            return False
    
    else:
        print("❌ No LLM response debug files found")
        print("🔧 Let's test the LLM directly...")
        return test_llm_directly()


def fix_json_issues(json_text):
    """Try to fix common JSON issues"""
    import re
    
    # Remove trailing commas
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    
    # Fix unquoted keys (basic attempt)
    json_text = re.sub(r'(\w+):', r'"\1":', json_text)
    
    # Fix single quotes to double quotes
    json_text = json_text.replace("'", '"')
    
    return json_text


def test_llm_directly():
    """Test LLM with a simple request"""
    
    print("\n🧪 Testing LLM directly...")
    
    try:
        llm_client = LLMClient()
        
        # Simple test
        simple_prompt = """Please respond with ONLY this JSON and nothing else:
{
    "test": "success",
    "message": "This is a test response"
}"""
        
        print("📤 Sending simple test prompt...")
        
        from langchain_core.messages import HumanMessage
        response = llm_client.client.invoke([HumanMessage(content=simple_prompt)])
        
        print(f"\n📥 LLM Response:")
        print("="*40)
        print(response.content)
        print("="*40)
        
        # Try to parse
        try:
            test_json = json.loads(response.content.strip())
            print("✅ Simple JSON test passed!")
            return True
        except json.JSONDecodeError:
            print("❌ LLM is not returning pure JSON")
            print("🔧 This suggests the LLM is adding extra text")
            return False
            
    except Exception as e:
        print(f"❌ Direct LLM test failed: {e}")
        return False


def suggest_fixes():
    """Suggest potential fixes"""
    
    print("\n💡 Potential Solutions:")
    print("="*50)
    
    print("1. 🎯 PROMPT ISSUE:")
    print("   - Your prompt might be too complex")
    print("   - Try adding: 'RESPOND WITH ONLY JSON, NO OTHER TEXT'")
    print("   - Or: 'Do not include any explanations or text outside the JSON'")
    
    print("\n2. 🤖 MODEL ISSUE:")
    print("   - Some models ignore JSON-only instructions")
    print("   - Try a different model (gpt-4, gpt-3.5-turbo)")
    print("   - Check if your API endpoint supports structured output")
    
    print("\n3. 🔧 PARSING ISSUE:")
    print("   - The LLM might be returning valid JSON with extra text")
    print("   - We can improve the JSON extraction logic")
    
    print("\n4. 🌐 API ISSUE:")
    print("   - Check if you're using a custom API endpoint")
    print("   - Verify your API key and model access")
    
    print("\n🚀 Quick Fix: Try running with a simpler prompt first!")


def main():
    """Main debug function"""
    
    print("🐛 LLM Response Debugger\n")
    
    success = debug_llm_response()
    
    if not success:
        suggest_fixes()
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()