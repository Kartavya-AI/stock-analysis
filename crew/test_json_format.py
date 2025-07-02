#!/usr/bin/env python3
"""
Test the JSON format output and parameter handling
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_fmp_tool_params():
    """Test FMP tool with various parameter formats"""
    print("Testing FMP Tool Parameter Handling")
    print("=" * 40)
    
    try:
        from crew.tools.fmp import FMPTool
        
        fmp_tool = FMPTool()
        print("✅ FMP Tool initialized")
        
        # Test 1: Standard parameters
        print("\n1. Testing standard parameters...")
        result1 = fmp_tool._run(symbol="AAPL", data_type="income-statement", period="annual", years=3)
        print(f"✅ Standard params work: {len(result1)} characters returned")
        
        # Test 2: LLM-style parameters (the problematic call)
        print("\n2. Testing LLM-style parameters...")
        result2 = fmp_tool._run(symbol="AAPL", data_type="income-statement", period="annual", years=3, sav=True)
        print(f"✅ LLM params work: {len(result2)} characters returned")
        
        # Test 3: Missing symbol (should handle gracefully)
        print("\n3. Testing missing symbol...")
        result3 = fmp_tool._run(data_type="income-statement", period="annual", years=3)
        print(f"✅ Missing symbol handled: {result3[:100]}...")
        
        # Test 4: Alternative parameter names
        print("\n4. Testing alternative parameter names...")
        result4 = fmp_tool._run(stock_symbol="AAPL", datatype="dcf", timeframe="annual", limit=2)
        print(f"✅ Alternative params work: {len(result4)} characters returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_basic():
    """Test basic crew functionality"""
    print("\n\nTesting Crew Basic Functionality")
    print("=" * 40)
    
    try:
        from crew.dcf_crew import create_dcf_crew
        
        crew = create_dcf_crew()
        print("✅ Crew created successfully")
        
        # Test basic query parsing
        query = "Analyze Apple for DCF analysis"
        info = crew._extract_basic_info(query)
        print(f"✅ Query parsed: {info.get('company_name')} -> {info.get('stock_symbol')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_parsing():
    """Test JSON format parsing"""
    print("\n\nTesting JSON Format Parsing")
    print("=" * 40)
    
    sample_json = {
        "executive_summary": "Apple shows strong financial performance with stable cash flows.",
        "company_overview": "Apple Inc. is a technology company.",
        "financial_metrics": {
            "revenue": [{"year": 2024, "value": 391.04, "currency": "USD_billions"}],
            "ebit": [{"year": 2024, "value": 123.22, "currency": "USD_billions"}]
        },
        "valuation": {
            "intrinsic_value": 150.00,
            "current_price": 145.50,
            "recommendation": "UNDERVALUED",
            "upside_potential": 3.1
        },
        "key_insights": ["Strong revenue growth", "Improving margins", "Solid cash generation"]
    }
    
    try:
        json_str = json.dumps(sample_json, indent=2)
        print("✅ Sample JSON created")
        
        # Test parsing
        parsed = json.loads(json_str)
        print("✅ JSON parsing works")
        
        # Test extraction
        if 'valuation' in parsed:
            val = parsed['valuation']
            print(f"✅ Valuation extracted: ${val['intrinsic_value']} vs ${val['current_price']}")
        
        if 'financial_metrics' in parsed:
            metrics = parsed['financial_metrics']
            print(f"✅ Metrics extracted: {len(metrics)} metrics found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("JSON Format and Parameter Handling Test")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ No FMP_API_KEY found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Run tests
    test1 = test_fmp_tool_params()
    test2 = test_crew_basic()
    test3 = test_json_parsing()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"FMP Tool Parameters: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Crew Basic Function: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"JSON Format Parsing: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if test1 and test2 and test3:
        print("\n🎉 All tests passed! System ready for JSON format.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
