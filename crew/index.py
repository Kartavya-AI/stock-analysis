from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from src.crew.dcf_crew import DCFCrew

# Initialize FastAPI app
app = FastAPI(
    title="DCF Analysis Crew API",
    description="API for performing DCF (Discounted Cash Flow) analysis on companies",
    version="1.0.0"
)

# Initialize CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for structured input
class DCFAnalysisRequest(BaseModel):
    company: str
    years: Optional[int] = 5
    data_type: Optional[str] = "annual"  # "annual" or "quarterly"
    analysis_type: Optional[str] = "comprehensive"  # "basic", "comprehensive", "detailed"

class CompanyQuery(BaseModel):
    query: str

# Sample queries for reference
SAMPLE_QUERIES = [
    "Analyze Apple Inc for DCF analysis with 5 years of annual data",
    "Calculate DCF metrics for Microsoft Corporation",
    "Perform comprehensive financial analysis on TSLA stock",
    "DCF analysis for Amazon with quarterly data for 3 years",
    "Evaluate Netflix financial performance and intrinsic value",
    "Analyze Google (Alphabet) cash flow projections"
]

@app.get("/")
async def root():
    return {
        "message": "Welcome to the DCF Analysis Crew API!",
        "description": "This API provides comprehensive DCF analysis for publicly traded companies",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Perform DCF analysis with structured input",
            "POST /query": "Perform DCF analysis with natural language query",
            "GET /samples": "Get sample analysis queries",
            "GET /health": "Health check endpoint"
        }
    }

@app.post("/analyze")
async def analyze_company(request: DCFAnalysisRequest):
    """
    Perform DCF analysis on a specific company with structured parameters
    """
    try:
        # Create DCF crew instance
        dcf_crew = DCFCrew()
        
        # Format the analysis query
        formatted_query = f"Analyze {request.company} for DCF analysis with {request.years} years of {request.data_type} data. "
        formatted_query += f"Perform {request.analysis_type} analysis including intrinsic value calculation."
        
        # Run the DCF analysis
        result = dcf_crew.analyze_company(formatted_query)
        
        return {
            "status": "success",
            "company": request.company,
            "analysis_parameters": {
                "years": request.years,
                "data_type": request.data_type,
                "analysis_type": request.analysis_type
            },
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DCF analysis failed: {str(e)}")

@app.post("/query")
async def analyze_with_query(request: CompanyQuery):
    """
    Perform DCF analysis using natural language query
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Create DCF crew instance
        dcf_crew = DCFCrew()
        
        # Run the DCF analysis with the provided query
        result = dcf_crew.analyze_company(request.query)
        
        return {
            "status": "success",
            "query": request.query,
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DCF analysis failed: {str(e)}")

@app.get("/samples")
async def get_sample_queries():
    """
    Get sample DCF analysis queries for reference
    """
    return {
        "status": "success",
        "description": "Sample queries you can use for DCF analysis",
        "sample_queries": SAMPLE_QUERIES,
        "usage_tips": [
            "Include company name (ticker symbol or full name)",
            "Specify time period (e.g., '5 years', '3 years')",
            "Mention data type preference (annual/quarterly)",
            "Request specific analysis depth (basic/comprehensive/detailed)"
        ]
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status
    """
    try:
        # Test DCF crew initialization
        dcf_crew = DCFCrew()
        return {
            "status": "healthy",
            "message": "DCF Analysis Crew API is running successfully",
            "dcf_crew_status": "initialized"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"DCF crew initialization failed: {str(e)}",
            "dcf_crew_status": "failed"
        }

@app.post("/batch_analyze")
async def batch_analyze_companies(companies: List[str]):
    """
    Perform DCF analysis on multiple companies
    """
    try:
        if not companies:
            raise HTTPException(status_code=400, detail="Company list cannot be empty")
        
        if len(companies) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 companies allowed per batch")
        
        # Create DCF crew instance
        dcf_crew = DCFCrew()
        
        results = []
        for company in companies:
            try:
                query = f"Perform comprehensive DCF analysis for {company} with 5 years of annual data"
                result = dcf_crew.analyze_company(query)
                results.append({
                    "company": company,
                    "status": "success",
                    "result": result
                })
            except Exception as company_error:
                results.append({
                    "company": company,
                    "status": "failed",
                    "error": str(company_error)
                })
        
        return {
            "status": "completed",
            "total_companies": len(companies),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)