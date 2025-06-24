import json
import logging
import types
from pathlib import Path
from typing import (
    Annotated,
    Any,
    OrderedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from mhd_model.model.v0_1.dataset.profiles.base.base import BaseMhdModel
from mhd_model.model.v0_1.dataset.profiles.base.graph_nodes import (
    CvTermObject,
    CvTermValueObject,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import MhdGraph
from mhd_model.model.v0_1.dataset.profiles.ms.graph_validation import (
    MHD_MS_PROFILE_V0_1,
)
from mhd_model.model.v0_1.dataset.validation.profile.base import (
    EmbeddedRefValidation,
    RelationshipValidation,
)
from mhd_model.model.v0_1.dataset.validation.profile.definition import (
    CvNodeValidation,
    CvTermValidation,
    MhDatasetValidation,
    NodePropertyValidation,
    NodeValidation,
    PropertyConstraint,
)
from scripts.utils import set_basic_logging_config

logger = logging.getLogger(__name__)


def get_relationship_rules(validations: MhDatasetValidation) -> tuple[dict, dict]:
    relationships = {}
    reverse_relationships = {}

    for nodes in [validations.mhd_nodes, validations.cv_nodes]:
        for node in nodes:
            if not node.relationships:
                continue
            for item in node.relationships:
                rel: RelationshipValidation = item
                if rel.source not in relationships:
                    relationships[rel.source] = {}
                if rel.relationship_name not in relationships[rel.source]:
                    relationships[rel.source][rel.relationship_name] = {}
                rels = relationships[rel.source][rel.relationship_name]
                if rel.source_property_name not in rels:
                    rels[rel.source_property_name] = []
                rels[rel.source_property_name].append(rel)

                if rel.target not in reverse_relationships:
                    reverse_relationships[rel.target] = {}
                rev_rels = reverse_relationships[rel.target]
                if rel.reverse_relationship_name not in rev_rels:
                    rev_rels[rel.reverse_relationship_name] = {}
                    rev_rels[rel.reverse_relationship_name][None] = []
                rev_rels[rel.reverse_relationship_name][None].append(rel)

    return relationships, reverse_relationships


def get_validation_rules(validations: MhDatasetValidation) -> dict:
    cv_term_validations_map = {}
    for nodes in [validations.mhd_nodes, validations.cv_nodes]:
        for node in nodes:
            for item in node.validations:
                node_type = item.node_type
                property_name = item.node_property_name or None
                condition = None
                if isinstance(item, CvTermValidation):
                    validation = item.validation
                    condition = item.condition
                elif isinstance(item, NodePropertyValidation):
                    validation = item.contraints
                else:
                    validation = item

                if not condition:
                    field_key = (node_type, property_name)
                    if field_key not in cv_term_validations_map:
                        cv_term_validations_map[field_key] = {}
                    key = (None, None, None, None, None, None, None)
                    if key not in cv_term_validations_map[field_key]:
                        cv_term_validations_map[field_key][key] = []
                    cv_term_validations_map[field_key][key].append(validation)
                else:
                    for cond_item in condition:
                        if cond_item.source_node_value:
                            field_key = (cond_item.source_node_type, None)
                        else:
                            field_key = (
                                cond_item.source_node_type,
                                cond_item.source_node_property,
                            )
                        if field_key not in cv_term_validations_map:
                            cv_term_validations_map[field_key] = {}
                        cond_key = (
                            cond_item.source_node_type,
                            cond_item.relationship_name,
                            node_type,
                            property_name,
                            cond_item.name,
                            cond_item.source_node_property,
                            cond_item.source_node_value,
                        )
                        if cond_key not in cv_term_validations_map[field_key]:
                            cv_term_validations_map[field_key][cond_key] = []
                        cv_term_validations_map[field_key][cond_key].append(validation)
    return cv_term_validations_map


def unwrap_union_excluding_none(annotation: Any) -> Any:
    """Return union element excluding NoneType, if applicable."""
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        return args[0] if args else None
    return annotation


def unwrap_annotated(annotation: Any) -> Any:
    """Unwrap Annotated and Union[None, T] to get the true base type."""
    annotation = unwrap_union_excluding_none(annotation)
    while get_origin(annotation) is Annotated:
        annotation = get_args(annotation)[0]
    return annotation


def get_type_name(annotation: Any) -> str:
    """Generate readable string for the annotation, including generics."""
    # Handle Annotated alias name
    origin = get_origin(annotation)
    if origin is Annotated:
        # processed = get_type_name(get_args(annotation)[0])
        annotation_name = getattr(annotation, "__name__")
        if annotation_name and annotation_name != Annotated.__name__:
            return annotation_name

        processed = get_type_name(get_args(annotation)[0])
        return processed

    # Handle Union (NoneType already removed)
    if origin in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        val = " | ".join(get_type_name(arg) for arg in args)
        return val

    # Handle generic types like List[T], Dict[K, V]
    origin = get_origin(annotation)
    if origin:
        arg_types = getattr(annotation, "__name__")
        if arg_types and arg_types in {set.__name__, dict.__name__, list.__name__}:
            name = get_args(annotation)[0].__name__
            if name in ["Union", "UnionType"]:
                name = get_type_name(get_args(annotation)[0])
            return f"{origin.__name__}[{name}]"

        arg_types = ", ".join(get_type_name(arg) for arg in get_args(annotation))
        return f"{origin.__name__}[{arg_types}]"

    val = getattr(annotation, "__name__", str(annotation).replace("typing.", ""))
    return val


def get_custom_type_alias(annotation: Any) -> str | None:
    """Get top-level Annotated alias name, if assigned (like 'ObjectId')."""
    if get_origin(annotation) is Annotated:
        return getattr(annotation, "__name__", None)
    return None


def get_inherited_fields(child_cls: type[BaseMhdModel], parent_cls: type[BaseMhdModel]) -> list:
    inherited = []

    parent_hints = get_type_hints(parent_cls, include_extras=True)
    child_hints = get_type_hints(child_cls, include_extras=True)

    for field in parent_hints:
        if field in child_hints:
            if child_hints[field] == parent_hints[field]:
                inherited.append(field)
        else:
            inherited.append(field)

    return inherited


def get_property_constraint(validations_map: dict, node: NodeValidation, field: str) -> None | PropertyConstraint:
    key = (node.node_type, field)
    if key in validations_map:
        vals = validations_map[key]
        for val in vals.values():
            for item in val:
                if isinstance(item, PropertyConstraint):
                    return item
    return None


def get_ref_constraint(validations_map: dict, node: NodeValidation, field: str) -> None | EmbeddedRefValidation:
    key = (node.node_type, field)
    if key in validations_map:
        vals = validations_map[key]
        for val in vals.values():
            for item in val:
                if isinstance(item, EmbeddedRefValidation):
                    return item
    return None


class NodeDocumentation(BaseModel):
    node_type: str
    name: None | str = None
    description: None | str = None
    properties: OrderedDict[str, list[str]] = OrderedDict()

    embedded_relationships: str = ""
    relationships: OrderedDict[tuple[str, str, str, str], list[str]] = OrderedDict()
    reverse_relationships: OrderedDict[tuple[str, str, str, str], list[str]] = (
        OrderedDict()
    )


def get_embedded_relationships(profile: MhDatasetValidation) -> tuple[dict, dict]:
    embedded_relationships = {}
    reverse_embedded_relationships = {}

    for node in profile.mhd_nodes:
        node_type = node.node_type

        for validation in node.validations:
            if isinstance(validation, EmbeddedRefValidation):
                if node_type not in embedded_relationships:
                    embedded_relationships[node_type] = {}

                embedded_relationships[node_type][validation.node_property_name] = (
                    validation
                )
                for item in validation.target_ref_types:
                    if item not in reverse_embedded_relationships:
                        reverse_embedded_relationships[item] = {}

                    reverse_embedded_relationships[item][
                        (validation.node_type, validation.node_property_name)
                    ] = validation

    return embedded_relationships, reverse_embedded_relationships


def get_default_value(
    node: NodeValidation, model: BaseMhdModel, field: str, info: FieldInfo
) -> tuple[bool | None, Any]:
    if (model is CvTermObject or model is CvTermValueObject) and field == "type_":
        return True, node.node_type
    else:
        default_val = info.get_default()
        if default_val != PydanticUndefined:
            if info.frozen:
                return True, default_val
            else:
                if default_val and field != "type_":
                    return False, default_val
        return None, None


def update_nodes(
    validation_rules_map: dict,
    node_documentation: dict[str, NodeDocumentation],
    node_doc: NodeDocumentation,
    node: NodeValidation,
) -> None:
    node_type = node.node_type
    model = None
    if isinstance(node, CvNodeValidation):
        model = CvTermObject
        if node.has_value:
            model = CvTermValueObject
    elif isinstance(node, NodeValidation):
        model = MhdGraph.get_mhd_class_by_type(node.node_type)
    if not model:
        logger.info("invalid type: %s", node.node_type)
        return

    # Node description
    doc = model.__doc__
    if doc:
        doc = doc.strip().replace("\n", "<br>")
    node_doc.description = doc

    for field, info in model.model_fields.items():
        if info.exclude:
            continue
        node_doc.properties[field] = []
        row = node_doc.properties[field]
        field_title = info.alias if info.alias else field

        field_type = get_type_name(info.annotation)
        required = info.is_required()
        min_length = None
        max_length = None
        prop_constraint = get_property_constraint(validation_rules_map, node, field)

        if prop_constraint:
            required = prop_constraint.required
            min_length = prop_constraint.min_length
            max_length = prop_constraint.max_length
            if prop_constraint.allowed_types:
                types = []
                if isinstance(prop_constraint.allowed_types, list):
                    types = [x for x in prop_constraint.allowed_types]
                else:
                    types = [prop_constraint.allowed_types]
                field_type = " or ".join(types)
        ref_constraint = get_ref_constraint(validation_rules_map, node, field)
        if ref_constraint:
            required = ref_constraint.required

        description = []
        if info.description:
            description.append(info.description.strip().strip("."))

        constant, default_value = get_default_value(node, model, field, info)

        if default_value is not None and constant:
            description.append(f"Its value MUST be <code>**{default_value}**</code>")
        elif default_value is not None and not constant:
            description.append(f"**Default value**: <code>{default_value}</code>")

        if min_length is not None:
            description.append(f"Minimum length: <code>{min_length}</code>")
        if max_length is not None:
            description.append(f"Maximum length: <code>{max_length}</code>")

        field_rules = []
        field_key = (node_type, field)
        node_rules = None

        for key in (field_key, (None, field)):
            if key in validation_rules_map:
                node_rules = validation_rules_map[key]
                for k, v in node_rules.items():
                    if k[6] is None:
                        for val in v:
                            field_rules.append(val)
        if field.endswith("_ref") or field.endswith("_refs"):
            target_node_type = None
            if node_rules:
                targets = [str(x[2]) for x in node_rules.keys() if x and x[2]]
                if len(targets) == 1:
                    target_node_type = (
                        f"Target CV term type: <code>**{targets[0]}**</code>"
                    )

                elif len(targets) > 1:
                    target_node_type = (
                        f"Target CV term types: <code>**{' or '.join(targets)}**</code>"
                    )
            if not target_node_type:
                name = (
                    field_title.removesuffix("_refs")
                    .removesuffix("_ref")
                    .replace("_", "-")
                )
                if name in node_documentation:
                    target_node_type = f"Target node type: <code>**{name}**</code>"

            if target_node_type:
                description.append(target_node_type)

        if field_rules:
            rules = [
                str(x).replace("\n", "<br>").replace(" [", "<br>* [")
                for x in field_rules
                if str(x) != "Required"
            ]
            if rules:
                description.append(
                    ("Validation Rules:" if len(rules) > 1 else "Validation Rule:")
                    + "<br> <code>"
                    + "<br>".join(rules)
                    + "</code>"
                )
        examples = info.examples
        if examples:
            description.append(
                "<br>Example: <br><code>"
                + "<br>".join(
                    [json.dumps(x, indent=2).replace("\n", "<br>") for x in examples]
                )
                + "</code>"
            )

        row.append(f"**{field_title}**")
        row.append(f"{'**required**' if required else 'optional'}")
        row.append(f"<code>*{field_type.replace(' | ', ' or ')}*<code>")
        row.append("<br>".join(description))


if __name__ == "__main__":
    set_basic_logging_config()
    profile = MHD_MS_PROFILE_V0_1
    validation_rules_map = get_validation_rules(profile)
    relationships_map, reverse_relationships_map = get_relationship_rules(profile)
    common_fields = {x for x in BaseMhdModel.model_fields}
    NO_CONDITION_KEY = (None, None, None, None, None, None)
    node_documentation: OrderedDict[str, NodeDocumentation] = OrderedDict()
    embedded_relationships, reverse_embedded_relationships = get_embedded_relationships(
        profile
    )

    for nodes in [profile.mhd_nodes, profile.cv_nodes]:
        for node in nodes:
            node_type = node.node_type

            name = " ".join(x.capitalize() for x in node_type.replace("-", " ").split())
            node_documentation[node_type] = NodeDocumentation(
                node_type=node_type, name=name
            )

    for nodes in [profile.mhd_nodes, profile.cv_nodes]:
        for node in nodes:
            update_nodes(
                validation_rules_map,
                node_documentation,
                node_documentation[node.node_type],
                node,
            )

            node_type = node.node_type
            node_doc = node_documentation[node_type]

            for relationships, target_map in [
                (relationships_map, node_doc.relationships),
                (reverse_relationships_map, node_doc.reverse_relationships),
            ]:
                if node_type not in relationships:
                    continue
                if node_type in embedded_relationships:
                    embedded_targets = embedded_relationships[node_type]
                    references = {}
                    for x in embedded_targets.values():
                        for y in x.target_ref_types:
                            if y not in references:
                                references[y] = set()
                            if x.node_property_name:
                                references[y].add(x.node_property_name)

                    node_doc.embedded_relationships = (
                        "<code>"
                        + ", ".join(sorted([x for x in references.keys()]))
                        + "</code>"
                    )
                node_relationships = relationships[node_type]
                for rels in node_relationships.values():
                    for rel_item in rels.values():
                        for rel in rel_item:
                            rel_key = (
                                rel.source or "",
                                rel.source_property_name or "",
                                rel.relationship_name,
                                rel.target or "",
                            )
                            field_key = (rel.source, None)
                            rules = []
                            if field_key in validation_rules_map:
                                node_rules = validation_rules_map[field_key]
                                for k, v in node_rules.items():
                                    if (
                                        k[0] == node_type
                                        and k[1] == rel.relationship_name
                                    ):
                                        if k[6] is not None:
                                            for val in v:
                                                rule = f"**Conditional - ({k[4]})**<br>[Source {k[5]} = {k[6]}]<br>{str(val)}"
                                                rules.append(rule)
                                        else:
                                            for val in v:
                                                rules.append(str(val))
                            rule_desc = None
                            if rules:
                                rule_desc = (
                                    (
                                        (
                                            "<br>Target Validation Rules:"
                                            if len(rules) > 1
                                            else "Target Validation Rule:"
                                        )
                                        + "<br><code>-----<br>"
                                        + "<br>-----<br>".join([str(x) for x in rules])
                                        + "</code><br>-----"
                                    )
                                    .replace("\n", "<br>")
                                    .replace(" [", "<br>* [")
                                )

                            desc = rel.description
                            min_in_dataset = None
                            max_in_dataset = None
                            if rel.min is not None and rel.min > 0:
                                prefix = "Required min count in the dataset"
                                min_in_dataset = f"**{prefix}: {rel.min}.**"

                            if rel.max is not None and rel.min > 0:
                                prefix = "Allowed max count in the dataset"
                                max_in_dataset = f"**{prefix}: {rel.max}.**"

                            description = "<br>".join(
                                [
                                    x
                                    for x in (
                                        desc,
                                        min_in_dataset,
                                        max_in_dataset,
                                        rule_desc,
                                    )
                                    if x
                                ]
                            )

                            # if rel_key not in node_doc.relationships:
                            target_map[rel_key] = [
                                rel.source or "",
                                rel.relationship_name or "",
                                rel.reverse_relationship_name or "",
                                rel.target or "",
                                (
                                    str(rel.min_for_each_source)
                                    if rel.min_for_each_source
                                    else "0"
                                ),
                                (
                                    str(rel.max_for_each_source)
                                    if rel.max_for_each_source
                                    else "N"
                                ),
                                description or "",
                            ]

                    # node_doc.relationships[]
    parent = Path("docs/mhd")
    parent.mkdir(parents=True, exist_ok=True)
    target_path = parent / Path("mhd-nodes.md")
    with target_path.open("w") as f:
        f.write("# Metabolomics Hub Common Data Model Nodes\n\n")

        for nodes, header in [
            (profile.mhd_nodes, "MHD Domain Objects"),
            (profile.cv_nodes, "MHD CV Term Objects"),
        ]:
            f.write(f"## {header}\n\n")
            for node in nodes:
                node_type = node.node_type
                node_doc = node_documentation[node_type]
                f.write(f"### {node_doc.name}\n\n")
                f.write("**Properties**\n\n")
                f.write("|Property Name|Necessity|Type|Description|\n")
                f.write("|-------------|---------|----|-----------|\n")
                for row in node_doc.properties.values():
                    f.write(f"|{'|'.join(row)}|\n")
                f.write("\n")
                source_rels = list(node_doc.relationships.values())
                source_rels.sort(key=lambda x: (x[0], x[1], x[2]))
                target_rels = list(node_doc.reverse_relationships.values())
                target_rels.sort(key=lambda x: (x[0], x[1], x[2]))
                for rel, embedded_rels, rel_name in [
                    (
                        source_rels,
                        node_doc.embedded_relationships,
                        "**Node Relationships**",
                    ),
                    (target_rels, None, "**Reverse Node Relationships**"),
                ]:
                    f.write(f"\n{rel_name}\n\n")

                    f.write(
                        "|Source|Relationship|Reverse Name|Target|Min|Max|Description|\n"
                    )
                    f.write(
                        "|------|------------|------------|------|---|---|-----------|\n"
                    )
                    for row in rel:
                        f.write(f"|{'|'.join(row)}|\n")
                    f.write("\n")
                    if embedded_rels:
                        f.write(f"\n**Embedded Relationships**: {embedded_rels}\n\n")
