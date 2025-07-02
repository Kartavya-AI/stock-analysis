#!/usr/bin/env python3
"""
Test the FMP Tool to ensure it's working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_fmp_tool():
    """Test the FMP tool initialization and basic functionality"""
    
    print("Testing FMP Tool...")
    print("=" * 40)
    
    # Check if API key is available
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ Error: FMP_API_KEY not found in environment variables")
        print("Please create a .env file with your FMP API key:")
        print("FMP_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Import and test the FMP tool
        from crew.tools.fmp import FMPTool
        
        print("✅ FMPTool imported successfully")
        
        # Initialize the tool
        fmp_tool = FMPTool()
        print("✅ FMPTool initialized successfully")
        
        # Test basic functionality with Apple
        print("\nTesting data fetch for Apple (AAPL)...")
        
        # Test income statement
        income_data = fmp_tool.get_income_statement("AAPL", "annual", 2)
        if income_data:
            print(f"✅ Income statement data fetched: {len(income_data)} years")
        else:
            print("❌ Failed to fetch income statement data")
            return False
        
        # Test cash flow statement
        cashflow_data = fmp_tool.get_cash_flow_statement("AAPL", "annual", 2)
        if cashflow_data:
            print(f"✅ Cash flow data fetched: {len(cashflow_data)} years")
        else:
            print("❌ Failed to fetch cash flow data")
            return False
        
        # Test DCF data
        dcf_data = fmp_tool.get_dcf_data("AAPL", "annual", 2)
        if dcf_data and "error" not in dcf_data:
            print(f"✅ DCF data calculated successfully")
            print(f"   Symbol: {dcf_data.get('symbol')}")
            print(f"   Years of data: {dcf_data.get('years_of_data')}")
            
            # Test saving to files
            csv_path = fmp_tool.save_to_csv(dcf_data, "AAPL_Test")
            excel_path = fmp_tool.save_to_excel(dcf_data, "AAPL_Test")
            
            print(f"✅ Files saved successfully:")
            print(f"   CSV: {csv_path}")
            print(f"   Excel: {excel_path}")
            
        else:
            print("❌ Failed to calculate DCF data")
            print(f"Error: {dcf_data.get('error', 'Unknown error')}")
            return False
        
        print("\n🎉 All tests passed! FMP Tool is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crew_initialization():
    """Test crew initialization"""
    
    print("\nTesting DCF Crew initialization...")
    print("=" * 40)
    
    try:
        from crew.dcf_crew import create_dcf_crew
        
        crew = create_dcf_crew()
        print("✅ DCF Crew initialized successfully")
        
        # Test basic query parsing
        test_query = "Analyze Apple for DCF analysis"
        extracted_info = crew._extract_basic_info(test_query)
        
        print(f"✅ Query parsing test:")
        print(f"   Company: {extracted_info.get('company_name')}")
        print(f"   Symbol: {extracted_info.get('stock_symbol')}")
        print(f"   Period: {extracted_info.get('period')}")
        print(f"   Years: {extracted_info.get('years')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during crew testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("DCF Analysis System Test")
    print("=" * 50)
    
    # Test FMP tool first
    fmp_success = test_fmp_tool()
    
    # Test crew initialization
    crew_success = test_crew_initialization()
    
    print("\n" + "=" * 50)
    if fmp_success and crew_success:
        print("🎉 All systems working! You can now use the DCF analysis crew.")
        print("\nTo get started:")
        print("python dcf_interface.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
