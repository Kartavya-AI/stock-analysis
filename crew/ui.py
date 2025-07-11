__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]
import streamlit as st
import sys
import os
import pandas as pd
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Add the src directory to the path (adjust path as needed)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    from crew.dcf_crew import create_dcf_crew
except ImportError:
    st.error("Could not import DCF crew module. Please ensure the src/crew/dcf_crew.py file exists.")
    st.stop()


class StreamlitDCFInterface:
    """Streamlit interface for DCF analysis with structured JSON handling"""
    
    def __init__(self):
        """Initialize the DCF analysis interface"""
        if 'dcf_crew' not in st.session_state:
            try:
                st.session_state.dcf_crew = create_dcf_crew()
            except Exception as e:
                st.error(f"Failed to initialize DCF crew: {str(e)}")
                st.stop()
    
    def analyze_company(self, query: str) -> str:
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
            result = st.session_state.dcf_crew.analyze_company(query.strip())
            return result
            
        except Exception as e:
            return f"Error during analysis: {str(e)}"


def parse_dcf_json(analysis_result) -> Optional[Dict[str, Any]]:
    """
    Parse DCF analysis result and return structured JSON data
    """
    try:
        # Handle CrewOutput object
        result_text = str(analysis_result)
        if hasattr(analysis_result, 'raw'):
            result_text = analysis_result.raw
        elif hasattr(analysis_result, 'result'):
            result_text = analysis_result.result
        
        # Extract JSON from text if it contains JSON block
        if '```json' in result_text:
            start_idx = result_text.find('```json') + 7
            end_idx = result_text.find('```', start_idx)
            if end_idx > start_idx:
                result_text = result_text[start_idx:end_idx].strip()
        
        # Try to parse JSON
        if result_text.strip().startswith('{'):
            return json.loads(result_text)
        
        return None
        
    except Exception as e:
        st.error(f"Error parsing DCF analysis result: {e}")
        return None


def display_executive_summary(summary: str):
    """Display executive summary in a structured format"""
    st.markdown("### 📋 Executive Summary")
    st.markdown(f"""
    <div style='background: #1a252f; padding: 20px; border-radius: 10px; border-left: 4px solid #4472C4; margin: 10px 0;'>
        <p style='margin: 0; font-size: 16px; line-height: 1.6; color: #ffffff;'>{summary}</p>
    </div>
    """, unsafe_allow_html=True)


def display_company_overview(overview: str):
    """Display company overview in a structured format"""
    st.markdown("### 🏢 Company Overview")
    st.markdown(f"""
    <div style='background: #1a252f; padding: 20px; border-radius: 10px; margin: 10px 0;'>
        <p style='margin: 0; font-size: 15px; line-height: 1.6; color: #ffffff;'>{overview}</p>
    </div>
    """, unsafe_allow_html=True)


def display_valuation_results(valuation_data: Dict):
    """Display valuation results with enhanced formatting"""
    st.markdown("### 🎯 Valuation Results")
    
    recommendation = valuation_data.get('recommendation', 'N/A')
    intrinsic_value = valuation_data.get('intrinsic_value', 'N/A')
    current_price = valuation_data.get('current_price', 'N/A')
    upside_potential = valuation_data.get('upside_potential', 'N/A')
    
    # Color coding for recommendation - using darker, more visible colors
    color_map = {
        "UNDERVALUED": "#1e7e34",  # Darker green
        "OVERVALUED": "#bd2130",   # Darker red
        "FAIRLY_VALUED": "#e0a800"  # Darker yellow/amber
    }
    bg_color = color_map.get(recommendation, "#1a252f")
    
    # Display recommendation banner
    st.markdown(f"""
    <div style='background: {bg_color}; 
                padding: 25px; border-radius: 15px; text-align: center; 
                margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin: 0; font-size: 2.5em;'>
            📈 {recommendation}
        </h1>
        <p style='color: white; margin: 10px 0 0 0; font-size: 1.2em;'>
            Investment Recommendation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Valuation metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Intrinsic Value",
            f"${intrinsic_value:.2f}" if isinstance(intrinsic_value, (int, float)) else str(intrinsic_value),
            help="Calculated fair value based on DCF analysis"
        )
    
    with col2:
        st.metric(
            "💰 Current Price",
            f"${current_price:.2f}" if isinstance(current_price, (int, float)) else str(current_price),
            help="Current market price per share"
        )
    
    with col3:
        delta_value = None
        if isinstance(upside_potential, (int, float)):
            delta_value = f"{upside_potential:.1f}%"
        st.metric(
            "📊 Upside/Downside",
            f"{upside_potential:.1f}%" if isinstance(upside_potential, (int, float)) else str(upside_potential),
            delta=delta_value,
            help="Potential return based on intrinsic value vs current price"
        )
    
    with col4:
        # Calculate absolute price difference
        if isinstance(intrinsic_value, (int, float)) and isinstance(current_price, (int, float)):
            price_diff = intrinsic_value - current_price
            st.metric(
                "💲 Price Difference",
                f"${price_diff:.2f}",
                delta=f"${price_diff:.2f}",
                help="Absolute difference between intrinsic and current price"
            )
        else:
            st.metric("💲 Price Difference", "N/A")


def display_financial_metrics(financial_metrics: Dict):
    """Display financial metrics in a structured table"""
    st.markdown("### 📊 Financial Metrics")
    
    # Create structured data for display
    metrics_data = []
    
    for metric_name, metric_values in financial_metrics.items():
        if isinstance(metric_values, list) and len(metric_values) > 0:
            # Get the most recent data point
            latest_data = metric_values[0]
            
            # Format metric name
            display_name = metric_name.replace('_', ' ').title()
            
            # Extract value and unit
            value = latest_data.get('value', 'N/A')
            currency = latest_data.get('currency', '')
            unit = latest_data.get('unit', '')
            year = latest_data.get('year', 'N/A')
            
            # Format value based on unit/currency
            if currency == 'USD_billions':
                formatted_value = f"${value:.2f}B"
            elif unit == 'percent':
                formatted_value = f"{value:.2f}%"
            else:
                formatted_value = f"{value:.2f}"
            
            metrics_data.append({
                'Metric': display_name,
                'Value': formatted_value,
                'Year': year
            })
    
    if metrics_data:
        df = pd.DataFrame(metrics_data)
        
        # Display as a styled table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Metric": st.column_config.TextColumn("Financial Metric", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="medium"),
                "Year": st.column_config.NumberColumn("Year", width="small")
            }
        )
    else:
        st.info("No financial metrics data available")


def display_dcf_analysis(dcf_data: Dict):
    """Display DCF analysis details in structured format"""
    st.markdown("### 🧮 DCF Analysis Details")
    
    # UFCF Calculations
    if 'ufcf_calculations' in dcf_data:
        st.markdown("#### 💰 Unlevered Free Cash Flow (UFCF)")
        
        ufcf_data = dcf_data['ufcf_calculations']
        if isinstance(ufcf_data, list) and len(ufcf_data) > 0:
            # Convert to DataFrame for better display
            df = pd.DataFrame(ufcf_data)
            
            # Format column names
            column_mapping = {
                'year': 'Year',
                'ebit': 'EBIT ($B)',
                'tax_rate': 'Tax Rate (%)',
                'depreciation': 'Depreciation ($B)',
                'capex': 'CapEx ($B)',
                'wc_change': 'WC Change ($B)',
                'ufcf': 'UFCF ($B)'
            }
            
            # Rename columns that exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No UFCF calculation data available")
    
    # Trends Analysis
    if 'trends' in dcf_data:
        st.markdown("#### 📈 Financial Trends Analysis")
        trends = dcf_data['trends']
        
        for trend_name, trend_description in trends.items():
            # Format trend name
            display_name = trend_name.replace('_', ' ').title()
            
            st.markdown(f"""
            <div style='background: #0d7377; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid #4472C4;'>
                <h4 style='margin: 0 0 10px 0; color: #ffffff;'>{display_name}</h4>
                <p style='margin: 0; font-size: 14px; line-height: 1.5; color: #ffffff;'>{trend_description}</p>
            </div>
            """, unsafe_allow_html=True)


def display_key_insights(insights: list):
    """Display key insights in a structured format"""
    st.markdown("### 💡 Key Insights")
    
    if insights:
        for i, insight in enumerate(insights, 1):
            st.markdown(f"""
            <div style='background: #5a2d82; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid #ffc107;'>
                <p style='margin: 0; font-size: 14px; line-height: 1.5; color: #ffffff;'><strong>Insight {i}:</strong> {insight}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No key insights available")


def display_methodology_and_notes(analysis_json: Dict):
    """Display methodology and data quality notes"""
    st.markdown("### 📚 Methodology & Notes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'methodology' in analysis_json:
            st.markdown("#### 🔬 Methodology")
            st.markdown(f"""
            <div style='background: #1e7e34; padding: 15px; border-radius: 8px; border-left: 3px solid #28a745;'>
                <p style='margin: 0; font-size: 14px; font-family: monospace; color: #ffffff;'>{analysis_json['methodology']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if 'data_quality_notes' in analysis_json:
            st.markdown("#### ⚠️ Data Quality Notes")
            st.markdown(f"""
            <div style='background: #b8860b; padding: 15px; border-radius: 8px; border-left: 3px solid #ffc107;'>
                <p style='margin: 0; font-size: 14px; color: #ffffff;'>{analysis_json['data_quality_notes']}</p>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main Streamlit application with structured DCF analysis display"""
    
    # Page configuration
    st.set_page_config(
        page_title="DCF Analysis Tool",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #4472C4, #5B9BD5);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stMetric {
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
    .stMetric > div {
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
    }
    .stMetric [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stMetric [data-testid="metric-container"] > div {
        color: #1a1a1a;
        font-weight: 600;
    }
    .stMetric [data-testid="metric-container"] label {
        color: #333333;
        font-weight: 700;
        font-size: 14px;
    }
    .stMetric [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1a1a1a;
        font-size: 24px;
        font-weight: 700;
    }
    .stMetric [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize the interface
    dcf_interface = StreamlitDCFInterface()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; text-align: center; margin: 0;">
            📊 DCF Analysis Tool
        </h1>
        <p style="color: white; text-align: center; margin: 5px 0 0 0; opacity: 0.9;">
            Comprehensive Discounted Cash Flow Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### 🎛️ Analysis Configuration")
        
        # Company input
        company_input = st.text_input(
            "🏢 Company Name or Symbol",
            placeholder="e.g., Apple, AAPL, Microsoft, MSFT",
            help="Enter the company name or stock symbol for analysis"
        )
        
        # Analysis type
        analysis_type = st.selectbox(
            "📋 Analysis Type",
            [
                "Comprehensive DCF Analysis",
                "Quick Valuation Check", 
                "Financial Metrics Review",
                "Custom Analysis Query"
            ],
            help="Select the type of analysis to perform"
        )
        
        # Time period selection
        time_period = st.selectbox(
            "📅 Data Period",
            ["5 years", "3 years", "10 years", "Custom"],
            help="Select the historical data period for analysis"
        )
        
        # Advanced DCF parameters
        with st.expander("⚙️ Advanced DCF Parameters"):
            discount_rate = st.slider(
                "Discount Rate (WACC) %", 
                min_value=5.0, max_value=15.0, value=9.0, step=0.1,
                help="Weighted Average Cost of Capital"
            )
            terminal_growth = st.slider(
                "Terminal Growth Rate %", 
                min_value=0.0, max_value=5.0, value=2.5, step=0.1,
                help="Long-term growth rate assumption"
            )
            projection_years = st.slider(
                "Projection Years", 
                min_value=5, max_value=15, value=10,
                help="Number of years for cash flow projections"
            )
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🔍 Analysis Query")
        
        if analysis_type == "Custom Analysis Query":
            query = st.text_area(
                "Enter your custom analysis query:",
                placeholder="e.g., 'Perform comprehensive DCF analysis for Apple with 5 years of historical data'",
                height=120,
                help="Describe exactly what kind of analysis you want"
            )
        else:
            # Auto-generate query based on selections
            if company_input:
                query_templates = {
                    "Comprehensive DCF Analysis": f"Perform comprehensive DCF analysis for {company_input} with {time_period} of historical data, including detailed financial metrics, UFCF calculations, and valuation with {discount_rate}% discount rate",
                    "Quick Valuation Check": f"Quick DCF valuation for {company_input} with {time_period} of data",
                    "Financial Metrics Review": f"Analyze financial metrics and trends for {company_input} over {time_period}",
                }
                query = query_templates.get(analysis_type, f"Analyze {company_input} for DCF analysis")
                
                st.text_area(
                    "Generated Query:", 
                    value=query, 
                    height=120, 
                    disabled=True,
                    help="This query was automatically generated based on your selections"
                )
            else:
                st.warning("⚠️ Please enter a company name or symbol to generate the analysis query")
                query = ""
    
    with col2:
        st.markdown("### 💡 Query Examples")
        st.markdown("""
        **Comprehensive:**
        - "DCF analysis for Tesla with 5 years data"
        - "Analyze Apple financial performance"
        
        **Quick Checks:**
        - "Valuation check for Microsoft"
        - "Is Amazon undervalued?"
        
        **Specific Metrics:**
        - "UFCF trends for Google"
        - "Cash flow analysis for Meta"
        """)
    
    # Analysis execution
    st.markdown("---")
    
    if st.button("🚀 Run DCF Analysis", type="primary", use_container_width=True):
        if query:
            with st.spinner("🔄 Performing DCF analysis... This may take a few minutes."):
                # Run the analysis
                result = dcf_interface.analyze_company(query)
                
                # Store results in session state
                st.session_state.analysis_result = result
                st.session_state.query_used = query
                st.session_state.analysis_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            st.error("❌ Please enter a query or select a company to analyze")
    
    # Display results if available
    if hasattr(st.session_state, 'analysis_result'):
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Parse JSON result
        analysis_json = parse_dcf_json(st.session_state.analysis_result)
        
        if analysis_json:
            # Display timestamp and query info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"**Query:** {st.session_state.query_used}")
            with col2:
                st.caption(f"**Completed:** {st.session_state.analysis_timestamp}")
            
            st.markdown("---")
            
            # 1. Executive Summary
            if 'executive_summary' in analysis_json:
                display_executive_summary(analysis_json['executive_summary'])
            
            # 2. Company Overview
            if 'company_overview' in analysis_json:
                display_company_overview(analysis_json['company_overview'])
            
            st.markdown("---")
            
            # 3. Valuation Results (Most Important)
            if 'valuation' in analysis_json:
                display_valuation_results(analysis_json['valuation'])
            
            st.markdown("---")
            
            # 4. Financial Metrics
            if 'financial_metrics' in analysis_json:
                display_financial_metrics(analysis_json['financial_metrics'])
            
            st.markdown("---")
            
            # 5. DCF Analysis Details
            if 'dcf_analysis' in analysis_json:
                display_dcf_analysis(analysis_json['dcf_analysis'])
            
            st.markdown("---")
            
            # 6. Key Insights
            if 'key_insights' in analysis_json:
                display_key_insights(analysis_json['key_insights'])
            
            st.markdown("---")
            
            # 7. Methodology and Notes
            display_methodology_and_notes(analysis_json)
            
        else:
            # Display raw text result if JSON parsing fails
            st.markdown("### 📄 Raw Analysis Output")
            st.text_area(
                "Analysis Result:", 
                value=str(st.session_state.analysis_result), 
                height=400,
                help="Raw output from the DCF analysis"
            )
            
            # Try to show any partial JSON
            result_str = str(st.session_state.analysis_result)
            if '```json' in result_str:
                st.markdown("### 🔍 Detected JSON Content")
                start_idx = result_str.find('```json')
                end_idx = result_str.find('```', start_idx + 7)
                if end_idx > start_idx:
                    json_content = result_str[start_idx:end_idx + 3]
                    st.code(json_content, language='json')


if __name__ == "__main__":
    main()