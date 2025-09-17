import json
import logging
import sys
from pathlib import Path
from typing import Any

from mhd_model.model.v0_1.dataset.profiles.base.graph_nodes import Study
from mhd_model.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile

logger = logging.getLogger(__name__)


def create_neo4j_input_file(input_root_path: str, output_root_path: str):
    files = list(Path(input_root_path).glob("*.mhd.json"))
    files.sort(key=lambda x: x.name, reverse=True)
    for file in files:
        txt = file.read_text()
        json_data = json.loads(txt)
        mhd_dataset = MhDatasetLegacyProfile.model_validate(json_data)
        nodes_map = {x.id_: x for x in mhd_dataset.graph.nodes}
        relationships_map = {x.id_: x for x in mhd_dataset.graph.relationships}
        # embedded_refs = []
        nodes: list[dict[str, Any]] = []
        relationships: list[dict[str, Any]] = []
        study_id = ""
        for node in nodes_map.values():
            if isinstance(node, Study):
                study_id = node.repository_identifier
            properties = {}
            for key, value in node.model_dump(exclude_none=True).items():
                refs = []
                if key == "id_":
                    continue
                if key.endswith("_ref"):
                    ref = getattr(node, key, None)
                    if hasattr(nodes_map[ref], "name"):
                        val = getattr(nodes_map[ref], "name")
                        properties[key.replace("_ref", "")] = val
                    refs.append(ref)
                elif key.endswith("_refs"):
                    refs = getattr(node, key, [])
                    vals = []
                    for ref in refs:
                        if hasattr(nodes_map[ref], "name"):
                            val = getattr(nodes_map[ref], "name")
                            if val and val not in vals:
                                vals.append(val)
                    properties[key.replace("_refs", "") + "_list"] = vals
                if refs:
                    link_name = "EMBEDDED_" + key.replace("_ref", "").replace(
                        "_refs", ""
                    ).upper().replace("-", "_")
                    for ref in refs:
                        relationships.append(
                            {
                                "start": node.id_,
                                "end": ref,
                                "type": link_name,
                                "properties": {},
                            }
                        )

                if not refs:
                    if isinstance(value, list):
                        properties[key] = [str(x) for x in value]
                    elif isinstance(value, dict):
                        properties[key] = json.dumps(
                            {k: str(v) for k, v in value.items()}
                        )
                    elif (
                        isinstance(value, str)
                        or isinstance(value, int)
                        or isinstance(value, float)
                        or isinstance(value, bool)
                    ):
                        properties[key] = value
                    else:
                        properties[key] = str(value)

            if not hasattr(properties, "name"):
                properties["name"] = node.label

            nodes.append(
                {"id": node.id_, "labels": [node.type_], "properties": properties}
            )

        for rel in relationships_map.values():
            # if nodes_map[rel.source_ref].type_ == "study" and nodes_map[
            #     rel.target_ref
            # ].type_ in {
            #     "raw-data-file",
            #     "derived-data-file",
            #     "supplementary-file",
            #     # "metabolite",
            # }:
            #     continue
            # if nodes_map[rel.target_ref].type_ == "study" and nodes_map[
            #     rel.source_ref
            # ].type_ in {
            #     "raw-data-file",
            #     "derived-data-file",
            #     "supplementary-file",
            #     # "metabolite",
            # }:
            #     continue
            relationships.append(
                {
                    "start": rel.source_ref,
                    "end": rel.target_ref,
                    "type": rel.relationship_name.upper().replace("-", "_"),
                    "properties": rel.model_dump(exclude_none=True),
                }
            )
        output_file = Path(output_root_path) / Path(f"{study_id}_neo4j_input.json")
        with Path(output_file).open("w") as f:
            json.dump({"nodes": nodes, "relationships": relationships}, f, indent=2)
        # print(f"File Upload started: {str(file.name)}")
        #
        # print(f"File Upload started: {str(file.name)}")
        # upload_to_neo4j(nodes, relationships)
        # print(f"File Upload completed: {str(file.name)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )
    input_root_path = "tests/data/mhd_data/legacy"
    output_root_path = "tests/data/neo4j/legacy"

    create_neo4j_input_file(input_root_path, output_root_path)
