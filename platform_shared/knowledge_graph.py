from __future__ import annotations

from typing import List

from neo4j import GraphDatabase

from .config import KG_MODE, KG_PASSWORD, KG_URI, KG_USER
from .schemas import ApiEndpoint


MOCK_APIS = [
    ApiEndpoint(method="POST", path="/vendors", object="Vendor"),
    ApiEndpoint(method="POST", path="/invoices", object="Invoice"),
    ApiEndpoint(method="GET", path="/invoices", object="Invoice"),
    ApiEndpoint(method="POST", path="/expenses", object="Expense"),
    ApiEndpoint(method="GET", path="/expenses", object="Expense"),
]


class KnowledgeGraphClient:
    def __init__(self) -> None:
        self._driver = None
        if KG_MODE == "neo4j":
            self._driver = GraphDatabase.driver(KG_URI, auth=(KG_USER, KG_PASSWORD))

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()

    def discover_apis(self, objects: List[str]) -> List[ApiEndpoint]:
        if KG_MODE != "neo4j" or self._driver is None:
            return [api for api in MOCK_APIS if api.object in objects]

        query = (
            "MATCH (o:BusinessObject)<-[:CREATES]-(a:APIEndpoint) "
            "WHERE o.name IN $objects "
            "RETURN a.method as method, a.path as path, o.name as object"
        )
        with self._driver.session() as session:
            results = session.run(query, objects=objects)
            return [ApiEndpoint(method=r["method"], path=r["path"], object=r["object"]) for r in results]
