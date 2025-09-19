import json
import logging
from pathlib import Path
from typing import Any

from mhd_model.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile

logger = logging.getLogger(__name__)


def create_neo4j_input_file(input_file_path: str, output_file_path: str):
    file = Path(input_file_path)
    txt = file.read_text()
    json_data = json.loads(txt)
    mhd_dataset = MhDatasetLegacyProfile.model_validate(json_data)
    nodes_map = {x.id_: x for x in mhd_dataset.graph.nodes}
    relationships_map = {x.id_: x for x in mhd_dataset.graph.relationships}
    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for node in nodes_map.values():
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
                    properties[key] = json.dumps({k: str(v) for k, v in value.items()})
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

        nodes.append({"id": node.id_, "labels": [node.type_], "properties": properties})

    for rel in relationships_map.values():
        relationships.append(
            {
                "start": rel.source_ref,
                "end": rel.target_ref,
                "type": rel.relationship_name.upper().replace("-", "_"),
                "properties": rel.model_dump(exclude_none=True),
            }
        )
    output_file = Path(output_file_path)
    with Path(output_file).open("w") as f:
        json.dump({"nodes": nodes, "relationships": relationships}, f, indent=2)
