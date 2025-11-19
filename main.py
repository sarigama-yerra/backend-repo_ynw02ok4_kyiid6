import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="CRM Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FinanceSummary(BaseModel):
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    total_salaries: float = 0.0
    profit: float = 0.0


@app.get("/")
def root():
    return {"status": "ok", "service": "crm-backend"}


@app.get("/api/summary", response_model=FinanceSummary)
def get_summary():
    """Aggregate totals for revenue, expenses, salary, and profit"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    pipeline = [
        {"$group": {"_id": "$type", "total": {"$sum": "$amount"}}}
    ]
    try:
        coll = db["financerecord"]
        results = list(coll.aggregate(pipeline))
        totals = {r["_id"]: r["total"] for r in results}
        revenue = float(totals.get("revenue", 0))
        expenses = float(totals.get("expense", 0))
        salaries = float(totals.get("salary", 0))
        profit = revenue - (expenses + salaries)
        return FinanceSummary(
            total_revenue=revenue,
            total_expenses=expenses,
            total_salaries=salaries,
            profit=profit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NewFinanceRecord(BaseModel):
    type: str = Field(..., pattern="^(revenue|expense|salary)$")
    amount: float = Field(..., gt=0)
    date: Optional[datetime] = None
    category: Optional[str] = None
    description: Optional[str] = None
    employee_id: Optional[str] = None


@app.post("/api/records")
def add_record(payload: NewFinanceRecord):
    """Create a new finance record in DB"""
    data = payload.model_dump()
    if data.get("date") is None:
        data["date"] = datetime.utcnow()
    try:
        inserted_id = create_document("financerecord", data)
        return {"inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/records")
def list_records(record_type: Optional[str] = None, limit: int = 100):
    """List finance records optionally filtered by type"""
    if record_type and record_type not in ("revenue", "expense", "salary"):
        raise HTTPException(status_code=400, detail="Invalid type")
    filt = {"type": record_type} if record_type else {}
    try:
        docs = get_documents("financerecord", filt, limit)
        # Convert ObjectId to string for JSON
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
            if isinstance(d.get("date"), datetime):
                d["date"] = d["date"].isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
