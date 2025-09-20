"""
Data processing module for Job Ad Analyzer
"""

import logging
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from collections import Counter
import config
from src.utils import load_json_file, save_json_file


class DataProcessor:
    """Process individual job ad JSONs into structured tables"""
    
    def __init__(self):
        logging.debug("DataProcessor initialized")
    
    # def create_final_table(self, results: List[Dict[str, Any]]) -> None:
    #     """
    #     Create final structured table from individual job ad results
        
    #     Args:
    #         results: List of successful processing results
    #     """
    #     try:
    #         logging.info(f"Processing {len(results)} job ads into final table")
            
    #         # Extract all job data
    #         job_data_list = []
    #         for result in results:
    #             if result.get("data"):
    #                 job_data = result["data"].copy()
    #                 job_data["url_id"] = result["url_id"]
    #                 job_data["source_url"] = result["url"]
    #                 job_data_list.append(job_data)
            
    #         if not job_data_list:
    #             logging.error("No valid job data to process")
    #             return
            
    #         # Analyze field frequency across all jobs
    #         field_analysis = self._analyze_field_frequency(job_data_list)
    #         logging.info(f"Analyzed {len(field_analysis)} unique fields")
            
    #         # Create unified schema
    #         schema = self._create_unified_schema(field_analysis)
    #         logging.info(f"Created schema with {len(schema['standard_fields'])} standard fields")
            
    #         # Transform data to unified format
    #         unified_data = self._transform_to_unified_format(job_data_list, schema)
            
    #         # Create DataFrames
    #         df = self._create_dataframe(unified_data)
            
    #         # Save outputs
    #         self._save_outputs(df, unified_data, schema, field_analysis)
            
    #         logging.info("Final table creation completed successfully")
            
    #     except Exception as e:
    #         logging.error(f"Error creating final table: {e}")
    #         raise
    
    def create_final_table(self, results: List[Dict[str, Any]]) -> None:
        """
        Create final structured table from individual job ad results
        
        Args:
            results: List of successful processing results
        """
        try:
            logging.info(f"Processing {len(results)} job ads into final table")
            
            # Extract all job data
            job_data_list = []
            for result in results:
                if result.get("data"):
                    # **HERE'S WHERE YOU CALL THE FLATTEN FUNCTION**
                    raw_data = result["data"].copy()
                    
                    # Flatten the nested structure from LLM response
                    flattened_data = self._flatten_nested_data(raw_data)
                    
                    # Add metadata
                    flattened_data["url_id"] = result["url_id"]
                    flattened_data["source_url"] = result["url"]
                    
                    job_data_list.append(flattened_data)
            
            if not job_data_list:
                logging.error("No valid job data to process")
                return
            
            # Rest of the method remains the same...
            # Analyze field frequency across all jobs
            field_analysis = self._analyze_field_frequency(job_data_list)
            logging.info(f"Analyzed {len(field_analysis)} unique fields")
            
            # Create unified schema
            schema = self._create_unified_schema(field_analysis)
            logging.info(f"Created schema with {len(schema['standard_fields'])} standard fields")
            
            # Transform data to unified format
            unified_data = self._transform_to_unified_format(job_data_list, schema)
            
            # Create DataFrames
            df = self._create_dataframe(unified_data)
            
            # Save outputs
            self._save_outputs(df, unified_data, schema, field_analysis)
            
            logging.info("Final table creation completed successfully")
            
        except Exception as e:
            logging.error(f"Error creating final table: {e}")
            raise
    
    def _analyze_field_frequency(self, job_data_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze frequency and types of fields across all job ads"""
        
        field_stats = {}
        total_jobs = len(job_data_list)
        
        for job_data in job_data_list:
            for field, value in job_data.items():
                if field not in field_stats:
                    field_stats[field] = {
                        'count': 0,
                        'frequency': 0.0,
                        'types': Counter(),
                        'sample_values': [],
                        'non_null_count': 0
                    }
                
                field_stats[field]['count'] += 1
                
                if value is not None and value != "":
                    field_stats[field]['non_null_count'] += 1
                    field_stats[field]['types'][type(value).__name__] += 1
                    
                    # Store sample values (limit to 5)
                    if len(field_stats[field]['sample_values']) < 5:
                        sample_val = str(value)[:100]  # Truncate long values
                        if sample_val not in field_stats[field]['sample_values']:
                            field_stats[field]['sample_values'].append(sample_val)
        
        # Calculate frequencies
        for field in field_stats:
            field_stats[field]['frequency'] = field_stats[field]['count'] / total_jobs
            field_stats[field]['non_null_frequency'] = field_stats[field]['non_null_count'] / total_jobs
        
        return field_stats
    
    def _create_unified_schema(self, field_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create unified schema based on field analysis"""
        
        # Standard fields that should always be included
        priority_fields = {
            'url_id', 'source_url', 'job_title', 'company', 'location',
            'salary_min', 'salary_max', 'currency', 'employment_type',
            'experience_years', 'remote_work', 'required_skills',
            'education_level', 'industry', 'department'
        }
        
        # Fields that appear frequently enough to be standard columns
        frequent_fields = {
            field for field, stats in field_analysis.items()
            if stats['non_null_frequency'] >= config.MIN_FIELD_FREQUENCY
        }
        
        # Combine priority and frequent fields
        standard_fields = priority_fields.union(frequent_fields)
        
        # Remaining fields go to misc
        misc_fields = set(field_analysis.keys()) - standard_fields
        
        schema = {
            'standard_fields': list(standard_fields),
            'misc_fields': list(misc_fields),
            'field_analysis': field_analysis
        }
        
        return schema
    
    def _transform_to_unified_format(self, job_data_list: List[Dict[str, Any]], 
                                   schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform job data to unified format"""
        
        unified_data = []
        standard_fields = schema['standard_fields']
        misc_fields = schema['misc_fields']
        
        for job_data in job_data_list:
            unified_job = {}
            
            # Add standard fields
            for field in standard_fields:
                unified_job[field] = job_data.get(field, None)
            
            # Collect misc fields
            misc_data = {}
            for field in misc_fields:
                if field in job_data and job_data[field] is not None:
                    misc_data[field] = job_data[field]
            
            # Limit misc data size
            if len(misc_data) > config.MAX_MISC_ITEMS:
                # Keep most "interesting" items (non-empty, varied values)
                misc_items = list(misc_data.items())[:config.MAX_MISC_ITEMS]
                misc_data = dict(misc_items)
            
            unified_job[config.MISC_COLUMN_NAME] = misc_data if misc_data else None
            
            unified_data.append(unified_job)
        
        return unified_data
    
    def _create_dataframe(self, unified_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create pandas DataFrame from unified data"""
        
        df = pd.DataFrame(unified_data)
        
        # Convert misc column to JSON string for CSV compatibility
        if config.MISC_COLUMN_NAME in df.columns:
            df[config.MISC_COLUMN_NAME] = df[config.MISC_COLUMN_NAME].apply(
                lambda x: json.dumps(x) if x is not None else None
            )
        
        # Clean up data types
        df = self._clean_dataframe_types(df)
        
        return df
    
    def _clean_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and optimize DataFrame data types"""
        
        # Convert salary columns to numeric
        salary_cols = [col for col in df.columns if 'salary' in col.lower()]
        for col in salary_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert experience to numeric
        if 'experience_years' in df.columns:
            df['experience_years'] = pd.to_numeric(df['experience_years'], errors='coerce')
        
        # Convert boolean columns
        boolean_cols = [col for col in df.columns if 'remote' in col.lower() or col.endswith('_flag')]
        for col in boolean_cols:
            if col in df.columns:
                df[col] = df[col].astype('boolean')
        
        # Convert list columns to string representation
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains lists
                sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample_val, list):
                    df[col] = df[col].apply(
                        lambda x: ', '.join(str(item) for item in x) if isinstance(x, list) else x
                    )
        
        return df
    
    def _save_outputs(self, df: pd.DataFrame, unified_data: List[Dict[str, Any]], 
                     schema: Dict[str, Any], field_analysis: Dict[str, Dict[str, Any]]) -> None:
        """Save all output files"""
        
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        
        # Save CSV with proper UTF-8 encoding for Farsi
        csv_file = config.OUTPUT_DIR / f"job_ads_analysis_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')  # BOM for Excel compatibility
        logging.info(f"Saved CSV: {csv_file}")
        
        # Save Excel if openpyxl is available
        try:
            excel_file = config.OUTPUT_DIR / f"job_ads_analysis_{timestamp}.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=config.EXCEL_SHEET_NAME, index=False)
                
                # Add field analysis sheet
                field_df = pd.DataFrame.from_dict(field_analysis, orient='index')
                field_df.to_excel(writer, sheet_name='Field_Analysis')
            
            logging.info(f"Saved Excel: {excel_file}")
        except ImportError:
            logging.warning("openpyxl not available, skipping Excel output")
        
        # Save JSON with full data
        json_file = config.OUTPUT_DIR / f"job_ads_full_data_{timestamp}.json"
        full_data = {
            'metadata': {
                'total_jobs': len(unified_data),
                'timestamp': timestamp,
                'schema': schema
            },
            'jobs': unified_data
        }
        save_json_file(full_data, json_file)
        logging.info(f"Saved JSON: {json_file}")
        
        # Save field analysis report
        analysis_file = config.OUTPUT_DIR / f"field_analysis_report_{timestamp}.json"
        save_json_file(field_analysis, analysis_file)
        logging.info(f"Saved field analysis: {analysis_file}")
        
        # Save latest versions (without timestamp) with proper encoding
        latest_csv = config.OUTPUT_DIR / "job_ads_analysis_latest.csv"
        df.to_csv(latest_csv, index=False, encoding='utf-8-sig')  # BOM for Excel compatibility
        
        latest_json = config.OUTPUT_DIR / "job_ads_full_data_latest.json"
        save_json_file(full_data, latest_json)
        
        logging.info("Saved latest versions of outputs")
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of the processing results"""
        
        successful = [r for r in results if r.get("data")]
        failed = [r for r in results if not r.get("data")]
        
        summary = {
            'processing_summary': {
                'total_urls': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) if results else 0
            },
            'failed_urls': [
                {
                    'url_id': r['url_id'],
                    'url': r['url'],
                    'error': r.get('error', 'Unknown error')
                }
                for r in failed
            ]
        }
        
        if successful:
            # Analyze successful extractions
            all_fields = set()
            field_coverage = Counter()
            
            for result in successful:
                job_data = result['data']
                job_fields = set(job_data.keys())
                all_fields.update(job_fields)
                
                for field in job_fields:
                    if job_data[field] is not None:
                        field_coverage[field] += 1
            
            summary['field_analysis'] = {
                'total_unique_fields': len(all_fields),
                'field_coverage': {
                    field: {
                        'count': count,
                        'percentage': (count / len(successful)) * 100
                    }
                    for field, count in field_coverage.most_common()
                }
            }
        
        return summary
    
    def load_processed_data(self) -> List[Dict[str, Any]]:
        """Load all processed JSON files"""
        processed_files = list(config.PROCESSED_DATA_DIR.glob("url_*.json"))
        results = []
        
        for file_path in processed_files:
            try:
                data = load_json_file(file_path)
                results.append(data)
            except Exception as e:
                logging.error(f"Failed to load {file_path}: {e}")
        
        logging.info(f"Loaded {len(results)} processed files")
        return results
    
    def _flatten_nested_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested JSON structure from LLM response"""
        flattened = {}
        
        # Handle standard extraction
        if 'standard_extraction' in data:
            for key, value in data['standard_extraction'].items():
                flattened[key] = value
        
        # Handle payment analysis
        if 'payment_analysis' in data:
            flattened['estimated_salary_irr'] = data['payment_analysis'].get('estimated_range_IRR')
            flattened['salary_reasoning'] = data['payment_analysis'].get('reasoning')
        
        # Handle candidate fit
        if 'candidate_fit' in data:
            flattened['fit_tier'] = data['candidate_fit'].get('tier')
            flattened['fit_summary'] = data['candidate_fit'].get('summary')
            flattened['fit_strengths'] = ', '.join(data['candidate_fit'].get('strengths', []))
            flattened['fit_gaps'] = ', '.join(data['candidate_fit'].get('gaps', []))
        
        # Handle overqualified assessment
        if 'is_overqualified' in data:
            flattened['is_overqualified'] = data['is_overqualified'].get('value')
            flattened['overqualified_reasoning'] = data['is_overqualified'].get('reasoning')
        
        # Handle growth potential
        if 'growth_potential' in data:
            flattened['growth_potential'] = data['growth_potential']
        
        return flattened