#!/usr/bin/env python3
"""
DCF Analysis Interface

Simple interface for running DCF analysis on companies using natural language queries.
"""

import sys
import os
from typing import Optional

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crew.dcf_crew import create_dcf_crew


class DCFAnalysisInterface:
    """Simple interface for DCF analysis"""
    
    def __init__(self):
        """Initialize the DCF analysis interface"""
        self.crew = create_dcf_crew()
        print("DCF Analysis Interface initialized successfully!")
        print("You can now analyze companies using natural language queries.")
        print("\nExample queries:")
        print("- 'Analyze Apple for DCF analysis'")
        print("- 'Calculate DCF metrics for Microsoft with 5 years of data'")
        print("- 'Perform financial analysis on TSLA stock'")
        print("- 'DCF analysis for Amazon with quarterly data'")
        print("\n" + "="*50)
    
    def analyze(self, query: str) -> str:
        """
        Analyze a company based on user query
        
        Args:
            query: Natural language query about company analysis
            
        Returns:
            Analysis result
        """
        if not query or not query.strip():
            return "Please provide a valid query."
        
        try:
            print(f"Processing query: {query}")
            print("This may take a few minutes to fetch data and perform analysis...")
            print("-" * 50)
            
            result = self.crew.analyze_company(query.strip())
            return result
            
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    def interactive_mode(self):
        """Run the interface in interactive mode"""
        print("Interactive DCF Analysis Mode")
        print("Type 'quit', 'exit', or 'q' to exit")
        print("Type 'help' for examples")
        print("-" * 50)
        
        while True:
            try:
                query = input("\nEnter your analysis query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if query.lower() == 'help':
                    self._show_help()
                    continue
                
                if not query:
                    print("Please enter a valid query.")
                    continue
                
                result = self.analyze(query)
                print("\n" + "="*80)
                print("ANALYSIS RESULT:")
                print("="*80)
                print(result)
                print("="*80)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
HELP - DCF Analysis Query Examples:

Basic Analysis:
- "Analyze Apple for DCF"
- "DCF analysis for Microsoft"
- "Calculate DCF metrics for Tesla"

With Specific Parameters:
- "Analyze Amazon with 5 years of annual data"
- "DCF analysis for Google with quarterly data"
- "Calculate UFCF for Netflix with 3 years of data"

Using Stock Symbols:
- "Analyze AAPL stock"
- "DCF analysis for MSFT"
- "Calculate metrics for TSLA"

Advanced Queries:
- "Comprehensive financial analysis of Meta"
- "Calculate unlevered free cash flow for Disney"
- "Analyze Nvidia's financial performance for DCF modeling"

The system will:
1. Extract the company name/symbol from your query
2. Fetch financial data from Financial Modeling Prep API
3. Calculate DCF metrics (EBIT, tax rate, depreciation, CapEx, working capital changes)
4. Generate a comprehensive analysis report
5. Save data to CSV and Excel files

Files are saved in the 'financial_data' directory.
        """
        print(help_text)


def main():
    """Main function"""
    interface = DCFAnalysisInterface()
    
    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        result = interface.analyze(query)
        print(result)
    else:
        # Run in interactive mode
        interface.interactive_mode()


if __name__ == "__main__":
    main()
