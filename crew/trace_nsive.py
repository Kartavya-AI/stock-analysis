#!/usr/bin/env python3
"""
Trace through the NSIVE generation issue
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def trace_nsive_issue():
    """Trace through how NSIVE gets generated"""
    print("Tracing NSIVE Generation Issue")
    print("=" * 40)
    
    try:
        from crew.dcf_crew import DCFCrew
        
        crew = DCFCrew()
        print("✅ DCF Crew initialized")
        
        # Test various problematic queries
        problematic_queries = [
            "comprehensive analysis",
            "Analyze comprehensive for DCF",
            "comprehensive DCF analysis",
            "study comprehensive financial analysis",
            "comprehensive valuation"
        ]
        
        for query in problematic_queries:
            print(f"\n🧪 Testing problematic query: '{query}'")
            print("-" * 50)
            
            try:
                info = crew._extract_basic_info(query)
                
                print(f"Final result:")
                print(f"  Company: {info.get('company_name')}")
                print(f"  Symbol: {info.get('stock_symbol')}")
                print(f"  Period: {info.get('period')}")
                print(f"  Years: {info.get('years')}")
                
                # Test if this would cause problems in FMP tool
                symbol = info.get('stock_symbol')
                if symbol and symbol not in [None, '', 'Unknown']:
                    print(f"\n🔍 Testing symbol '{symbol}' in FMP tool...")
                    
                    from crew.tools.fmp import FMPTool
                    fmp_tool = FMPTool()
                    
                    result = fmp_tool._run(symbol=symbol, data_type="income-statement", period="annual", years=1)
                    
                    if "Error:" in result:
                        print(f"✅ FMP Tool caught the error: {result[:100]}...")
                    else:
                        print(f"❌ FMP Tool didn't catch the error - would try to fetch data!")
                
            except Exception as e:
                print(f"❌ Error during processing: {e}")
                import traceback
                traceback.print_exc()
        
        # Test with valid queries for comparison
        print(f"\n🧪 Testing valid query: 'Analyze Apple for DCF'")
        print("-" * 50)
        
        info = crew._extract_basic_info("Analyze Apple for DCF")
        print(f"Final result:")
        print(f"  Company: {info.get('company_name')}")
        print(f"  Symbol: {info.get('stock_symbol')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_symbol_extraction():
    """Test direct symbol extraction"""
    print("\n\nTesting Direct Symbol Extraction")
    print("=" * 40)
    
    try:
        from crew.dcf_crew import DCFCrew
        
        crew = DCFCrew()
        
        test_names = [
            "comprehensive",
            "comprehensive analysis", 
            "nsive",
            "Apple",
            "Microsoft",
            "AAPL",
            "analysis comprehensive"
        ]
        
        for name in test_names:
            print(f"\n🧪 Testing name: '{name}'")
            symbol = crew.extract_stock_symbol(name)
            print(f"Result: '{symbol}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("NSIVE Generation Trace")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ No FMP_API_KEY found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Run tests
    test1 = trace_nsive_issue()
    test2 = test_direct_symbol_extraction()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"NSIVE Issue Trace: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Direct Symbol Extraction: {'✅ PASS' if test2 else '❌ FAIL'}")

if __name__ == "__main__":
    main()
