#!/usr/bin/env python3
"""
Example usage of the DCF Analysis Crew

This script demonstrates how to use the DCF analysis system with various queries.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crew.dcf_crew import create_dcf_crew


def run_example_analysis():
    """Run example DCF analysis"""
    
    print("DCF Analysis Crew - Example Usage")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create the crew
    try:
        crew = create_dcf_crew()
        print("✅ DCF Crew initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing crew: {e}")
        return
    
    # Example queries to test
    example_queries = [
        "Analyze Apple Inc for DCF analysis with 5 years of annual data",
        "Calculate DCF metrics for Microsoft",
        "DCF analysis for AAPL stock",
        "Analyze Tesla for comprehensive financial analysis"
    ]
    
    print("\nAvailable example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Let user choose or run first example
    try:
        choice = input("\nEnter query number (1-4) or press Enter for query 1: ").strip()
        
        if choice == "":
            choice = "1"
        
        if choice.isdigit() and 1 <= int(choice) <= len(example_queries):
            selected_query = example_queries[int(choice) - 1]
        else:
            print("Invalid choice, using first example.")
            selected_query = example_queries[0]
        
        print(f"\nRunning analysis for: {selected_query}")
        print("-" * 60)
        
        # Run the analysis
        result = crew.analyze_company(selected_query)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETED!")
        print("="*80)
        print(result)
        print("="*80)
        
        print(f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Check the 'financial_data' directory for saved CSV and Excel files.")
        
    except KeyboardInterrupt:
        print("\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")


def test_fmp_tool():
    """Test the FMP tool directly"""
    print("Testing FMP Tool directly...")
    print("-" * 30)
    
    try:
        from crew.tools.fmp import fmp_tool
        
        # Test with a simple query
        print("Testing data fetch for Apple (AAPL)...")
        data = fmp_tool.get_dcf_data("AAPL", "annual", 3)
        
        if data and "error" not in data:
            print("✅ FMP Tool working correctly!")
            print(f"   Retrieved {data.get('years_of_data', 0)} years of data")
            print(f"   Company: {data.get('symbol', 'Unknown')}")
            
            # Save test data
            csv_path = fmp_tool.save_to_csv(data, "AAPL_Test_Data")
            excel_path = fmp_tool.save_to_excel(data, "AAPL_Test_Data")
            print(f"   Test files saved:")
            print(f"   - CSV: {csv_path}")
            print(f"   - Excel: {excel_path}")
        else:
            print("❌ FMP Tool error:", data.get('error', 'Unknown error'))
            
    except Exception as e:
        print(f"❌ Error testing FMP tool: {e}")


if __name__ == "__main__":
    print("DCF Analysis Example Script")
    print("=" * 40)
    
    # Check if user wants to test FMP tool only
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        test_fmp_tool()
    else:
        run_example_analysis()
