"""Generate JSON-LD schema definitions from model classes in a Python module."""

import inspect
from types import ModuleType
from typing import Any

from mhd_model.model.v1_0.dataset.profiles.base import graph_nodes
from mhd_model.shared.model import (
    BaseCvTermModel,
    BaseCvTermValueModel,
    BaseMhdObjectModel,
    BaseReferencedObjectModel,
)

_SCHEMA_BASE_CLASSES = (
    BaseMhdObjectModel,
    BaseCvTermValueModel,
    BaseCvTermModel,
    BaseReferencedObjectModel,
)


def create_jsonld_schema(module: ModuleType) -> dict[str, Any]:
    """Create JSON-LD class/property mappings for eligible classes in *module*.

    A class must inherit from one of the supported base classes and declare its
    own ``iri`` in ``model_config['json_schema_extra']``. Fields without an
    ``iri`` in their ``json_schema_extra`` are omitted.
    """
    definitions: dict[str, Any] = {}
    for class_name, model_class in inspect.getmembers(module, inspect.isclass):
        if model_class.__module__ != module.__name__:
            continue
        if model_class in _SCHEMA_BASE_CLASSES or not issubclass(
            model_class, _SCHEMA_BASE_CLASSES
        ):
            continue
        if inspect.isabstract(model_class):
            continue

        model_extra = model_class.model_config.get("json_schema_extra", {}) or {}
        model_iri = model_extra.get("iri")
        if not model_iri:
            continue

        properties: dict[str, str] = {}
        for field_name, field_info in model_class.model_fields.items():
            field_extra = field_info.json_schema_extra or {}
            field_iri = field_extra.get("iri")
            if field_iri:
                properties[field_name] = field_iri

        definitions[class_name] = {
            "@id": model_iri,
            "@type": "rdfs:Class",
            "properties": properties,
        }

    return {
        "@context": {"rdfs": "http://www.w3.org/2000/01/rdf-schema#"},
        "classes": definitions,
    }


def create_graph_nodes_jsonld_schema() -> dict[str, Any]:
    """Create a JSON-LD schema from the v1.0 graph nodes module."""
    return create_jsonld_schema(graph_nodes)
