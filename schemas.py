"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date

# Example schemas (kept for reference/examples):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# CRM Schemas
# --------------------------------------------------

class Employee(BaseModel):
    """
    Employees collection schema
    Collection name: "employee"
    """
    name: str = Field(..., description="Employee full name")
    role: Optional[str] = Field(None, description="Job role/title")
    monthly_salary: float = Field(..., ge=0, description="Monthly salary amount")
    start_date: Optional[date] = Field(None, description="Employment start date")
    is_active: bool = Field(True, description="Active employment status")

class FinanceRecord(BaseModel):
    """
    Finance records for revenue, expenses, and salaries
    Collection name: "financerecord"
    """
    type: Literal["revenue", "expense", "salary"] = Field(..., description="Record type")
    amount: float = Field(..., gt=0, description="Transaction amount (positive number)")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date/time of the record")
    category: Optional[str] = Field(None, description="Category (e.g., subscription, rent, sales)")
    description: Optional[str] = Field(None, description="Short description")
    employee_id: Optional[str] = Field(None, description="Related employee id (for salary records)")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
