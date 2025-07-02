#!/usr/bin/env python3
"""
Test FMP Tool with LLM-style parameters
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_llm_style_calls():
    """Test the FMP tool with the parameters that LLM is trying to use"""
    
    print("Testing FMP Tool with LLM-style parameters")
    print("=" * 50)
    
    try:
        from crew.tools.fmp import FMPTool
        
        fmp_tool = FMPTool()
        print("✅ FMP Tool initialized successfully")
        
        # Test the parameters that LLM is trying to use
        test_params = {
            "symbol": "AAPL",
            "data_type": "income-statement", 
            "period": "annual",
            "years": 3,
            "save_to_file": True
        }
        
        print(f"\nTesting with parameters: {test_params}")
        
        # Call _run method directly with these parameters
        result = fmp_tool._run(**test_params)
        
        print("✅ Tool call successful!")
        print(f"Result preview: {result[:200]}...")
        
        # Test other data types
        test_cases = [
            {"symbol": "AAPL", "data_type": "cash-flow-statement", "period": "annual", "years": 2},
            {"symbol": "AAPL", "data_type": "dcf", "period": "annual", "years": 3},
            {"symbol": "AAPL", "data_type": "valuation", "period": "annual", "years": 3}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['data_type']}")
            result = fmp_tool._run(**test_case)
            if "Failed" not in result:
                print(f"✅ {test_case['data_type']} test passed")
            else:
                print(f"❌ {test_case['data_type']} test failed: {result}")
        
        print("\n🎉 All LLM-style parameter tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_style_calls()
