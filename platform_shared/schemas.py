from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class A2AMessage(BaseModel):
    contextId: str
    taskType: str
    payload: Dict[str, Any]
    timestamp: str


class ScenarioPayload(BaseModel):
    scenario: str


class IntentPayload(BaseModel):
    product: str
    domain: str
    objects: List[str]
    goal: str
    quantity: int


class PlanStep(BaseModel):
    stepId: str
    action: str
    object: str
    dependsOn: List[str] = []


class WorkflowPlan(BaseModel):
    steps: List[PlanStep]


class ApiEndpoint(BaseModel):
    method: str
    path: str
    object: str


class DiscoveredApis(BaseModel):
    apis: List[ApiEndpoint]


class GeneratedData(BaseModel):
    vendor: Dict[str, Any]
    invoices: List[Dict[str, Any]]


class ExecutionResult(BaseModel):
    vendorId: Optional[str] = None
    invoiceIds: List[str]


class VerificationResult(BaseModel):
    overdueInvoiceIds: List[str]
    verified: bool
