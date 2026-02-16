import json
import logging
from pathlib import Path
from typing import Any

from mhd_model.log_utils import set_basic_logging_config

logger = logging.getLogger(__name__)

try:
    from neo4j import Driver, GraphDatabase

    # Neo4j credentials
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "mhd.database"
    driver: Driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def create_nodes(tx, nodes):
        for node in nodes:
            labels = ":".join(f"`{label}`" for label in node["labels"])
            tx.run(
                f"MERGE (n:{labels} {{id: $id}}) SET n += $properties",
                id=node["id"],
                properties=node["properties"],
            )

    def create_relationships(tx, relationships):
        for rel in relationships:
            tx.run(
                f"""
                MATCH (a {{id: $start_id}})
                MATCH (b {{id: $end_id}})
                MERGE (a)-[r:{rel["type"]}]->(b)
                SET r += $properties
                """,
                start_id=rel["start"],
                end_id=rel["end"],
                properties=rel["properties"],
            )

    def upload_to_neo4j(
        driver: Driver,
        nodes: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
    ):
        with driver.session() as session:
            session.execute_write(create_nodes, nodes)
            session.execute_write(create_relationships, relationships)

    def update_neo4j(input_root_path: str):
        files = list(Path(input_root_path).glob("*.neo4j_input.json"))
        files.sort(key=lambda x: x.name, reverse=True)
        for file in files:
            txt = file.read_text()
            json_data = json.loads(txt)

            # print(f"File Upload started: {str(file.name)}")
            upload_to_neo4j(
                driver, json_data.get("nodes"), json_data.get("relationships")
            )
            # print(f"File Upload completed: {str(file.name)}")


except Exception:
    logger.error("neo4j library is not loaded.")

if __name__ == "__main__":
    set_basic_logging_config()
    input_root_path = "tests/data/neo4j/legacy"

    update_neo4j(input_root_path)
