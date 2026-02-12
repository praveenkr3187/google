from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Vendor(BaseModel):
    name: str
    address: str
    city: str
    state: str
    postalCode: str
    country: str


class Invoice(BaseModel):
    vendorId: str
    invoiceNumber: str
    invoiceDate: str
    dueDate: str
    paymentTerms: str
    paymentStatus: str
    lineItems: List[Dict]
    currency: str


class Expense(BaseModel):
    employeeId: str
    amount: float
    date: str
    description: str
    currency: str


vendors: Dict[str, Dict] = {}
invoices: Dict[str, Dict] = {}
expenses: Dict[str, Dict] = {}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/vendors")
async def create_vendor(vendor: Vendor) -> Dict[str, str]:
    vendor_id = str(uuid.uuid4())
    vendors[vendor_id] = {"id": vendor_id, **vendor.model_dump()}
    return {"id": vendor_id}


@app.post("/invoices")
async def create_invoice(invoice: Invoice) -> Dict[str, str]:
    invoice_id = str(uuid.uuid4())
    data = invoice.model_dump()
    data["id"] = invoice_id
    invoices[invoice_id] = data
    return {"id": invoice_id}


@app.get("/invoices")
async def list_invoices() -> List[Dict]:
    return list(invoices.values())


@app.post("/expenses")
async def create_expense(expense: Expense) -> Dict[str, str]:
    expense_id = str(uuid.uuid4())
    expenses[expense_id] = {"id": expense_id, **expense.model_dump()}
    return {"id": expense_id}


@app.get("/expenses")
async def list_expenses() -> List[Dict]:
    return list(expenses.values())


@app.get("/invoices/overdue")
async def list_overdue_invoices() -> List[Dict]:
    today = date.today()
    result = []
    for invoice in invoices.values():
        due_date = date.fromisoformat(invoice.get("dueDate"))
        if due_date < today and invoice.get("paymentStatus") != "Paid":
            result.append(invoice)
    return result
