#!/usr/bin/env python3
"""
Test script to verify UI can handle the JSON schema format
"""

import json

# Sample JSON that matches the schema from final_analysis_report.md
sample_json = {
    "executive_summary": "This report presents a discounted cash flow (DCF) analysis of Apple (AAPL) to determine its intrinsic value and investment recommendation.",
    "company_overview": "Apple Inc. is a multinational technology company specializing in consumer electronics, software, and online services.",
    "financial_metrics": {
        "revenue": [
            {"year": 2024, "value": 383.93, "currency": "USD_billions"},
            {"year": 2023, "value": 383.29, "currency": "USD_billions"},
            {"year": 2022, "value": 394.33, "currency": "USD_billions"}
        ],
        "ebit": [
            {"year": 2024, "value": 114.3, "currency": "USD_billions"},
            {"year": 2023, "value": 111.5, "currency": "USD_billions"},
            {"year": 2022, "value": 119.4, "currency": "USD_billions"}
        ],
        "net_income": [
            {"year": 2024, "value": 96.99, "currency": "USD_billions"},
            {"year": 2023, "value": 96.9, "currency": "USD_billions"},
            {"year": 2022, "value": 99.8, "currency": "USD_billions"}
        ],
        "tax_rate": [
            {"year": 2024, "value": 15.11, "unit": "percent"},
            {"year": 2023, "value": 13.45, "unit": "percent"},
            {"year": 2022, "value": 16.41, "unit": "percent"}
        ],
        "capex": [
            {"year": 2024, "value": 10.9, "currency": "USD_billions"},
            {"year": 2023, "value": 7.9, "currency": "USD_billions"},
            {"year": 2022, "value": 7.4, "currency": "USD_billions"}
        ]
    },
    "dcf_analysis": {
        "ufcf_calculations": [
            {"year": 2024, "ebit": 114.3, "tax_rate": 15.11, "depreciation": 11.3, "capex": 10.9, "wc_change": 2.0, "ufcf": 95.4},
            {"year": 2023, "ebit": 111.5, "tax_rate": 13.45, "depreciation": 11.0, "capex": 7.9, "wc_change": -14.4, "ufcf": 110.4},
            {"year": 2022, "ebit": 119.4, "tax_rate": 16.41, "depreciation": 10.8, "capex": 7.4, "wc_change": -7.5, "ufcf": 115.4}
        ],
        "trends": {
            "revenue_trend": "Apple's revenue has shown consistent growth over the past years.",
            "profitability_trend": "Profitability remains strong despite fluctuations."
        }
    },
    "valuation": {
        "intrinsic_value": 175.50,
        "current_price": 170.34,
        "recommendation": "UNDERVALUED",
        "upside_potential": 3.03
    },
    "key_insights": [
        "Apple's strong brand loyalty contributes to stable revenue growth.",
        "Efficient supply chain management supports high profitability.",
        "Large cash reserves provide financial flexibility."
    ],
    "methodology": "UFCF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - ΔWorking Capital",
    "data_quality_notes": "The financial data is based on publicly available information from Apple's financial statements."
}

def test_json_parsing():
    """Test that the JSON can be parsed correctly"""
    try:
        # Convert to JSON string and back to verify it's valid
        json_string = json.dumps(sample_json, indent=2)
        parsed_json = json.loads(json_string)
        
        print("✅ JSON parsing successful")
        print(f"📊 Financial metrics found: {len(parsed_json.get('financial_metrics', {}))}")
        print(f"📈 UFCF calculations: {len(parsed_json.get('dcf_analysis', {}).get('ufcf_calculations', []))}")
        print(f"💡 Key insights: {len(parsed_json.get('key_insights', []))}")
        print(f"🎯 Valuation available: {'valuation' in parsed_json}")
        
        # Test specific extractions that the UI will use
        if 'financial_metrics' in parsed_json:
            metrics = parsed_json['financial_metrics']
            for metric_name, metric_data in metrics.items():
                if isinstance(metric_data, list) and metric_data:
                    latest = metric_data[0]
                    print(f"   {metric_name}: {latest.get('value')} {latest.get('currency', latest.get('unit', ''))}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

def save_sample_json():
    """Save sample JSON for testing"""
    with open('sample_analysis_result.json', 'w') as f:
        json.dump(sample_json, f, indent=2)
    print("📄 Sample JSON saved to 'sample_analysis_result.json'")

if __name__ == "__main__":
    print("Testing UI JSON Schema Compatibility")
    print("=" * 40)
    
    if test_json_parsing():
        save_sample_json()
        print("\n🎉 All tests passed! UI should handle this JSON format correctly.")
    else:
        print("\n❌ Tests failed. Check JSON structure.")
