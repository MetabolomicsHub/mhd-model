import json
from pathlib import Path
from typing import Any

import click

from mhd_model.model.definitions import (
    MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME,
    MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
    MHD_MODEL_V0_1_MS_PROFILE_NAME,
)
from mhd_model.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile
from mhd_model.model.v0_1.dataset.profiles.ms.profile import MhDatasetMsProfile
from mhd_model.shared.model import ProfileEnabledDataset


@click.command(name="neo4j-input", no_args_is_help=True)
@click.option(
    "--output-dir",
    default="outputs",
    show_default=True,
    help="Output directory for neo4j input file",
)
@click.option(
    "--output-filename",
    default=None,
    show_default=True,
    help="neo4j input filename (e.g., MHD000001.neo4j_input.json, ST000001.neo4j_input.json)",
)
@click.argument("mhd_study_id")
@click.argument("mhd_model_file_path")
def create_neo4j_input_file_task(
    mhd_study_id: str,
    mhd_model_file_path: str,
    output_dir: str,
    output_filename: str,
):
    """Create neo4j input file from MHD data model file.

    Args:

    mhd_study_id (str): MHD study identifier

    mhd_model_file_path (str): MHD data model path


    output_dir (str): Output directory of neo4j input file

    output_filename (str): Name of neo4j input file. Default is <repository identifier>.neo4j_input.json
    """
    file = Path(mhd_model_file_path)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    txt = file.read_text()
    json_data = json.loads(txt)

    profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(json_data)
    mhd_dataset = None
    if profile.schema_name == MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME:
        if profile.profile_uri == MHD_MODEL_V0_1_LEGACY_PROFILE_NAME:
            mhd_dataset = MhDatasetLegacyProfile.model_validate(json_data)
        elif profile.profile_uri == MHD_MODEL_V0_1_MS_PROFILE_NAME:
            mhd_dataset = MhDatasetMsProfile.model_validate(json_data)
        else:
            click.echo(f"{profile.profile_uri} is not supported.")
            exit(1)
    else:
        click.echo(f"{profile.schema_name} is not schema.")
        exit(1)

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

        properties["label"] = node.label

        nodes.append(
            {
                "id": node.id_,
                "labels": [node.type_],
                "properties": properties,
            }
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
    output_file = f"{output_dir}/{mhd_study_id}.neo4j_input.json"
    if output_filename:
        output_file = f"{output_dir}/{output_filename}"

    with Path(output_file).open("w") as f:
        json.dump({"nodes": nodes, "relationships": relationships}, f, indent=2)

    click.echo(f"{output_file} is created.")
