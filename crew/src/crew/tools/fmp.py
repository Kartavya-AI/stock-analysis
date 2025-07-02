import os
import re
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class FMPTool(BaseTool):
    name: str = "FMP Financial Data Tool"
    description: str = """
    Fetches financial data from Financial Modeling Prep API for DCF analysis.
    
    Parameters:
    - symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
    - data_type (str): Type of data to fetch:
        * 'dcf' - Complete DCF analysis data
        * 'income-statement' - Income statement data  
        * 'cash-flow-statement' - Cash flow statement data
        * 'ufcf' - Unlevered Free Cash Flow calculations
        * 'valuation' - Complete DCF valuation with intrinsic value
        * 'comprehensive' - All data types
    - period (str): 'annual' or 'quarter' (default: 'annual')
    - years (int): Number of years of data (default: 5)
    - save_to_file (bool): Save results to files (default: True)
    - save_format (str): 'csv', 'excel', or 'both' (default: 'both')
    
    Returns: Financial data and analysis results
    """
    
    # Declare fields properly for Pydantic
    api_key: str = Field(default="")
    base_url: str = Field(default="https://financialmodelingprep.com/api/v3")
    data_dir: str = Field(default="")
    
    def __init__(self, **kwargs):
        # Get API key from environment
        api_key = os.getenv('FMP_API_KEY', '')
        if not api_key:
            raise ValueError("FMP_API_KEY not found in environment variables")
        
        # Create data directory
        data_dir = os.path.join(os.getcwd(), "financial_data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize with proper field values
        super().__init__(
            api_key=api_key,
            base_url="https://financialmodelingprep.com/api/v3",
            data_dir=data_dir,
            **kwargs
        )
    
    def _make_request(self, endpoint: str) -> Optional[List[Dict]]:
        """Make a request to the FMP API"""
        url = f"{self.base_url}{endpoint}"
        params = {"apikey": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
    
    def get_income_statement(self, symbol: str, period: str = "annual", limit: int = 5) -> Optional[List[Dict]]:
        """
        Get income statement data for a company
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
        """
        endpoint = f"/income-statement/{symbol}"
        params = f"?period={period}&limit={limit}"
        return self._make_request(endpoint + params)
    
    def get_cash_flow_statement(self, symbol: str, period: str = "annual", limit: int = 5) -> Optional[List[Dict]]:
        """
        Get cash flow statement data for a company
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
        """
        endpoint = f"/cash-flow-statement/{symbol}"
        params = f"?period={period}&limit={limit}"
        return self._make_request(endpoint + params)
    
    def get_dcf_data(self, symbol: str, period: str = "annual", years: int = 5) -> Dict:
        """
        Get all necessary data for DCF analysis
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: 'annual' or 'quarter'
            years: Number of years of data to fetch
        
        Returns:
            Dictionary containing all DCF relevant data
        """
        # Get income statement and cash flow data
        income_data = self.get_income_statement(symbol, period, years)
        cashflow_data = self.get_cash_flow_statement(symbol, period, years)
        
        if not income_data or not cashflow_data:
            return {"error": "Failed to fetch financial data"}
        
        dcf_data = {
            "symbol": symbol,
            "period": period,
            "years_of_data": len(income_data),
            "data": []
        }
        
        # Process each year's data
        for i in range(min(len(income_data), len(cashflow_data))):
            income = income_data[i]
            cashflow = cashflow_data[i]
            
            # Calculate tax rate (Income Tax Expense / Income Before Tax)
            income_before_tax = income.get('incomeBeforeTax', 0)
            income_tax_expense = income.get('incomeTaxExpense', 0)
            tax_rate = (income_tax_expense / income_before_tax * 100) if income_before_tax != 0 else 0
            
            # Calculate working capital change
            # Working Capital = Current Assets - Current Liabilities
            # Change in Working Capital = Previous Year WC - Current Year WC
            working_capital_change = cashflow.get('changeInWorkingCapital', 0)
            
            year_data = {
                "date": income.get('date'),
                "calendarYear": income.get('calendarYear'),
                "period": income.get('period'),
                
                # DCF Components
                "ebit": income.get('operatingIncome', 0),  # EBIT = Operating Income
                "ebitda": income.get('ebitda', 0),
                "tax_rate_percent": round(tax_rate, 2),
                "tax_expense": income_tax_expense,
                "income_before_tax": income_before_tax,
                
                # Cash Flow Components
                "depreciation_amortization": cashflow.get('depreciationAndAmortization', 0),
                "capex": abs(cashflow.get('capitalExpenditure', 0)),  # Make positive for DCF
                "working_capital_change": working_capital_change,
                
                # Additional useful metrics
                "revenue": income.get('revenue', 0),
                "net_income": income.get('netIncome', 0),
                "free_cash_flow": cashflow.get('freeCashFlow', 0),
                "operating_cash_flow": cashflow.get('operatingCashFlow', 0),
            }
            
            dcf_data["data"].append(year_data)
        
        return dcf_data
    
    def calculate_unlevered_free_cash_flow(self, symbol: str, period: str = "annual", years: int = 5) -> Dict:
        """
        Calculate Unlevered Free Cash Flow (UFCF) for DCF analysis
        UFCF = EBIT * (1 - Tax Rate) + Depreciation - CapEx - Change in Working Capital
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarter'
            years: Number of years of data
        """
        dcf_data = self.get_dcf_data(symbol, period, years)
        
        if "error" in dcf_data:
            return dcf_data
        
        ufcf_data = {
            "symbol": symbol,
            "ufcf_calculations": []
        }
        
        for year_data in dcf_data["data"]:
            ebit = year_data["ebit"]
            tax_rate = year_data["tax_rate_percent"] / 100
            depreciation = year_data["depreciation_amortization"]
            capex = year_data["capex"]
            wc_change = year_data["working_capital_change"]
            
            # UFCF Calculation
            ebit_after_tax = ebit * (1 - tax_rate)
            ufcf = ebit_after_tax + depreciation - capex - wc_change
            
            ufcf_calc = {
                "date": year_data["date"],
                "year": year_data["calendarYear"],
                "ebit": ebit,
                "tax_rate": tax_rate,
                "ebit_after_tax": round(ebit_after_tax, 0),
                "depreciation_amortization": depreciation,
                "capex": capex,
                "working_capital_change": wc_change,
                "unlevered_free_cash_flow": round(ufcf, 0)
            }
            
            ufcf_data["ufcf_calculations"].append(ufcf_calc)
        
        return ufcf_data
    
    def _run(self, symbol: str = None, data_type: str = "dcf", period: str = "annual", 
             years: int = 5, save_to_file: bool = True, save_format: str = "both", 
             **kwargs) -> str:
        """
        Main execution method for the tool
        
        Args:
            symbol: Stock symbol
            data_type: Type of data to fetch ('dcf', 'income-statement', 'cash-flow-statement', 'ufcf', 'valuation', 'comprehensive')
            period: 'annual' or 'quarter'
            years: Number of years of data
            save_to_file: Whether to save data to files
            save_format: 'csv', 'excel', or 'both'
            **kwargs: Additional parameters for flexibility (handles various parameter names from LLM)
        """
        # Debug logging
        print(f"🔍 FMP Tool called with: symbol={symbol}, data_type={data_type}, kwargs={kwargs}")
        
        # Handle various parameter name variations from LLM/agent calls
        if symbol is None:
            symbol = kwargs.get('stock_symbol', kwargs.get('ticker', ''))
        
        # Handle data_type variations
        if 'datatype' in kwargs:
            data_type = kwargs['datatype']
        elif 'type' in kwargs:
            data_type = kwargs['type']
        
        # Handle period variations
        if 'timeframe' in kwargs:
            period = kwargs['timeframe']
        elif 'frequency' in kwargs:
            period = kwargs['frequency']
        
        # Handle years variations
        if 'limit' in kwargs:
            years = kwargs['limit']
        elif 'num_years' in kwargs:
            years = kwargs['num_years']
        
        # Handle save variations
        if 'sav' in kwargs or 'save' in kwargs:
            save_to_file = kwargs.get('sav', kwargs.get('save', save_to_file))
        
        print(f"🔍 After parameter processing: symbol={symbol}, data_type={data_type}")
        
        if not symbol:
            return "Error: No stock symbol provided. Please specify a symbol parameter."
        
        symbol = symbol.upper()
        
        # Validate stock symbol format
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            return f"Error: Invalid stock symbol format '{symbol}'. Stock symbols should be 1-5 uppercase letters."
        
        # Check for common invalid symbols that might be parsing errors
        invalid_symbols = ['NSIVE', 'NSVE', 'COMPR', 'COMP', 'ANALY', 'ANAL', 'REPOR', 'REPO', 'STUDI', 'STUD', 'HENSI', 'HENS']
        if symbol in invalid_symbols:
            return f"Error: '{symbol}' appears to be a parsing error, not a valid stock symbol. Please provide a valid company name or stock symbol."
        
        # Handle different data_type variations
        if data_type in ["income-statement", "income"]:
            result = self.get_income_statement(symbol, period, years)
        elif data_type in ["cash-flow-statement", "cashflow", "cash-flow"]:
            result = self.get_cash_flow_statement(symbol, period, years)
        elif data_type == "dcf":
            result = self.get_dcf_data(symbol, period, years)
        elif data_type == "ufcf":
            result = self.calculate_unlevered_free_cash_flow(symbol, period, years)
        elif data_type == "valuation":
            result = self.calculate_dcf_valuation(symbol, period, years)
        elif data_type == "comprehensive":
            # Create comprehensive report with all data types
            file_paths = self.create_comprehensive_report(symbol, period, years, save_format)
            return f"Comprehensive report created for {symbol}. Files saved: {file_paths}"
        else:
            return f"Invalid data_type '{data_type}'. Choose from: 'dcf', 'income-statement', 'cash-flow-statement', 'ufcf', 'valuation', 'comprehensive'"
        
        if result and "error" not in result:
            # Save to file if requested
            if save_to_file:
                file_paths = []
                filename = f"{symbol}_{data_type.replace('-', '_').upper()}_Data"
                
                if save_format in ["csv", "both"]:
                    csv_path = self.save_to_csv(result, filename)
                    file_paths.append(f"CSV: {csv_path}")
                
                if save_format in ["excel", "both"]:
                    excel_path = self.save_to_excel(result, filename)
                    file_paths.append(f"Excel: {excel_path}")
                
                file_info = " | ".join(file_paths) if file_paths else ""
                return f"Data fetched for {symbol} ({data_type}). Files saved: {file_info}\n\nData preview:\n{str(result)[:500]}..."
            
            return str(result)
        else:
            return f"Failed to fetch {data_type} data for {symbol}"
    
    def save_to_csv(self, data: Dict, filename: str) -> str:
        """
        Save financial data to CSV file
        
        Args:
            data: Financial data dictionary
            filename: Name of the CSV file (without extension)
        
        Returns:
            Full path to the saved CSV file
        """
        if "error" in data:
            return f"Error: {data['error']}"
        
        # Convert data to DataFrame based on data structure
        if "data" in data:  # DCF data structure
            df = pd.DataFrame(data["data"])
        elif "ufcf_calculations" in data:  # UFCF data structure
            df = pd.DataFrame(data["ufcf_calculations"])
        elif isinstance(data, list):  # Direct API response
            df = pd.DataFrame(data)
        else:
            return "Error: Unsupported data format for CSV export"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{filename}_{timestamp}.csv"
        csv_path = os.path.join(self.data_dir, csv_filename)
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        return csv_path
    
    def save_to_excel(self, data: Dict, filename: str, include_summary: bool = True) -> str:
        """
        Save financial data to Excel file with multiple sheets
        
        Args:
            data: Financial data dictionary
            filename: Name of the Excel file (without extension)
            include_summary: Whether to include a summary sheet
        
        Returns:
            Full path to the saved Excel file
        """
        if "error" in data:
            return f"Error: {data['error']}"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"{filename}_{timestamp}.xlsx"
        excel_path = os.path.join(self.data_dir, excel_filename)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            if "data" in data:  # DCF data structure
                df = pd.DataFrame(data["data"])
                df.to_excel(writer, sheet_name='Financial_Data', index=False)
                
                if include_summary:
                    # Create summary sheet
                    summary_data = {
                        'Symbol': [data.get('symbol', 'N/A')],
                        'Period': [data.get('period', 'N/A')],
                        'Years_of_Data': [data.get('years_of_data', 0)],
                        'Generated_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
            elif "ufcf_calculations" in data:  # UFCF data structure
                df = pd.DataFrame(data["ufcf_calculations"])
                df.to_excel(writer, sheet_name='UFCF_Calculations', index=False)
                
                if include_summary:
                    summary_data = {
                        'Symbol': [data.get('symbol', 'N/A')],
                        'Generated_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
            elif isinstance(data, list):  # Direct API response
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='Financial_Data', index=False)
        
        return excel_path
    
    def create_comprehensive_report(self, symbol: str, period: str = "annual", years: int = 5, 
                                  save_format: str = "both") -> Dict[str, str]:
        """
        Create a comprehensive financial report with all data types
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarter'
            years: Number of years of data
            save_format: 'csv', 'excel', or 'both'
        
        Returns:
            Dictionary with file paths of saved reports
        """
        symbol = symbol.upper()
        results = {}
        
        # Get all data types
        dcf_data = self.get_dcf_data(symbol, period, years)
        ufcf_data = self.calculate_unlevered_free_cash_flow(symbol, period, years)
        income_data = self.get_income_statement(symbol, period, years)
        cashflow_data = self.get_cash_flow_statement(symbol, period, years)
        
        # Save data based on format preference
        if save_format in ["csv", "both"]:
            if dcf_data and "error" not in dcf_data:
                results["dcf_csv"] = self.save_to_csv(dcf_data, f"{symbol}_DCF_Data")
            if ufcf_data and "error" not in ufcf_data:
                results["ufcf_csv"] = self.save_to_csv(ufcf_data, f"{symbol}_UFCF_Data")
            if income_data:
                results["income_csv"] = self.save_to_csv(income_data, f"{symbol}_Income_Statement")
            if cashflow_data:
                results["cashflow_csv"] = self.save_to_csv(cashflow_data, f"{symbol}_Cash_Flow")
        
        if save_format in ["excel", "both"]:
            if dcf_data and "error" not in dcf_data:
                results["dcf_excel"] = self.save_to_excel(dcf_data, f"{symbol}_DCF_Data")
            if ufcf_data and "error" not in ufcf_data:
                results["ufcf_excel"] = self.save_to_excel(ufcf_data, f"{symbol}_UFCF_Data")
            if income_data:
                results["income_excel"] = self.save_to_excel(income_data, f"{symbol}_Income_Statement")
            if cashflow_data:
                results["cashflow_excel"] = self.save_to_excel(cashflow_data, f"{symbol}_Cash_Flow")
        
        return results

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price for a company
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current stock price or None if error
        """
        endpoint = f"/quote-short/{symbol}"
        data = self._make_request(endpoint)
        
        if data and len(data) > 0:
            return data[0].get('price', None)
        return None
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        Get company profile including shares outstanding
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Company profile data
        """
        endpoint = f"/profile/{symbol}"
        data = self._make_request(endpoint)
        
        if data and len(data) > 0:
            return data[0]
        return None
    
    def calculate_dcf_valuation(self, symbol: str, period: str = "annual", years: int = 5,
                               terminal_growth_rate: float = 0.03, discount_rate: float = 0.10,
                               net_debt: Optional[float] = None) -> Dict:
        """
        Calculate complete DCF valuation including intrinsic value per share
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarter'
            years: Number of years of historical data
            terminal_growth_rate: Long-term growth rate (default 3%)
            discount_rate: WACC/discount rate (default 10%)
            net_debt: Net debt amount (if None, will estimate)
            
        Returns:
            Complete DCF valuation results
        """
        # Get UFCF data
        ufcf_data = self.calculate_unlevered_free_cash_flow(symbol, period, years)
        
        if "error" in ufcf_data:
            return ufcf_data
        
        # Get current stock price and company profile
        current_price = self.get_current_price(symbol)
        company_profile = self.get_company_profile(symbol)
        
        # Extract UFCF values
        ufcf_values = [calc["unlevered_free_cash_flow"] for calc in ufcf_data["ufcf_calculations"]]
        
        # Calculate present values
        present_values = []
        for i, ufcf in enumerate(ufcf_values, 1):
            pv_factor = 1 / ((1 + discount_rate) ** i)
            present_value = ufcf * pv_factor
            present_values.append({
                "year": i,
                "ufcf": ufcf,
                "pv_factor": round(pv_factor, 3),
                "present_value": round(present_value, 0)
            })
        
        # Calculate terminal value
        final_ufcf = ufcf_values[-1] if ufcf_values else 0
        terminal_fcf = final_ufcf * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
        terminal_pv_factor = 1 / ((1 + discount_rate) ** len(ufcf_values))
        terminal_present_value = terminal_value * terminal_pv_factor
        
        # Calculate enterprise value
        sum_pv_fcf = sum([pv["present_value"] for pv in present_values])
        enterprise_value = sum_pv_fcf + terminal_present_value
        
        # Estimate net debt if not provided
        if net_debt is None:
            # Simple estimation - in practice, get from balance sheet
            net_debt = enterprise_value * 0.05  # Assume 5% of enterprise value
        
        # Calculate equity value
        equity_value = enterprise_value - net_debt
        
        # Get shares outstanding
        shares_outstanding = None
        if company_profile:
            shares_outstanding = company_profile.get('mktCap', 0) / current_price if current_price else None
            if not shares_outstanding:
                shares_outstanding = company_profile.get('sharesOutstanding', 0)
        
        # Calculate intrinsic value per share
        intrinsic_value_per_share = None
        if shares_outstanding and shares_outstanding > 0:
            intrinsic_value_per_share = equity_value / shares_outstanding
        
        # Calculate valuation metrics
        price_variance = None
        price_variance_percent = None
        recommendation = "N/A"
        
        if current_price and intrinsic_value_per_share:
            price_variance = current_price - intrinsic_value_per_share
            price_variance_percent = (price_variance / intrinsic_value_per_share) * 100
            
            if price_variance_percent > 20:
                recommendation = "OVERVALUED"
            elif price_variance_percent < -20:
                recommendation = "UNDERVALUED"
            else:
                recommendation = "FAIRLY VALUED"
        
        return {
            "symbol": symbol,
            "valuation_date": datetime.now().strftime("%Y-%m-%d"),
            "assumptions": {
                "terminal_growth_rate": terminal_growth_rate,
                "discount_rate": discount_rate,
                "years_analyzed": len(ufcf_values)
            },
            "cash_flow_projections": present_values,
            "terminal_value": {
                "terminal_fcf": round(terminal_fcf, 0),
                "terminal_value": round(terminal_value, 0),
                "present_value": round(terminal_present_value, 0)
            },
            "valuation_summary": {
                "sum_pv_fcf": round(sum_pv_fcf, 0),
                "terminal_pv": round(terminal_present_value, 0),
                "enterprise_value": round(enterprise_value, 0),
                "net_debt": round(net_debt, 0),
                "equity_value": round(equity_value, 0),
                "shares_outstanding": shares_outstanding,
                "intrinsic_value_per_share": round(intrinsic_value_per_share, 2) if intrinsic_value_per_share else None
            },
            "market_comparison": {
                "current_price": current_price,
                "intrinsic_value": round(intrinsic_value_per_share, 2) if intrinsic_value_per_share else None,
                "price_variance": round(price_variance, 2) if price_variance else None,
                "price_variance_percent": round(price_variance_percent, 1) if price_variance_percent else None,
                "recommendation": recommendation
            },
            "company_profile": company_profile
        }
        
# Create an instance of the tool for easy import
fmp_tool = FMPTool()

# Convenience functions for direct use
def get_dcf_data(symbol: str, period: str = "annual", years: int = 5, save_to_file: bool = False):
    """Get DCF analysis data for a company"""
    data = fmp_tool.get_dcf_data(symbol, period, years)
    if save_to_file and data and "error" not in data:
        csv_path = fmp_tool.save_to_csv(data, f"{symbol}_DCF_Data")
        excel_path = fmp_tool.save_to_excel(data, f"{symbol}_DCF_Data")
        print(f"Data saved to: {csv_path} and {excel_path}")
    return data

def get_ufcf_data(symbol: str, period: str = "annual", years: int = 5, save_to_file: bool = False):
    """Get Unlevered Free Cash Flow calculations for a company"""
    data = fmp_tool.calculate_unlevered_free_cash_flow(symbol, period, years)
    if save_to_file and data and "error" not in data:
        csv_path = fmp_tool.save_to_csv(data, f"{symbol}_UFCF_Data")
        excel_path = fmp_tool.save_to_excel(data, f"{symbol}_UFCF_Data")
        print(f"Data saved to: {csv_path} and {excel_path}")
    return data

def get_dcf_valuation(symbol: str, period: str = "annual", years: int = 5, save_to_file: bool = False):
    """Get complete DCF valuation with market comparison"""
    data = fmp_tool.calculate_dcf_valuation(symbol, period, years)
    if save_to_file and data and "error" not in data:
        csv_path = fmp_tool.save_to_csv(data, f"{symbol}_DCF_Valuation")
        excel_path = fmp_tool.save_to_excel(data, f"{symbol}_DCF_Valuation")
        print(f"Valuation data saved to: {csv_path} and {excel_path}")
    return data

def save_data_to_csv(data: Dict, filename: str) -> str:
    """Save any financial data to CSV"""
    return fmp_tool.save_to_csv(data, filename)

def save_data_to_excel(data: Dict, filename: str) -> str:
    """Save any financial data to Excel"""
    return fmp_tool.save_to_excel(data, filename)

def create_comprehensive_report(symbol: str, period: str = "annual", years: int = 5, save_format: str = "both"):
    """Create comprehensive financial report with all data types"""
    return fmp_tool.create_comprehensive_report(symbol, period, years, save_format)