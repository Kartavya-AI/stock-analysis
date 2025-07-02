#!/usr/bin/env python3
"""
DCF Analysis Crew

This module contains the DCF Analysis crew that processes user queries to extract
company information and perform comprehensive DCF analysis using Financial Modeling Prep API.
"""

import os
import re
from typing import Dict, List, Optional
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
# Import our custom FMP tool
from src.crew.tools.fmp import FMPTool
load_dotenv()

@CrewBase
class DCFCrew:
    """DCF Analysis Crew for financial analysis"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        # Initialize LLM - using Gemini if API key is available, otherwise default
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            self.llm = LLM(model="gemini/gemini-2.0-flash", api_key=gemini_key)
        else:
            # Use default LLM or OpenAI if available
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.llm = LLM(model="gpt-4o-mini", api_key=openai_key)
            else:
                # Default to a free model or let CrewAI handle it
                self.llm = None
        
        # Initialize tools
        self.fmp_tool = FMPTool()
        # For web search to get company info
        self.search_tool = SerperDevTool() if os.getenv('SERPER_API_KEY') else None
    
    def extract_stock_symbol(self, company_name: str) -> str:
        """
        Extract or derive stock symbol from company name
        This is a simple mapping - in production, you'd use a more comprehensive database
        """
        # Common company name to stock symbol mappings
        symbol_mapping = {
            'apple': 'AAPL',
            'apple inc': 'AAPL',
            'microsoft': 'MSFT',
            'microsoft corporation': 'MSFT',
            'amazon': 'AMZN',
            'amazon.com': 'AMZN',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'meta': 'META',
            'facebook': 'META',
            'tesla': 'TSLA',
            'tesla inc': 'TSLA',
            'nvidia': 'NVDA',
            'nvidia corporation': 'NVDA',
            'netflix': 'NFLX',
            'netflix inc': 'NFLX',
            'coca-cola': 'KO',
            'coca cola': 'KO',
            'johnson & johnson': 'JNJ',
            'johnson and johnson': 'JNJ',
            'walmart': 'WMT',
            'walmart inc': 'WMT',
            'disney': 'DIS',
            'walt disney': 'DIS',
            'mcdonalds': 'MCD',
            "mcdonald's": 'MCD',
            'visa': 'V',
            'visa inc': 'V',
            'mastercard': 'MA',
            'mastercard inc': 'MA',
            'intel': 'INTC',
            'intel corporation': 'INTC',
            'ibm': 'IBM',
            'international business machines': 'IBM',
            'oracle': 'ORCL',
            'oracle corporation': 'ORCL',
            'salesforce': 'CRM',
            'salesforce.com': 'CRM',
            'adobe': 'ADBE',
            'adobe inc': 'ADBE',
            'paypal': 'PYPL',
            'paypal holdings': 'PYPL',
            'uber': 'UBER',
            'uber technologies': 'UBER',
            'airbnb': 'ABNB',
            'airbnb inc': 'ABNB',
            'zoom': 'ZM',
            'zoom video': 'ZM',
            'slack': 'WORK',
            'slack technologies': 'WORK',
            'spotify': 'SPOT',
            'spotify technology': 'SPOT',
            'twitter': 'TWTR',
            'twitter inc': 'TWTR',
            'snap': 'SNAP',
            'snap inc': 'SNAP',
            'pinterest': 'PINS',
            'pinterest inc': 'PINS',
            'square': 'SQ',
            'block': 'SQ',
            'roku': 'ROKU',
            'roku inc': 'ROKU',
            'peloton': 'PTON',
            'peloton interactive': 'PTON',
            'beyond meat': 'BYND',
            'beyond meat inc': 'BYND',
            'zoom': 'ZM',
            'zoom video communications': 'ZM',
            'crowdstrike': 'CRWD',
            'crowdstrike holdings': 'CRWD',
            'snowflake': 'SNOW',
            'snowflake inc': 'SNOW',
            'palantir': 'PLTR',
            'palantir technologies': 'PLTR',
            'roblox': 'RBLX',
            'roblox corporation': 'RBLX',
            'coinbase': 'COIN',
            'coinbase global': 'COIN',
            'robinhood': 'HOOD',
            'robinhood markets': 'HOOD',
            'upstart': 'UPST',
            'upstart holdings': 'UPST',
            'affirm': 'AFRM',
            'affirm holdings': 'AFRM'
        }
        
        # Clean the company name
        clean_name = company_name.lower().strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)  # Replace multiple spaces with single space
        clean_name = re.sub(r'[^\w\s&.-]', '', clean_name)  # Remove special characters except &, ., -
        
        # Check exact match first
        if clean_name in symbol_mapping:
            return symbol_mapping[clean_name]
        
        # Check partial matches
        for name, symbol in symbol_mapping.items():
            if name in clean_name or clean_name in name:
                return symbol
        
        # If no match found, return the original name (user might have provided symbol)
        # Check if it looks like a stock symbol (2-5 uppercase letters)
        if re.match(r'^[A-Z]{2,5}$', company_name.strip()):
            return company_name.strip().upper()
        
        # Default fallback - return cleaned name in uppercase
        return clean_name.upper().replace(' ', '')[:5]
    
    @agent
    def company_researcher(self) -> Agent:
        """Create the company researcher agent"""
        tools = []
        if self.search_tool:
            tools.append(self.search_tool)
        
        agent_config = {
            'config': self.agents_config['company_researcher'],
            'tools': tools,
            'verbose': True,
            'allow_delegation': False
        }
        
        if self.llm:
            agent_config['llm'] = self.llm
            
        return Agent(**agent_config)
    
    @agent
    def financial_analyst(self) -> Agent:
        """Create the financial analyst agent"""
        agent_config = {
            'config': self.agents_config['financial_analyst'],
            'tools': [self.fmp_tool],
            'verbose': True,
            'allow_delegation': False
        }
        
        if self.llm:
            agent_config['llm'] = self.llm
            
        return Agent(**agent_config)
    
    @agent
    def dcf_calculator(self) -> Agent:
        """Create the DCF calculator agent"""
        agent_config = {
            'config': self.agents_config['dcf_calculator'],
            'tools': [self.fmp_tool],
            'verbose': True,
            'allow_delegation': False
        }
        
        if self.llm:
            agent_config['llm'] = self.llm
            
        return Agent(**agent_config)
    
    @agent
    def report_generator(self) -> Agent:
        """Create the report generator agent"""
        agent_config = {
            'config': self.agents_config['report_generator'],
            'verbose': True,
            'allow_delegation': False
        }
        
        if self.llm:
            agent_config['llm'] = self.llm
            
        return Agent(**agent_config)
    
    @task
    def extract_company_info(self) -> Task:
        """Create the company information extraction task"""
        return Task(
            config=self.tasks_config['extract_company_info'],
            agent=self.company_researcher(),
            output_file='company_info.md'
        )
    
    @task
    def fetch_financial_data(self) -> Task:
        """Create the financial data fetching task"""
        return Task(
            config=self.tasks_config['fetch_financial_data'],
            agent=self.financial_analyst(),
            output_file='financial_data.md'
        )
    
    @task
    def calculate_dcf_metrics(self) -> Task:
        """Create the DCF metrics calculation task"""
        return Task(
            config=self.tasks_config['calculate_dcf_metrics'],
            agent=self.dcf_calculator(),
            output_file='dcf_calculations.md'
        )
    
    @task
    def generate_analysis_report(self) -> Task:
        """Create the analysis report generation task"""
        return Task(
            config=self.tasks_config['generate_analysis_report'],
            agent=self.report_generator(),
            output_file='final_analysis_report.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the DCF analysis crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def analyze_company(self, query: str) -> str:
        """
        Main method to analyze a company based on user query
        
        Args:
            query: User query containing company information and analysis requirements
            
        Returns:
            Final analysis report
        """
        # Extract basic info from query to help guide the analysis
        extracted_info = self._extract_basic_info(query)
        
        # Prepare inputs for the crew
        inputs = {
            'query': query,
            'company_name': extracted_info.get('company_name', 'Unknown'),
            'stock_symbol': extracted_info.get('stock_symbol', 'Unknown'),
            'period': extracted_info.get('period', 'annual'),
            'years': extracted_info.get('years', 5)
        }
        
        # Run the crew
        result = self.crew().kickoff(inputs=inputs)
        
        return result
    
    def _extract_basic_info(self, query: str) -> Dict:
        """
        Extract basic information from query to help guide the analysis
        This is a helper method for the crew
        """
        query_lower = query.lower()
        
        # Try to extract company name using common patterns
        company_patterns = [
            r'analyze\s+([A-Za-z\s&.-]+?)(?:\s+stock|\s+company|\s+for|\s+dcf|$)',
            r'(?:company|stock|ticker)[\s:]+([A-Za-z\s&.-]+?)(?:\s+analysis|\s+dcf|\s+for|$)',
            r'dcf\s+(?:analysis\s+)?(?:for\s+)?([A-Za-z\s&.-]+?)(?:\s+company|\s+stock|$)',
            r'([A-Z]{2,5})\s+(?:stock|company|analysis|dcf)',
            r'(?:^|\s)([A-Za-z\s&.-]+?)\s+(?:dcf|analysis|financial|valuation)'
        ]
        
        company_name = None
        for pattern in company_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                break
        
        # Extract stock symbol if provided
        stock_symbol = None
        if company_name:
            stock_symbol = self.extract_stock_symbol(company_name)
        
        # Extract period preference
        period = 'annual'
        if 'quarter' in query_lower or 'quarterly' in query_lower:
            period = 'quarter'
        
        # Extract years
        years = 5
        year_match = re.search(r'(\d+)\s+years?', query_lower)
        if year_match:
            years = int(year_match.group(1))
        
        return {
            'company_name': company_name,
            'stock_symbol': stock_symbol,
            'period': period,
            'years': min(years, 10)  # Cap at 10 years
        }


# Create the DCF crew instance
def create_dcf_crew():
    """Factory function to create DCF crew instance"""
    return DCFCrew()


# Main execution function
def main():
    """Main function for testing the crew"""
    crew = create_dcf_crew()
    
    # Example usage
    sample_query = "Analyze Apple Inc for DCF analysis with 5 years of annual data"
    result = crew.analyze_company(sample_query)
    print(result)


if __name__ == "__main__":
    main()
