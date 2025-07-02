# DCF Analysis Crew

An intelligent financial analysis system that extracts company information from natural language queries and performs comprehensive DCF (Discounted Cash Flow) analysis using the Financial Modeling Prep API.

## Features

- **Natural Language Processing**: Extract company names and analysis requirements from user queries
- **Comprehensive DCF Analysis**: Calculate EBIT, tax rates, depreciation, CapEx, and working capital changes
- **Multi-Agent System**: Specialized agents for research, analysis, calculation, and reporting
- **Data Export**: Save results to CSV and Excel formats
- **Interactive Interface**: Easy-to-use command-line interface

## Setup

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or using uv (recommended)
uv add pandas openpyxl requests python-dotenv
```

### 2. Environment Configuration

Create a `.env` file in the project root with your API keys:

```env
# Required: Financial Modeling Prep API Key
FMP_API_KEY=your_fmp_api_key_here

# Optional: Serper API Key for enhanced company research
SERPER_API_KEY=your_serper_api_key_here
```

**Getting API Keys:**
- **FMP API Key**: Sign up at [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs) for free
- **Serper API Key**: Sign up at [Serper](https://serper.dev/) for enhanced web search (optional)

## Usage

### Interactive Mode

Run the interactive interface:

```bash
python dcf_interface.py
```

### Command Line Mode

Analyze a company directly:

```bash
python dcf_interface.py "Analyze Apple for DCF analysis"
```

### Python API

Use the system in your Python code:

```python
from crew.dcf_crew import create_dcf_crew

# Create crew instance
crew = create_dcf_crew()

# Run analysis
result = crew.analyze_company("Analyze Microsoft with 5 years of data")
print(result)
```

## Example Queries

The system understands various natural language queries:

### Basic Analysis
- `"Analyze Apple for DCF analysis"`
- `"DCF analysis for Microsoft"`
- `"Calculate DCF metrics for Tesla"`

### With Parameters
- `"Analyze Amazon with 5 years of annual data"`
- `"DCF analysis for Google with quarterly data"`
- `"Calculate UFCF for Netflix with 3 years of data"`

### Using Stock Symbols
- `"Analyze AAPL stock"`
- `"DCF analysis for MSFT"`
- `"Calculate metrics for TSLA"`

### Advanced Analysis
- `"Comprehensive financial analysis of Meta"`
- `"Calculate unlevered free cash flow for Disney"`
- `"Analyze Nvidia's financial performance for DCF modeling"`

## System Architecture

### Agents

1. **Company Researcher**: Extracts company information from queries
2. **Financial Analyst**: Fetches financial data from APIs
3. **DCF Calculator**: Performs DCF calculations and analysis
4. **Report Generator**: Creates comprehensive analysis reports

### Tasks

1. **Extract Company Info**: Parse queries and identify companies
2. **Fetch Financial Data**: Retrieve income statements and cash flow data
3. **Calculate DCF Metrics**: Compute all DCF components
4. **Generate Analysis Report**: Create final comprehensive report

## DCF Metrics Calculated

- **EBIT** (Earnings Before Interest and Taxes)
- **Effective Tax Rate** (Income Tax Expense / Income Before Tax)
- **Depreciation & Amortization**
- **Capital Expenditures (CapEx)**
- **Working Capital Changes**
- **Unlevered Free Cash Flow (UFCF)**

Formula: `UFCF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - ΔWorking Capital`

## Output Files

The system automatically saves data to:

- **CSV files**: For easy data analysis and manipulation
- **Excel files**: With multiple sheets and summary information
- **Markdown reports**: Detailed analysis reports

Files are saved in the `financial_data/` directory with timestamps.

## File Structure

```
dcf-analysis/crew/
├── src/crew/
│   ├── config/
│   │   ├── agents.yaml      # Agent configurations
│   │   └── tasks.yaml       # Task definitions
│   ├── tools/
│   │   └── fmp.py          # Financial Modeling Prep API tool
│   ├── dcf_crew.py         # Main crew orchestration
│   └── index.py            # Entry point
├── dcf_interface.py        # Interactive interface
├── example_usage.py        # Usage examples
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (create this)
└── financial_data/         # Output directory (created automatically)
```

## Testing

Test the FMP tool directly:

```bash
python example_usage.py test
```

Run example analysis:

```bash
python example_usage.py
```

## Supported Companies

The system includes mappings for major companies, including:
- Apple (AAPL)
- Microsoft (MSFT)
- Amazon (AMZN)
- Google/Alphabet (GOOGL)
- Tesla (TSLA)
- Meta/Facebook (META)
- Netflix (NFLX)
- Nvidia (NVDA)
- And many more...

For companies not in the mapping, provide the stock symbol directly.

## Error Handling

The system includes comprehensive error handling for:
- Invalid API keys
- Network connectivity issues
- Missing company data
- Invalid stock symbols
- API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the error messages for specific guidance
2. Verify your API keys are correctly set
3. Ensure all dependencies are installed
4. Check the `financial_data/` directory for output files

## Limitations

- Requires active internet connection for API calls
- FMP API has rate limits (check your plan)
- Historical data availability depends on FMP API
- Some companies might not be in the symbol mapping database
