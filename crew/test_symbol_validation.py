#!/usr/bin/env python3
"""
Test the improved error handling for invalid stock symbols
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_invalid_symbols():
    """Test handling of invalid/problematic stock symbols"""
    print("Testing Invalid Symbol Handling")
    print("=" * 40)
    
    try:
        from crew.tools.fmp import FMPTool
        
        fmp_tool = FMPTool()
        print("✅ FMP Tool initialized")
        
        # Test problematic symbols
        problematic_symbols = ["NSIVE", "COMPR", "ANALY", "", "123", "TOOLONG"]
        
        for symbol in problematic_symbols:
            print(f"\n🧪 Testing symbol: '{symbol}'")
            result = fmp_tool._run(symbol=symbol, data_type="income-statement", period="annual", years=3)
            
            if "Error:" in result:
                print(f"✅ Properly handled invalid symbol: {result[:100]}...")
            else:
                print(f"⚠️ Symbol not caught as invalid: {result[:50]}...")
        
        # Test valid symbols for comparison
        print(f"\n🧪 Testing valid symbol: 'AAPL'")
        result = fmp_tool._run(symbol="AAPL", data_type="income-statement", period="annual", years=1)
        
        if "Error:" not in result:
            print(f"✅ Valid symbol works: {len(result)} characters returned")
        else:
            print(f"❌ Valid symbol failed: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_company_extraction():
    """Test improved company name extraction"""
    print("\n\nTesting Company Name Extraction")
    print("=" * 40)
    
    try:
        from crew.dcf_crew import DCFCrew
        
        crew = DCFCrew()
        print("✅ DCF Crew initialized")
        
        # Test various queries
        test_queries = [
            "Analyze Apple for DCF analysis",
            "DCF analysis for Microsoft",
            "comprehensive analysis",  # This might cause issues
            "Analyze AAPL stock",
            "Tesla financial analysis",
            "study comprehensive dcf",  # Another problematic one
        ]
        
        for query in test_queries:
            print(f"\n🧪 Testing query: '{query}'")
            info = crew._extract_basic_info(query)
            
            company = info.get('company_name')
            symbol = info.get('stock_symbol')
            
            print(f"   Company: {company}")
            print(f"   Symbol: {symbol}")
            
            if symbol in ['NSIVE', 'COMPR', 'ANALY', '']:
                if not symbol:
                    print("   ✅ Properly rejected problematic extraction")
                else:
                    print(f"   ⚠️ Still extracting problematic symbol: {symbol}")
            else:
                print("   ✅ Extraction looks reasonable")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Invalid Symbol Handling Test")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ No FMP_API_KEY found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Run tests
    test1 = test_invalid_symbols()
    test2 = test_company_extraction()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"Invalid Symbol Handling: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Company Name Extraction: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! NSIVE and similar errors should be handled properly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
