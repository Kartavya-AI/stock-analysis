#!/usr/bin/env python3
"""
Simple test to verify the DCF system is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("Simple DCF Test")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ No FMP_API_KEY found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Test FMP tool
        print("\nTesting FMP Tool...")
        from crew.tools.fmp import FMPTool
        
        fmp_tool = FMPTool()
        print("✅ FMP Tool initialized")
        
        # Quick test
        data = fmp_tool.get_dcf_data("AAPL", "annual", 1)
        if data and "error" not in data:
            print("✅ FMP Tool working correctly")
        else:
            print("❌ FMP Tool error")
            return
        
        # Test crew import
        print("\nTesting Crew import...")
        from crew.dcf_crew import create_dcf_crew
        print("✅ Crew import successful")
        
        # Test crew creation
        print("Creating crew...")
        crew = create_dcf_crew()
        print("✅ Crew created successfully")
        
        # Test basic query parsing
        query = "Analyze Apple for DCF analysis"
        info = crew._extract_basic_info(query)
        print(f"✅ Query parsed: {info.get('company_name')} -> {info.get('stock_symbol')}")
        
        print("\n🎉 All basic tests passed!")
        print("The system is ready to use.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
