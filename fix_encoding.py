#!/usr/bin/env python3
"""
Fix encoding issues for Farsi text in CSV files
"""

import pandas as pd
import json
from pathlib import Path
import logging
import config
from src.utils import setup_logging


def fix_csv_encoding(csv_file_path: Path):
    """Fix encoding issues in CSV file"""
    print(f"🔧 Fixing encoding for: {csv_file_path}")
    
    try:
        # Try reading with different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1256', 'iso-8859-1']
        
        df = None
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(csv_file_path, encoding=encoding)
                print(f"✅ Successfully read with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("❌ Could not read CSV with any encoding")
            return False
        
        # Save with proper UTF-8-sig encoding
        output_path = csv_file_path.parent / f"{csv_file_path.stem}_fixed.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ Fixed CSV saved as: {output_path}")
        
        # Show sample of fixed data
        print("\n📋 Sample of fixed data:")
        print(df.head(2).to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing CSV: {e}")
        return False


def regenerate_table_from_json():
    """Regenerate the final table from JSON files with proper encoding"""
    print("🔄 Regenerating table from JSON files...")
    
    try:
        from src.processor import DataProcessor
        
        # Load all processed JSON files
        processor = DataProcessor()
        processed_files = list(config.PROCESSED_DATA_DIR.glob("url_*.json"))
        
        if not processed_files:
            print("❌ No processed JSON files found")
            return False
        
        results = []
        for file_path in processed_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("data"):
                        results.append(data)
            except Exception as e:
                print(f"⚠️ Error loading {file_path}: {e}")
        
        if not results:
            print("❌ No valid results found in JSON files")
            return False
        
        print(f"✅ Loaded {len(results)} valid results")
        
        # Regenerate table
        processor.create_final_table(results)
        
        print("✅ Table regenerated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating table: {e}")
        return False


def inspect_farsi_content():
    """Inspect Farsi content in the data"""
    print("🔍 Inspecting Farsi content...")
    
    try:
        # Check JSON files first (should have correct encoding)
        json_files = list(config.PROCESSED_DATA_DIR.glob("url_*_llm_response.json"))
        
        if json_files:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            print("📄 Sample from JSON file (should be readable):")
            if 'parsed_response' in data:
                for key, value in list(data['parsed_response'].items())[:5]:
                    print(f"  {key}: {value}")
            
            return True
        else:
            print("❌ No JSON response files found")
            return False
            
    except Exception as e:
        print(f"❌ Error inspecting content: {e}")
        return False


def main():
    """Main function to fix encoding issues"""
    print("🛠️  Farsi Encoding Fixer\n")
    
    # Setup logging
    setup_logging()
    
    # Check what files exist
    output_dir = config.OUTPUT_DIR
    csv_files = list(output_dir.glob("*.csv"))
    
    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
        print()
        
        # Inspect current content
        inspect_farsi_content()
        print()
        
        # Try to fix existing CSV files
        for csv_file in csv_files:
            fix_csv_encoding(csv_file)
            print()
    
    # Regenerate from JSON (recommended)
    print("🔄 Regenerating fresh table from JSON files...")
    regenerate_table_from_json()
    
    print("\n" + "="*50)
    print("✅ Encoding fix complete!")
    print(f"\nCheck these files:")
    print(f"  - {config.OUTPUT_DIR}/job_ads_analysis_latest.csv")
    print(f"  - {config.OUTPUT_DIR}/*_fixed.csv")
    print("\nTo view in Excel: Open CSV and select UTF-8 encoding when prompted")
    print("To view in terminal: Use 'head -5' or open with a UTF-8 capable editor")
    print("="*50)


if __name__ == "__main__":
    main()