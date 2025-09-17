import logging
import re
from typing import Any, Generator, OrderedDict

import jsonschema
from jsonschema import ValidationError, protocols

from mhd_model.model.v0_1.dataset.profiles.base.base import (
    BaseMhdRelationship,
    IdentifiableMhdModel,
)
from mhd_model.model.v0_1.dataset.profiles.base.graph_nodes import (
    CvTermObject,
    CvTermValueObject,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import MhdGraph
from mhd_model.model.v0_1.dataset.profiles.base.relationships import Relationship
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
)
from mhd_model.model.v0_1.rules.managed_cv_terms import MANAGED_CV_TERM_OBJECTS
from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.cv_term_helper import CvTermHelper
from mhd_model.shared.validation.definitions import (
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    ParentCvTerm,
)

logger = logging.getLogger(__name__)

NodeByIndexDict = dict[str, tuple[int, IdentifiableMhdModel]]
IdentifiableElementDict = OrderedDict[str, IdentifiableMhdModel]


class MhdModelValidator:
    def __init__(self, node_validation: MhDatasetValidation):
        self.cv_helper = CvTermHelper()
        self.node_validation: MhDatasetValidation = node_validation

    def anyOf(self, validator, anyOf, instance, schema):
        node_class = None
        all_errors = []
        if isinstance(instance, dict):
            node_class = MhdGraph.get_node_class(instance)
            if node_class:
                subschema = {"$ref": f"#/$defs/{node_class.__name__}"}
                if node_class is not None and subschema in anyOf:
                    index = anyOf.index(subschema)
                    errors = list(
                        validator.descend(instance, subschema, schema_path=index)
                    )
                    if errors:
                        for error in errors:
                            yield error
        else:
            optional_type = {"type": "null"}
            if len(anyOf) == 2 and optional_type in anyOf:
                null_errs = None
                other_errors = None
                for index, subschema in enumerate(anyOf):
                    errs = list(
                        validator.descend(instance, subschema, schema_path=index)
                    )
                    if subschema == optional_type:
                        null_errs = errs
                    else:
                        other_errors = errs
                if not null_errs:
                    return
                if other_errors:
                    for error in other_errors:
                        yield error
        if node_class:
            return
        for index, subschema in enumerate(anyOf):
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                break
            all_errors.extend(errs)
        else:
            yield jsonschema.ValidationError(
                f"{instance!r} is not valid under any of the given schemas",
                context=all_errors,
            )

    def validate_graph(
        self,
        validator: protocols.Validator,
        validator_value: str | dict,
        instance: str | dict,
        schema: dict[str, Any],
    ):
        nodes_path = "nodes"
        relationhips_path = "relationships"

        nodes: list[dict[str, Any]] = instance.get(nodes_path, [])
        relationhips = instance.get(relationhips_path, [])

        unique_nodes: IdentifiableElementDict = OrderedDict()
        nodes_by_type: dict[str, NodeByIndexDict] = {}
        yield from self.update_unique_nodes(
            nodes, unique_nodes, nodes_by_type, nodes_path
        )

        yield from self.check_start_items(instance, unique_nodes, nodes_path)

        yield from self.check_embedded_ref_ids_exist(
            nodes, unique_nodes, nodes_path, "node"
        )

        unique_relationships: OrderedDict = OrderedDict()
        relationships_by_name = {}
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]] = {}
        yield from self.update_unique_relationships(
            relationhips,
            unique_relationships,
            relationships_by_name,
            relationships_index,
            relationhips,
            nodes_path,
        )
        yield from self.check_embedded_ref_ids_exist(
            relationhips, unique_nodes, relationhips_path, "relationship"
        )

        yield from self.validate_profile(
            self.node_validation,
            unique_nodes,
            nodes_by_type,
            relationships_by_name,
            relationships_index,
            nodes_path,
        )

    def check_start_items(self, instance, unique_nodes, nodes_path):
        logger.info("Start item reference check task started...")

        start_item_refs_path = "start_item_refs"
        start_item_refs = instance.get(start_item_refs_path)
        start_node_error_message = ""
        if not start_item_refs:
            start_node_error_message = "Start node is not defined."
            yield jsonschema.ValidationError(
                message=start_node_error_message,
                validator="start-node-validation",
                context=(),
                path=(nodes_path, start_item_refs_path),
                instance=start_item_refs,
            )

        for idx, start in enumerate(start_item_refs):
            start_item = unique_nodes.get(start)
            if not start_item:
                start_node_error_message = f"Start item {start} does not exist."
                yield jsonschema.ValidationError(
                    message=start_node_error_message,
                    validator="start-node-validation",
                    context=(),
                    path=(nodes_path, start_item_refs_path, idx),
                    instance=start,
                )
        logger.info("Start item reference check task ended.")

    def update_unique_relationships(
        self,
        nodes,
        unique_relationships,
        relationships_by_name,
        relationships_index,
        instance,
        nodes_path,
    ):
        if not instance:
            logger.warning("There is no relationship. Skipping")
            return

        for idx, item in enumerate(instance):
            if not item.get("id") or not item.get("type"):
                yield jsonschema.ValidationError(
                    message=f"Relationship at index {idx} does not have a valid id or type property",
                    validator="invalid-relationship",
                    context=(),
                    path=(nodes_path, idx),
                    instance=instance[idx],
                )
                continue
            rel: BaseMhdRelationship = None
            try:
                rel = BaseMhdRelationship.model_validate(item)
            except ValueError:
                pass

            if not rel:
                logger.error("relationship at index %s is not valid. ", idx)
                continue

            if rel.id_ in unique_relationships:
                prev_rel = unique_relationships.get(rel.id_)
                prev_idx, _ = relationships_by_name.get(
                    prev_rel.relationship_name, {}
                ).get(prev_rel.id_, (None, None))

                yield jsonschema.ValidationError(
                    message=f"Relationship id is not unique. {rel.id_} at index {idx} and {prev_idx}",
                    validator="unique-relationship-id",
                    context=(),
                    path=(nodes_path, idx),
                    instance=instance[idx],
                )
                continue
            unique_relationships[rel.id_] = rel
            if rel.relationship_name not in relationships_by_name:
                relationships_by_name[rel.relationship_name] = {}
                relationships_index[rel.relationship_name] = {}
            if rel.source_ref not in relationships_index[rel.relationship_name]:
                relationships_index[rel.relationship_name][rel.source_ref] = {}
            source_index = relationships_index[rel.relationship_name][rel.source_ref]
            if rel.target_ref not in source_index:
                source_index[rel.target_ref] = []
            source_index[rel.target_ref].append((idx, rel))
            relationships_by_name[rel.relationship_name][rel.id_] = (idx, rel)

    def update_unique_nodes(
        self,
        nodes: list[dict[str, Any]],
        unique_nodes: IdentifiableElementDict,
        nodes_by_type: dict[str, NodeByIndexDict],
        nodes_path: str,
    ):
        if not nodes:
            logger.info(
                "There is no item. Node id and type consistency check is skipped."
            )
            return
        logger.info(
            "Start node id and type consistency checks for %s items...", len(nodes)
        )
        for idx, item in enumerate(nodes):
            if not item.get("id") or not item.get("type"):
                yield jsonschema.ValidationError(
                    message=f"Node at index {idx} does not have id or type property value",
                    validator="invalid-node",
                    context=(),
                    path=(nodes_path, idx),
                    instance=nodes[idx],
                )
                continue
            node: None | IdentifiableMhdModel = None
            try:
                node = MhdGraph.create_model(item)
            except Exception as err:
                try:
                    node = IdentifiableMhdModel.model_validate(item)
                    logger.warning(
                        "%s: '%s' node at index %s is not validated. %s"
                        "It is created as basic model and ignored all properties.",
                        node.type_,
                        idx,
                        node.id_,
                        str(err),
                    )
                except Exception as err:
                    logger.warning(
                        "%s: '%s' node at index %s is not validated. %s",
                        item.get("id"),
                        item.get("type"),
                        idx,
                        str(err),
                    )

            node_type: str = item.get("type", "")
            if not node and not node_type.startswith("x-"):
                yield jsonschema.ValidationError(
                    message=f"Node at index {idx} is not common node. "
                    "Define custom nodes with with x-<repository id> prefix.",
                    validator="not-common-node",
                    context=(),
                    path=(nodes_path, idx),
                    instance=nodes[idx],
                )
                continue

            if isinstance(node, CvTermObject) or isinstance(node, CvTermValueObject):
                if (
                    node.type_ not in MANAGED_CV_TERM_OBJECTS
                    and not node.type_.startswith("x-")
                ):
                    yield jsonschema.ValidationError(
                        message=f"{node.id_}: Node at index {idx} does not have a valid type. "
                        "If you create custom node, its type must start with x-<repository id>",
                        validator="valid-term-node",
                        context=(),
                        path=(nodes_path, idx),
                        instance=nodes[idx],
                    )
                elif "--" + node.type_ + "--" not in node.id_:
                    yield jsonschema.ValidationError(
                        message=f"{node.id_}: Node at index {idx} does not have a valid type and id pair. "
                        f"Type: {node.type_} id: {node.id_}",
                        validator="valid-term-node",
                        context=(),
                        path=(nodes_path, idx),
                        instance=nodes[idx],
                    )
            elif not node.id_.startswith("mhd--" + node.type_ + "--"):
                yield jsonschema.ValidationError(
                    message=f"{node.id_}: Node at index {idx} does not have a valid type and id. "
                    f"Type: {node.type_} id: {node.id_}",
                    validator="valid-term-node",
                    context=(),
                    path=(nodes_path, idx),
                    instance=nodes[idx],
                )
            if node.id_ in unique_nodes:
                obj = unique_nodes.get(node.id_)
                node_idx, _ = nodes_by_type.get(obj.type_, {}).get(
                    obj.id_, (None, None)
                )

                yield jsonschema.ValidationError(
                    message=f"{node.id_}: Id is not unique for indices {idx} and {node_idx}",
                    validator="unique-node-id",
                    context=(),
                    path=(nodes_path, idx),
                    instance=nodes[idx],
                )
                logger.warning(
                    "%s: Id is not unique for indices %s and %s."
                    "Node at %s will be skipped.",
                    node.id_,
                    idx,
                    node_idx,
                    idx,
                )
                continue
            unique_nodes[node.id_] = node
            if node.type_ not in nodes_by_type:
                nodes_by_type[node.type_] = {}
            nodes_by_type[node.type_][node.id_] = (idx, node)

        logger.info("Node id and type consistency checks are ended.")

    def check_embedded_ref_ids_exist(
        self,
        items: list[dict[str, Any]],
        unique_items: IdentifiableElementDict,
        item_path: str,
        item_name: str,
    ) -> Generator[Any, Any, jsonschema.ValidationError]:
        if not items:
            logger.info(
                "There is no item. Embedded reference check in %s items is skipped.",
                item_name,
            )
            return
        logger.info(
            "Start embedded reference checks in %s %s items...",
            len(items),
            item_name,
        )

        for idx, node in enumerate(items):
            if "id" not in node or node["id"] not in unique_items:
                continue
            item = unique_items[node["id"]]
            for prop in item.model_fields:
                if prop.endswith("_ref"):
                    val = getattr(item, prop)
                    if not val:
                        continue
                    if val not in unique_items:
                        yield jsonschema.ValidationError(
                            message=f"There is no {item_name} with id {val}",
                            validator=f"referenced-{item_name}",
                            context=(),
                            path=[item_path, idx, prop],
                            instance=item,
                        )
                elif prop.endswith("_refs"):
                    vals = getattr(item, prop)
                    if not vals:
                        continue
                    for sub_idx, sub_val in enumerate(vals):
                        if sub_val not in unique_items:
                            yield jsonschema.ValidationError(
                                message=f"There is no {item_name} with id {sub_val}.",
                                validator=f"referenced-{item_name}",
                                context=(),
                                path=[item_path, idx, prop, sub_idx],
                                instance=item,
                            )

        logger.info("Embedded reference check in %s items is ended...", item_name)

    def validate_profile(
        self,
        node_validation: MhDatasetValidation,
        nodes: IdentifiableElementDict,
        nodes_by_type: dict[str, NodeByIndexDict],
        relationships_by_name: dict[str, dict[str, tuple[int, str]]],
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]],
        nodes_path: str,
    ) -> Generator[Any, Any, jsonschema.ValidationError]:
        if not node_validation:
            yield jsonschema.ValidationError(
                message="There is no validation profile",
                validator="validation-profile-check",
                context=(),
                path=nodes_path,
                instance={},
            )
        for validation_nodes in (node_validation.mhd_nodes, node_validation.cv_nodes):
            for validation_item in validation_nodes:
                item: NodeValidation = validation_item
                errors = self.check_nodes(item, nodes_by_type)

                for error in errors:
                    yield error
                if item.relationships:
                    for relationship_list in item.relationships:
                        errors = self.check_relationships(
                            relationship_list,
                            nodes,
                            nodes_by_type,
                            relationships_by_name,
                            relationships_index,
                        )

                        for error in errors:
                            yield error
        for validation_nodes in (node_validation.mhd_nodes, node_validation.cv_nodes):
            for node in validation_nodes:
                for item in node.validations:
                    errors = []
                    if isinstance(item, NodePropertyValidation):
                        errors = self.check_property_constraint(
                            item, nodes_by_type, nodes_path
                        )
                    elif isinstance(item, CvTermValidation):
                        selected_items = self.filter_validation(
                            item,
                            nodes,
                            nodes_by_type,
                            relationships_index=relationships_index,
                        )
                        if not selected_items:
                            continue
                        if isinstance(item.validation, AllowedCvTerms):
                            errors = self.run_allowed_cv_terms_validation(
                                nodes,
                                item,
                                selected_items,
                                path=nodes_path,
                            )
                        elif isinstance(item.validation, AllowAnyCvTerm):
                            errors = self.run_allow_any_cv_terms_validation(
                                nodes,
                                item,
                                nodes_by_type,
                                selected_items,
                                path=nodes_path,
                            )
                        elif isinstance(item.validation, AllowedChildrenCvTerms):
                            errors = self.run_allow_children_cv_terms_validation(
                                nodes,
                                item,
                                nodes_by_type,
                                selected_items,
                                path=nodes_path,
                            )
                        elif isinstance(item.validation, AllowedCvList):
                            errors = self.run_allow_cv_list_validation(
                                nodes,
                                item,
                                nodes_by_type,
                                relationships_index,
                                selected_items,
                                path=nodes_path,
                            )
                    elif isinstance(item, EmbeddedRefValidation):
                        errors = self.validate_embedded_refs(item, nodes, nodes_by_type)

                    if errors:
                        for error in errors:
                            yield error
        # placeholders = [CvTermPlaceholder(source="", accession="")]
        errors = self.check_custom_nodes(
            nodes_by_type, "parameter-definition", path=nodes_path
        )
        # errors.extend(self.check_custom_nodes(nodes_by_type, "factor-definition"))
        # errors.extend(
        #     self.check_custom_nodes(nodes_by_type, "characteristic-definition")
        # )
        if errors:
            for error in errors:
                yield error

    def validate_embedded_refs(
        self,
        item: EmbeddedRefValidation,
        nodes: IdentifiableElementDict,
        nodes_by_type: dict[str, NodeByIndexDict],
    ) -> list[jsonschema.ValidationError]:
        errors = []
        selected_nodes: NodeByIndexDict = nodes_by_type.get(item.node_type, {})
        prop_name = item.node_property_name
        for idx, node in selected_nodes.values():
            vals = getattr(node, item.node_property_name, None)

            if not vals:
                continue

            is_list = True if isinstance(vals, (list, set)) else False
            vals = vals if is_list else [vals]

            for ref_idx, val in enumerate(vals):
                sub_path = ("nodes", idx, prop_name)
                if is_list:
                    sub_path = ("nodes", idx, prop_name, ref_idx)
                if not val and item.required:
                    errors.append(
                        jsonschema.ValidationError(
                            message=f"{node.id_}: '{node.type_}' node at index "
                            f"{idx} has a required property "
                            f" '{item.node_property_name}' but its value is not defined.",
                            validator="embedded-key-check",
                            context=(),
                            path=sub_path,
                            instance={},
                        )
                    )
                else:
                    ref_node: None | IdentifiableMhdModel = nodes.get(val, None)
                    if not ref_node:
                        logger.warning("%s id is not valid. Skipping...", val)
                        continue
                    matched = False
                    refs = item.target_ref_types or []
                    if not refs:
                        logger.error(
                            "Embedded validation type error."
                            " There is not target ref types for"
                            "node type: %s, property name: %s. Skipping...",
                            item.node_type,
                            item.node_property_name,
                        )
                        continue
                    for target in refs:
                        if (
                            ref_node.type_ == target
                            or ref_node.type_.startswith("x-")
                            and ref_node.type_.endswith("-" + target)
                        ):
                            matched = True
                            break
                    if not matched:
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node.id_}: '{node.type_}' node at index "
                                f"{idx} has a required property but "
                                "referenced node type is not in allowed for this property."
                                f"Allowed type(s): {', '.join(refs)}"
                                f"'{item.node_property_name}' {val}",
                                validator="embedded-key-check",
                                context=(),
                                path=sub_path,
                                instance={},
                            )
                        )
        return errors

    def check_property_constraint(
        self, item: NodePropertyValidation, nodes_by_type: dict, path: str = None
    ) -> list[jsonschema.ValidationError]:
        nodes = nodes_by_type.get(item.node_type, {})
        errors = []
        for node_idx, node_data in nodes.values():
            if hasattr(node_data, item.node_property_name):
                val = getattr(node_data, item.node_property_name)
                min_length_violation = False
                if item.contraints.min_length:
                    min_length = 0 if not val else len(val)
                    if min_length < item.contraints.min_length:
                        sub_path = [path, node_idx] if path else [node_idx]
                        min_length_violation = True
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node_data.id_}: '{node_data.type_}' node at index "
                                f"{node_idx} has a property named '{item.node_property_name}' "
                                f"that violates min length rule. Actual: {min_length}, Expected: {item.contraints.min_length}",
                                validator="check-property-constraint",
                                context=(),
                                path=sub_path,
                                instance={},
                            )
                        )
                if item.contraints.max_length:
                    max_length = len(val) if val else None
                    if max_length and max_length > item.contraints.min_length:
                        sub_path = [path, node_idx] if path else [node_idx]
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node_data.id_}: '{node_data.type_}' node at index "
                                f"{node_idx} has a property named '{item.node_property_name}' "
                                f"that violates max length rule. Actual: {max_length}, Expected: {item.contraints.min_length}",
                                validator="check-property-constraint",
                                context=(),
                                path=sub_path,
                                instance={},
                            )
                        )
                if item.contraints.pattern and val is not None:
                    if not re.match(item.contraints.pattern, val):
                        sub_path = [path, node_idx] if path else [node_idx]
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node_data.id_}: '{node_data.type_}' node at index "
                                f"{node_idx} has a property named '{item.node_property_name}' "
                                f"that violates pattern rule. Actual: {val}, Expected pattern: {item.contraints.pattern}",
                                validator="check-property-constraint",
                                context=(),
                                path=sub_path,
                                instance={},
                            )
                        )
                if not min_length_violation and item.contraints.required:
                    if not val:
                        sub_path = [path, node_idx] if path else [node_idx]
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node_data.id_}: '{node_data.type_}' node at index "
                                f"{node_idx} has a property named '{item.node_property_name}' "
                                f"that violates required rule.",
                                validator="check-property-constraint",
                                context=(),
                                path=sub_path,
                                instance={},
                            )
                        )
        return errors

    def check_custom_nodes(
        self, nodes_by_type: dict, type_name: None | str = None, path: str = None
    ) -> list[jsonschema.ValidationError]:
        errors = []
        for node_type, values in nodes_by_type.items():
            if node_type.startswith("x-"):
                if type_name and type_name not in node_type:
                    continue
                item_values = list(values.values())

                if (
                    item_values
                    and item_values[0]
                    and isinstance(item_values[0][1], CvTerm)
                ):
                    item = CvTermValidation(
                        node_type=node_type,
                        validation=AllowAnyCvTerm(),
                    )

                    errors = self.run_allow_any_cv_terms_validation(
                        item,
                        nodes_by_type,
                        nodes_by_type[item.node_type].values(),
                        path=path,
                    )
        return errors

    def run_allow_cv_list_validation(
        self,
        nodes: dict,
        check: CvTermValidation,
        nodes_by_type: dict,
        relationships_index: dict[
            str, dict[str, dict[str, tuple[int, Relationship]]]
        ] = None,
        selected_items: None | list[Any] = None,
        path: str = None,
    ) -> list[jsonschema.ValidationError]:
        if check.node_type not in nodes_by_type:
            return []
        errors = []
        property_name = check.node_property_name
        placeholder_values = set()
        if check.validation.allowed_placeholder_values:
            placeholder_values = {
                (x.source, x.accession)
                for x in check.validation.allowed_placeholder_values
            }

        missing_values = set()
        if check.validation.allowed_missing_cv_terms:
            missing_values = {
                (x.source, x.accession, x.name)
                for x in check.validation.allowed_missing_cv_terms
            }

        other_sources = set()
        if check.validation.allowed_other_sources:
            other_sources = {x for x in check.validation.allowed_other_sources}
        for idx, value in selected_items:
            run_validation = self.check_condition(
                value,
                check,
                nodes_by_type,
                relationships_index,
            )

            if run_validation:
                result = self.check_cv_term_in_list(
                    nodes,
                    idx,
                    value,
                    property_name,
                    placeholder_values,
                    missing_values,
                    other_sources,
                    check,
                    path=path,
                )
                if result:
                    errors.extend(result)
        return errors

    def check_condition(
        self,
        value: IdentifiableMhdModel,
        check: CvTermValidation,
        nodes_by_type: dict,
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]],
    ) -> list[jsonschema.ValidationError]:
        run_validation = False
        if not check.condition:
            return run_validation
        for condition_item in check.condition:
            rel_name = condition_item.relationship_name
            if rel_name not in relationships_index:
                continue
            target_rels = relationships_index.get(rel_name)
            if value.id_ not in target_rels:
                continue
            targets = target_rels.get(value.id_)
            for target_ref in targets.keys():
                if not nodes_by_type.get(condition_item.start_node_type):
                    continue
                target_nodes = nodes_by_type.get(condition_item.start_node_type)
                if not target_nodes:
                    continue
                target_tuple = target_nodes.get(target_ref)
                if target_tuple:
                    target = target_tuple[1]
                    if hasattr(target, "accession"):
                        accession = getattr(target, "accession")
                        if accession == condition_item.expression_value:
                            run_validation = True
                            break
            if run_validation:
                break
        return run_validation

    def check_cv_term_in_list(
        self,
        nodes: dict,
        idx: int,
        node: IdentifiableMhdModel,
        property_name: None | str = None,
        placeholder_values: None | set[tuple[str, str]] = None,
        missing_values: None | set[tuple[str, str, str]] = None,
        other_sources: None | set[tuple[str, str]] = None,
        check: None | CvTermValidation = None,
        path: str = None,
    ) -> list[jsonschema.ValidationError]:
        items, is_list, error = self.get_items(nodes, idx, node, property_name)
        if error:
            return [error]
        if not items:
            return None
        errors = []
        validation: AllowedCvList = check.validation
        source_names = {x for x in validation.source_names}
        for sub_idx, term in enumerate(items):
            item: CvTermObject = term

            item_key = (item.source, item.accession)
            accession_prefix = (
                item.accession.split(":")[0]
                if ":" in item.accession
                else item.accession
            )
            item_full_key = (item.source, item.accession, item.name)
            if (
                not isinstance(item, CvTermValueObject)
                and placeholder_values
                and item_key in placeholder_values
            ):
                continue
            if other_sources and accession_prefix in other_sources:
                continue
            if missing_values and item_full_key in missing_values:
                continue
            if path:
                sub_path = [path, idx, property_name] if property_name else [path, idx]
            else:
                sub_path = [idx, property_name] if property_name else [idx]
            message = f"{node.id_}: {node.type_} node at index {idx} with value "
            if property_name:
                message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its value "
                if is_list:
                    message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its {sub_idx}. index item "
            if is_list:
                sub_path.append(sub_idx)
            valid = False
            error_message = ""
            if item.source in source_names:
                valid, error_message = self.cv_helper.check_cv_term(item)
            if not error_message:
                error_message = ""
            else:
                error_message = " " + error_message
            if not valid:
                errors.append(
                    jsonschema.ValidationError(
                        message=message
                        + f"[{item.source}, {item.accession}, {item.name}] "
                        f"is not allowed cv term. "
                        f"Allowed cv term sources: {str(source_names)}.{error_message}",
                        validator="check-cv-source",
                        context=(),
                        path=sub_path,
                        instance={},
                    )
                )

        return errors

    def run_allow_children_cv_terms_validation(
        self,
        nodes: dict,
        check: CvTermValidation,
        nodes_by_type: dict,
        selected_items: list[Any],
        path: str = None,
    ) -> None | list[jsonschema.ValidationError]:
        if check.node_type not in nodes_by_type:
            return None
        errors = []
        property_name = check.node_property_name
        placeholder_values = set()
        if check.validation.allowed_placeholder_values:
            placeholder_values = {
                (x.source, x.accession)
                for x in check.validation.allowed_placeholder_values
            }

        missing_values = set()
        if check.validation.allowed_missing_cv_terms:
            missing_values = {
                (x.source, x.accession, x.name)
                for x in check.validation.allowed_missing_cv_terms
            }

        other_sources = set()
        if check.validation.allowed_other_sources:
            other_sources = {x for x in check.validation.allowed_other_sources}
        for item in selected_items:
            result = self.check_children_cv_term(
                nodes,
                item[0],
                item[1],
                property_name,
                placeholder_values,
                missing_values,
                other_sources,
                check.validation.parent_cv_terms,
                path=path,
            )
            if result:
                errors.extend(result)
        return errors

    def check_children_cv_term(
        self,
        nodes: dict,
        idx: int,
        node: IdentifiableMhdModel,
        property_name: None | str = None,
        placeholder_values: None | set[tuple[str, str]] = None,
        missing_values: None | set[tuple[str, str, str]] = None,
        other_sources: None | set[tuple[str, str]] = None,
        parent_cv_terms: None | list[ParentCvTerm] = None,
        path: str = None,
    ) -> list[jsonschema.ValidationError]:
        items, is_list, error = self.get_items(nodes, idx, node, property_name)
        if error:
            return [error]
        if not items:
            return None
        errors = []
        for sub_idx, term in enumerate(items):
            item: CvTermObject = term
            if not item.accession:
                item.accession = ""
            item_key = (item.source, item.accession)
            accession_prefix = (
                item.accession.split(":")[0]
                if ":" in item.accession
                else item.accession
            )
            item_full_key = (item.source, item.accession, item.name)
            if (
                not isinstance(item, CvTermValueObject)
                and placeholder_values
                and item_key in placeholder_values
            ):
                continue
            if other_sources and accession_prefix in other_sources:
                continue
            if missing_values and item_full_key in missing_values:
                continue
            if path:
                sub_path = [path, idx, property_name] if property_name else [path, idx]
            else:
                sub_path = [idx, property_name] if property_name else [idx]
            message = f"{node.id_}: {node.type_} node at index {idx} with value "
            if property_name:
                message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its value "
                if is_list:
                    message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its {sub_idx}. index item "
            if is_list:
                sub_path.append(sub_idx)
            valid_parents = [x.cv_term for x in parent_cv_terms]
            for x in parent_cv_terms:
                valid, error_message = self.cv_helper.check_cv_term(item, x)
                if valid:
                    continue
            error_message = error_message if error_message else ""
            if not valid:
                errors.append(
                    jsonschema.ValidationError(
                        message=message
                        + f"[{item.source}, {item.accession}, {item.name}] "
                        f"is not child of any parent cv term. "
                        f"Valid parents: {str(valid_parents)}. Error: {error_message}",
                        validator="check-child-cv-term",
                        context=(),
                        path=sub_path,
                        instance={},
                    )
                )
            if isinstance(item, CvTermValueObject):
                if item.value and (
                    not item.source and not item.accession and not item.name
                ):
                    if item.unit:
                        valid, error_message = self.cv_helper.check_cv_term(item.unit)
                        if not valid:
                            message = "Unit cv term is not valid."

                            errors.append(
                                jsonschema.ValidationError(
                                    message=message
                                    + f"[{item.unit.source}, {item.unit.accession}, {item.unit.name}] "
                                    f"is not valid. {error_message}",
                                    validator="check-child-cv-term",
                                    context=(),
                                    path=sub_path,
                                    instance={},
                                )
                            )

        return errors

    def run_allow_any_cv_terms_validation(
        self,
        nodes: dict,
        check: CvTermValidation,
        nodes_by_type: dict,
        selected_items: list[Any],
        path: str = None,
    ) -> None | list[jsonschema.ValidationError]:
        if check.node_type not in nodes_by_type:
            return None
        errors = []
        property_name = check.node_property_name
        placeholder_values = set()
        if check.validation.allowed_placeholder_values:
            placeholder_values = {
                (x.source, x.accession)
                for x in check.validation.allowed_placeholder_values
            }

        missing_values = set()
        if check.validation.allowed_missing_cv_terms:
            missing_values = {
                (x.source, x.accession, x.name)
                for x in check.validation.allowed_missing_cv_terms
            }

        other_sources = set()
        if check.validation.allowed_other_sources:
            other_sources = {x for x in check.validation.allowed_other_sources}
        for item in selected_items:
            result = self.check_cv_term(
                nodes,
                item[0],
                item[1],
                property_name,
                placeholder_values,
                missing_values,
                other_sources,
                path=path,
            )
            if result:
                errors.extend(result)
        return errors

    def check_cv_term(
        self,
        nodes: dict,
        idx: int,
        node: IdentifiableMhdModel,
        property_name: None | str = None,
        placeholder_values: None | set[tuple[str, str]] = None,
        missing_values: None | set[tuple[str, str, str]] = None,
        other_sources: None | set[tuple[str, str]] = None,
        path: str = None,
    ) -> list[jsonschema.ValidationError]:
        items, is_list, error = self.get_items(nodes, idx, node, property_name)
        if error:
            return [error]
        if not items:
            return []
        errors = []
        for sub_idx, term in enumerate(items):
            item: CvTermObject = term

            item_key = (item.source, item.accession)
            accession_prefix = (
                item.accession.split(":")[0]
                if ":" in item.accession
                else item.accession
            )
            item_full_key = (item.source, item.accession, item.name)
            if placeholder_values and item_key in placeholder_values:
                continue
            if other_sources and accession_prefix in other_sources:
                continue
            if missing_values and item_full_key in missing_values:
                continue
            if path:
                sub_path = [path, idx, property_name] if property_name else [path, idx]
            else:
                sub_path = [idx, property_name] if property_name else [idx]
            message = f"{node.id_}: {node.type_} node at index {idx} with value "
            if property_name:
                message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its value "
                if is_list:
                    message = f"{node.id_}: '{node.type_}' node at index {idx} has a property '{property_name}'. Its {sub_idx}. index item "
            if is_list:
                sub_path.append(sub_idx)
            valid, error_message = self.cv_helper.check_cv_term(item)
            error_message = error_message if error_message else ""
            if not valid:
                errors.append(
                    jsonschema.ValidationError(
                        message=message
                        + f"[{item.source}, {item.accession}, {item.name}] "
                        f"is not valid. {error_message}",
                        validator="check-cv-term",
                        context=(),
                        path=sub_path,
                        instance={},
                    )
                )
            if isinstance(item, CvTermValueObject):
                if item.value and (
                    not item.source and not item.accession and not item.name
                ):
                    if item.unit:
                        valid, error_message = self.cv_helper.check_cv_term(item.unit)
                        if not valid:
                            message = "Unit cv term is not valid."

                            errors.append(
                                jsonschema.ValidationError(
                                    message=message
                                    + f"[{item.unit.source}, {item.unit.accession}, {item.unit.name}] "
                                    f"is not valid. {error_message}",
                                    validator="check-cv-term",
                                    context=(),
                                    path=sub_path,
                                    instance={},
                                )
                            )

        return errors

    def parse_condition(
        self,
        item: Any,
        nodes: dict,
        source_property: str,
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]] = None,
    ) -> list[Any]:
        vals = [item]
        for term in source_property.split("."):
            new_vals = []
            if term.endswith("_ref"):
                for val in vals:
                    ref = getattr(val, term)
                    if ref:
                        val = nodes.get(ref)
                        new_vals.append(val)
            elif term.endswith("_refs"):
                for val in vals:
                    refs = getattr(val, term)
                    if refs:
                        new_vals.extend([nodes.get(x) for x in refs if x])
            else:
                match = re.match(r"\[(.+)\]", term)
                if match:
                    rel = match.groups()[0]
                    links = relationships_index.get(rel)

                    for val in vals:
                        if val.id_ in links:
                            new_vals.extend(
                                [nodes.get(x) for x in links[item.id_].keys()]
                            )
                else:
                    new_vals.append(getattr(val, term))

            if not new_vals:
                vals = None
                break
            vals = new_vals
        return vals

    def filter_validation(
        self,
        check: CvTermValidation,
        nodes: dict,
        nodes_by_type: dict,
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]] = None,
    ) -> list:
        selected_items = {}
        if check.node_type not in nodes_by_type:
            return []
        current_nodes = nodes_by_type[check.node_type]

        if not check.condition:
            return list(current_nodes.values())
        for condition in check.condition:
            source_node_type = condition.start_node_type
            source_property = condition.expression
            relationship_name = condition.relationship_name
            source_value = condition.expression_value
            relationships = relationships_index.get(relationship_name, {})
            source_nodes = nodes_by_type.get(source_node_type)
            if source_nodes and source_property and source_value:
                for _, item in source_nodes.values():
                    val = None
                    if (
                        not relationship_name.startswith("[embedded]")
                        and item.id_ not in relationships
                    ):
                        continue
                    # if "." in source_property:
                    vals = self.parse_condition(
                        item,
                        nodes,
                        source_property,
                        relationships_index=relationships_index,
                    )
                    for val in vals:
                        if val == source_value:
                            if relationships:
                                for item in relationships[item.id_]:
                                    if item in current_nodes:
                                        current_idx, selected = current_nodes.get(item)
                                        selected_items[current_idx] = (
                                            current_idx,
                                            selected,
                                        )
                            else:
                                path = relationship_name.replace(
                                    "[embedded]", ""
                                ).lstrip(".")
                                vals = self.parse_condition(
                                    item,
                                    nodes,
                                    path,
                                    relationships_index=relationships_index,
                                )
                                for val in vals:
                                    if val.id_ in nodes:
                                        val_node = nodes.get(val.id_)
                                        current_idx, selected = nodes_by_type.get(
                                            val_node.type_, {}
                                        ).get(val_node.id_, (None, None))
                                        if selected:
                                            selected_items[current_idx] = (
                                                current_idx,
                                                selected,
                                            )

            elif source_nodes and source_property:
                for _, item in source_nodes.values():
                    val = getattr(item, source_property)
                    selected = None
                    if val:
                        val_node = nodes.get(val)
                        current_idx, selected = nodes_by_type.get(
                            val_node.type_, {}
                        ).get(val_node.id_)
                    if selected:
                        selected_items[current_idx] = (current_idx, selected)
        return list(selected_items.values())

    def run_allowed_cv_terms_validation(
        self,
        nodes: dict,
        check: CvTermValidation,
        selected_items: list[tuple[int, Any]],
        path: str = None,
    ) -> list[ValidationError]:
        # errors = self.run_default_cv_term_validation(item.validation)
        # if errors:
        #     return errors

        errors = []
        cv_map = {x.accession: x for x in check.validation.cv_terms}
        # items = nodes_by_type[check.node_type]
        property_name = check.node_property_name
        for idx, item in selected_items:
            result = self.check_required_item(
                nodes, idx, item, cv_map, property_name, path=path
            )
            if result:
                errors.extend(result)
        return errors

    def check_optional_item(
        self,
        idx: int,
        item: CvTermObject,
        control_list: dict[str, CvTerm],
    ) -> None | jsonschema.ValidationError:
        if item.accession in control_list:
            reference = control_list[item.accession]
            if reference.name != item.name or reference.source != item.source:
                return jsonschema.ValidationError(
                    message=f"{item.type_} {item.id_}: node at {idx} with value [{item.source}, {item.accession}, {item.name}] "
                    "does not match the reference term. Reference term: "
                    f"[{reference.source}, {reference.accession}, {reference.name}].",
                    validator="check-cv-term",
                    context=(),
                    path=(
                        "nodes",
                        idx,
                    ),
                    instance={},
                )
            return None

    def get_items(
        self, nodes: dict, idx: int, node: NodeValidation, property_name: str
    ) -> tuple[list[CvTerm] | None, bool, jsonschema.ValidationError | None]:
        item: None | CvTerm | list[CvTerm] = None
        if property_name:
            item = None
            if property_name.endswith("_refs"):
                val = getattr(node, property_name)
                if val:
                    item = [nodes.get(x) for x in val if x in nodes]
            elif property_name.endswith("_ref"):
                val = getattr(node, property_name)
                if val:
                    item = nodes.get(val)
            elif not hasattr(node, property_name):
                return (
                    None,
                    False,
                    jsonschema.ValidationError(
                        message=f"{property_name} does not exist at index {idx}",
                        validator="check-propery",
                        context=(),
                        path=("nodes", idx),
                        instance={},
                    ),
                )
            if not item:
                item = getattr(node, property_name)
            if isinstance(item, list):
                if item:
                    if not isinstance(item[0], CvTerm):
                        return (
                            None,
                            True,
                            jsonschema.ValidationError(
                                message=f"{node.id_}: Item in the node at index {idx} is not a cv term",
                                validator="check-cv-term-type",
                                context=(),
                                path=["nodes", idx, property_name, 0],
                                instance={},
                            ),
                        )
                    return item, True, None
                return [], True, None
            else:
                if not item:
                    return [], False, None
                if not isinstance(item, CvTerm):
                    return (
                        None,
                        True,
                        jsonschema.ValidationError(
                            message=f"{node.id_}: Item in the node at index {idx} is not a cv term",
                            validator="check-cv-term-type",
                            context=(),
                            path=["nodes", idx, property_name, 0],
                            instance={},
                        ),
                    )
                return [item], False, None
        else:
            if not isinstance(node, CvTerm):
                return (
                    [],
                    False,
                    jsonschema.ValidationError(
                        message=f"Node at index {idx} is not a cv term",
                        validator="check-cv-term-type",
                        context=(),
                        path=("nodes", idx),
                        instance={},
                    ),
                )
            return [node], False, None

    def check_required_item(
        self,
        nodes: dict,
        idx: int,
        node: IdentifiableMhdModel,
        control_list: dict[str, CvTerm],
        property_name: None | str = None,
        path: str = None,
    ) -> None | list[jsonschema.ValidationError]:
        items, is_list, error = self.get_items(nodes, idx, node, property_name)
        if error:
            return [error]
        if not items:
            return None
        errors = []
        for sub_idx, term in enumerate(items):
            item: CvTermObject = term

            if path:
                sub_path = [path, idx, property_name] if property_name else [path, idx]
            else:
                sub_path = [idx, property_name] if property_name else [idx]
            message = f"{node.id_}: {node.type_} node at index {idx} with value "
            if property_name:
                message = f"{node.id_}: {node.type_} node at index {idx} has a property '{property_name}'. Its value "
                if is_list:
                    message = f"{node.id_}: {node.type_} node at index {idx} has a property '{property_name}'. Its {sub_idx}. index item "
            if is_list:
                sub_path.append(sub_idx)

            if item.accession not in control_list:
                if not item.type_.startswith("x-"):
                    control_list_items = ", ".join(
                        [str(x) for x in control_list.values()]
                    )
                    errors.append(
                        jsonschema.ValidationError(
                            message=message
                            + f"[{item.source}, {item.accession}, {item.name}] "
                            f"is not in control list. Control list items: {control_list_items}",
                            validator="check-cv-term-in-control-list",
                            context=(),
                            path=sub_path,
                            instance={},
                        )
                    )
                continue
            elif item.type_.startswith("x-"):
                errors.append(
                    jsonschema.ValidationError(
                        message=message
                        + f"[{item.source}, {item.accession}, {item.name}] "
                        f"is in common data model control list."
                        f"Rename {item.type_} to the one defined in common data model.",
                        validator="check-cv-term-in-control-list",
                        context=(),
                        path=sub_path,
                        instance={},
                    )
                )
                continue

            reference = control_list[item.accession]
            if reference.name != item.name or reference.source != item.source:
                errors.append(
                    jsonschema.ValidationError(
                        message=f"{item.type_} {item.id_}: node at {idx} with value [{item.source}, {item.accession}, {item.name}] "
                        "does not match the reference term. Reference term: "
                        f"[{reference.source}, {reference.accession}, {reference.name}].",
                        validator="check-cv-term-in-control-list",
                        context=(),
                        path=sub_path,
                        instance={},
                    )
                )
                continue
        return errors

    def check_relationships(
        self,
        item: RelationshipValidation,
        nodes: dict[str, IdentifiableMhdModel] = None,
        nodes_by_type: dict[str, dict[str, tuple[int, Any]]] = None,
        relationships_by_name: dict[str, dict[str, tuple[int, Any]]] = None,
        relationships_index: dict[str, dict[str, dict[str, tuple[int, str]]]] = None,
        path: str = None,
    ) -> None | protocols.Validator:
        relationships = relationships_by_name.get(item.relationship_name, {})
        items = []
        errors = []
        for idx, x in relationships.values():
            target_node = nodes.get(x.target_ref)

            source_node = nodes.get(x.source_ref)
            if item.source == source_node.type_ and item.target == target_node.type_:
                items.append(x)
            elif target_node.type_.startswith("x-") or source_node.type_.startswith(
                "x-"
            ):
                expected_source = (
                    item.source == source_node.type_
                    or item.source.endswith(f"-{item.source}")
                )
                expected_target = (
                    item.target == target_node.type_
                    or item.target.endswith(f"-{item.target}")
                )
                if expected_source and expected_target:
                    items.append(x)
        if len(items) < item.min:
            errors.append(
                jsonschema.ValidationError(
                    message=f"Number of '{item.source} - {item.relationship_name} - {item.target}' "
                    f"relationships is less than expected: {item.min}.",
                    validator="number-of-relationships",
                    context=(),
                    path=("relationships",),
                    instance={},
                )
            )
        if item.max is not None and len(items) > item.max:
            errors.append(
                jsonschema.ValidationError(
                    message=f"Number of '{item.source} - {item.relationship_name} - {item.target}' "
                    "relationship exceeds the allowed limit: {max}.",
                    validator="number-of-relationships",
                    context=(),
                    path=("relationships",),
                    instance={},
                )
            )
        if item.min_for_each_source or item.max_for_each_source:
            source_nodes = relationships_index.get(item.relationship_name, {})
            for node_idx, node in nodes_by_type.get(item.source, {}).values():
                target_count = len(source_nodes.get(node.id_, {}))

                if item.min_for_each_source and target_count < item.min_for_each_source:
                    errors.append(
                        jsonschema.ValidationError(
                            message=f"{node.id_}: The source node at index {node_idx} has less relationship "
                            f"('{item.source} - {item.relationship_name} - {item.target}'). "
                            f"Actual: {target_count}, Minimim : {item.min_for_each_source}.",
                            validator="number-of-relationships",
                            context=(),
                            path=["nodes", node_idx],
                            instance={},
                        )
                    )

                if item.max_for_each_source and target_count > item.max_for_each_source:
                    node_idx, node = nodes_by_type.get(node.type_).get(node.id_)
                    errors.append(
                        jsonschema.ValidationError(
                            message=f"{node.id_}: The source node at index {node_idx} has more relationships "
                            f"('{item.source} - {item.relationship_name} - {item.target}'). "
                            f"Actual: {target_count}, Limit : {item.max_for_each_source}.",
                            validator="number-of-relationships",
                            context=(),
                            path=["nodes", node_idx],
                            instance={},
                        )
                    )

        return errors

    def check_nodes(
        self,
        node_validation: NodeValidation | CvNodeValidation,
        nodes_by_type: dict[str, dict[str, tuple[int, Any]]] = None,
    ) -> None | protocols.Validator:
        min = node_validation.min
        max = node_validation.max
        node_name = node_validation.node_type
        item_count = len(nodes_by_type.get(node_name, {}))
        errors = []
        if item_count < min:
            errors.append(
                jsonschema.ValidationError(
                    message=f"Number of {node_name} nodes is less than the minimum: {min}.",
                    validator="number-of-nodes",
                    context=(),
                    path=("nodes",),
                    instance={},
                )
            )
        if max is not None and item_count > max:
            errors.append(
                jsonschema.ValidationError(
                    message=f"Number of {node_name} nodes exceeds the allowed limit: {max}.",
                    validator="number-of-nodes",
                    context=(),
                    path=("nodes",),
                    instance={},
                )
            )

        if isinstance(node_validation, CvNodeValidation):
            if node_validation.value_required:
                for idx, node in nodes_by_type.get(node_name, {}).values():
                    if not hasattr(node, "value") or not getattr(node, "value"):
                        errors.append(
                            jsonschema.ValidationError(
                                message=f"{node.id_}: {node_name} node at index {idx} must have non empty 'value'.",
                                validator="node-value",
                                context=(),
                                path=("nodes", idx),
                                instance={},
                            )
                        )

        return errors
