#!/usr/bin/env python3
"""
DCF Analysis Crew - Main Entry Point

This module provides the main entry point for the DCF analysis crew system.
"""

from dcf_crew import DCFCrew


def main():
    """
    Main entry point for the DCF analysis system
    """
    # Create DCF crew instance
    crew = DCFCrew()
    
    # Example usage
    sample_queries = [
        "Analyze Apple Inc for DCF analysis with 5 years of annual data",
        "Calculate DCF metrics for Microsoft Corporation",
        "Perform comprehensive financial analysis on TSLA stock",
        "DCF analysis for Amazon with quarterly data for 3 years"
    ]
    
    print("DCF Analysis Crew - Available for company analysis")
    print("=" * 60)
    
    print("\nExample queries you can use:")
    for i, query in enumerate(sample_queries, 1):
        print(f"{i}. {query}")
    
    print("\nTo use the system:")
    print("1. Import the DCFCrew class")
    print("2. Create an instance: crew = DCFCrew()")
    print("3. Run analysis: result = crew.analyze_company('your query here')")
    
    print("\nOr use the interactive interface:")
    print("python dcf_interface.py")
    
    return crew


if __name__ == "__main__":
    main()
