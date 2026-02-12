from neo4j import GraphDatabase

from platform_shared.config import KG_PASSWORD, KG_URI, KG_USER


def main() -> None:
    driver = GraphDatabase.driver(KG_URI, auth=(KG_USER, KG_PASSWORD))

    statements = [
        "MERGE (p:SAPProduct {name: 'SAP Concur Invoice'})",
        "MERGE (p2:SAPProduct {name: 'SAP Concur Expense'})",
        "MERGE (v:BusinessObject {name: 'Vendor'})",
        "MERGE (i:BusinessObject {name: 'Invoice'})",
        "MERGE (e:BusinessObject {name: 'Expense'})",
        "MERGE (p)-[:HAS_OBJECT]->(v)",
        "MERGE (p)-[:HAS_OBJECT]->(i)",
        "MERGE (p2)-[:HAS_OBJECT]->(e)",
        "MERGE (i)-[:DEPENDS_ON]->(v)",
        "MERGE (a1:APIEndpoint {method:'POST', path:'/vendors'})",
        "MERGE (a2:APIEndpoint {method:'POST', path:'/invoices'})",
        "MERGE (a3:APIEndpoint {method:'GET', path:'/invoices'})",
        "MERGE (a4:APIEndpoint {method:'POST', path:'/expenses'})",
        "MERGE (a5:APIEndpoint {method:'GET', path:'/expenses'})",
        "MERGE (a1)-[:CREATES]->(v)",
        "MERGE (a2)-[:CREATES]->(i)",
        "MERGE (a4)-[:CREATES]->(e)",
    ]

    with driver.session() as session:
        for stmt in statements:
            session.run(stmt)

    driver.close()
    print("Seeded Enterprise Knowledge Graph")


if __name__ == "__main__":
    main()
