import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from schemas import Lead as LeadSchema, ConnectionRequest as ConnectionSchema
from database import create_document

app = FastAPI(title="Cryptvest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Backend-first endpoints

@app.post("/leads")
def create_lead(lead: LeadSchema):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/connect")
def create_connection(req: ConnectionSchema):
    try:
        conn_id = create_document("connectionrequest", req)
        return {"status": "ok", "id": conn_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo-portfolio")
def demo_portfolio() -> Dict[str, Any]:
    # Static demo data to power the front-end visualization
    allocations = [
        {"asset": "BTC", "percent": 48, "value": 48250},
        {"asset": "ETH", "percent": 28, "value": 28110},
        {"asset": "SOL", "percent": 12, "value": 12040},
        {"asset": "USDC", "percent": 7, "value": 7010},
        {"asset": "Others", "percent": 5, "value": 5040},
    ]
    equity_curve = [
        {"t": "-6m", "v": 72000},
        {"t": "-5m", "v": 76000},
        {"t": "-4m", "v": 81000},
        {"t": "-3m", "v": 79000},
        {"t": "-2m", "v": 83000},
        {"t": "-1m", "v": 88500},
        {"t": "now", "v": 100450},
    ]
    stats = {
        "total_value": 100450,
        "one_day": 2.6,
        "one_week": 7.4,
        "one_month": 13.8,
        "best_asset": "SOL",
    }
    return {"allocations": allocations, "equity_curve": equity_curve, "stats": stats}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
