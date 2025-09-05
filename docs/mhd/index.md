# MHD Common Data Model v0.1

*MHD Common Data Model* is a connected graph of nodes and edges. MHD Domain Objects and MHD Cv Term Objects define the graph nodes and MHD Relationship Object (including both external and embedded relationships) define the edges. This graph-based structure allows for flexible, modular, structured, and consistent representation of metabolomics datasets.

## MHD Common Data Model Nodes

---
**MHD Domain Objects**

Each of *MHD Domain Objects* corresponds to a concept commonly used in metabolomics dataset metadata files.


List of MHD Domain Objects:

- [Study](mhd-ms-nodes.md#study)
- [Publication](mhd-ms-nodes.md#publication)
- [Person](mhd-ms-nodes.md#person)
- [Organization](mhd-ms-nodes.md#organization)
- [Project](mhd-ms-nodes.md#project)
- [Factor Definition](mhd-ms-nodes.md#factor-definition)
- [Protocol](mhd-ms-nodes.md#protocol)
- [Parameter Definition](mhd-ms-nodes.md#parameter-definition)
- [Metadata File](mhd-ms-nodes.md#metadata-file)
- [Raw Data File](mhd-ms-nodes.md#raw-data-file)
- [Derived Data File](mhd-ms-nodes.md#derived-data-file)
- [Result File](mhd-ms-nodes.md#result-file)
- [Supplementary File](mhd-ms-nodes.md#supplementary-file)
- [Metabolite](mhd-ms-nodes.md#metabolite)
- [Assay](mhd-ms-nodes.md#assay)
- [Subject](mhd-ms-nodes.md#subject)
- [Specimen](mhd-ms-nodes.md#specimen)
- [Sample](mhd-ms-nodes.md#sample)
- [Characteristic Definition](mhd-ms-nodes.md#characteristic-definition)
- [Sample Run](mhd-ms-nodes.md#sample-run)
- [Sample Run Configuration](mhd-ms-nodes.md#sample-run-configuration)

The following properties are common for all  *MHD Domain Objects*.

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|required|<code>*str*<code>|The id property uniquely identifies the object. All *MHD Domain Objects* have <u>*unique identifiers*</u> even if their values are exactly same.|
|**type**|required|<code>*str*<code>|The type MUST be lower case and '-' seperated value of node name. e.g. raw-data-file for Raw Data File|
|**created_by_ref**|optional|<code>*str*<code>|The id of the data provider.|
|**tags**|optional|<code>*list of KeyValue*<code>|Key and values. key and values may be CV Term|
|**descriptors**|optional|<code>*list of CvTerm*<code>|Descriptors for the object|
|**external_references**|optional|<code>*list of KeyValue*<code>|List of external references that describes the resource represented by the node. Key MUST be a URI type (FTP, URL, etc.)|
|**url_list**|optional|<code>*list of AnyUrl*<code>|List of URI addresses to access the resource represented by the node |

---

**MHD Cv Term Objects**

*MHD Common Data Model* defines a set of data types (MHD Cv Term Objects) presented as CV Term.

List of MHD Cv Term Objects: <code>Characteristic Type, Characteristic Value, Data Provider, Factor Type, Factor Value, Parameter Type, Protocol Type, Parameter Value, Uri Type</code>

The following properties are common for all  *MHD Cv Term Objects*.

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|required|<code>*str*<code>|The id property uniquely identifies the object. All *MHD Cv Term Objects* have <u>*same identifiers*</u> if their values are exactly same.|
|**type**|required|<code>*str*<code>|The type MUST be lower case and '-' seperated value of node name. e.g. parameter-value for Paramter Value|

---

## MHD Common Data Model Relationships

A relationship is a link between MHD Domain Objects or MHD Cv Term Objects that describes the way in which the objects are related. Relationships can be represented using an MHD Relationship Object or a property (embedded relationship)  in a node. Property names that used as embedded relationship in a node end with <code>_ref</code> or <code>_refs</code> (for multiple), and their values are id's of target nodes.
 
*MHD Relationship Object* has the following properties.


|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|required|<code>*MhdRelationshipObjectId*<code>|The id property uniquely identifies the object.|
|**type**|required|<code>*str*<code>|The type MUST be 'relationship'|
|**created_by_ref**|optional|<code>*str*<code>|The id of the data provider.|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key and values. key and values may be CV Term|
|**external_references**|optional|<code>*list[KeyValue]*<code>|List of external references that describes the resource represented by the relationship. Key MUST be a URI type (FTP, URL, etc.)|
|**url_list**|optional|<code>*list[KeyValue]*<code>|List of URI addresses to access the resource represented by the relationship |
|**source_ref**|required|<code>*CvTermValueObjectId or CvTermObjectId or MhdObjectId*<code>|The id of source node|
|**relationship_name**|required|<code>*str*<code>|Relationship name|
|**target_ref**|required|<code>*CvTermValueObjectId or CvTermObjectId or MhdObjectId*<code>|The id of target node|
|**source_role**|optional|<code>*str*<code>|Role name of source node|
|**target_role**|optional|<code>*str*<code>|Role name of target node|


---


## Node and Relationship Property Types

### Primitive Types

Primitive data types are <code>string (str), number (int or float), boolean (bool), and null (None)</code>.

The following string formatted JSON schema data types are also supported:

* date: ISO 8601 calendar date. e.g. 2025-05-18
* time: ISO 8601 time without timezone. e.g. 14:30:00
* date-time: ISO 8601 full timestamp. e.g. 2025-05-18T14:30:00Z
* email: RFC 5322 email address. e.g.  help@metabolomicshub.org
* uri: Full URI. e.g. https://metabolomicshub.org/docs

### Node and Relationship Ids

**MhdObjectId**

The id property of *MHD Domain Objects*  MUST have three parts. These parts are merged with <code>"--"</code> seperator to create id.

1. <code>mhd</code> constant
2. <code>[type name, e.g. study, protocol, etc.]</code>
3. <code>UUID4 value</code>


```python
# Pattern for id property of MHD Domain Objects
^mhd--[-a-zA-Z0-9]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$

# Example MHD Domain Object id
mhd--study--51be6a20-0e5a-4c2d-9177-f261193dc30c
```

**CvTermObjectId**


The id property of *MHD Cv Term Objects*  MUST have three parts. These parts are merged with <code>"--"</code> seperator to create id.

1. <code>cv</code> constant
2. <code>[type name, e.g. technology-type, factor-definition, etc.]</code>
3. <code>UUID5 value</code> of <code>source, accession, and name</code> fields' values [namespace is MHD namespace with a constant <code>efb4f8e4-d08b-4979-916e-600c4985e7f2</code>]

```python
# Pattern for id property of MHD Cv Term Objects
^cv--[-a-zA-Z0-9]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$

# Example MHD Cv Term Object id
cv--factor-definition--66be6a20-0e5a-4c2d-9177-f261193dc30c
```

**CvTermValueObjectId**

The id property of *MHD Cv Term Objects* with value MUST have three parts. These parts are merged with <code>"--"</code> seperator to create id.

1. <code>cv-value</code> constant
2. <code>[type name, e.g. data-provider, metabolite-definition, etc.]</code>
3. <code>UUID5 value</code> of <code>source, accession, name and value</code> fields' values [namespace is MHD namespace with a constant <code>efb4f8e4-d08b-4979-916e-600c4985e7f2</code>]

```python
# Pattern for id property of MHD Cv Term Value Objects
^cv-value--[-a-zA-Z0-9]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$

# Example MHD Cv Term Value Object id
cv-value--data-provider--88be6a20-0e5a-4c2d-9177-f261193dc30c
```

**MhdRelationshipObjectId**

The id property of *MHD Relationship Object*  MUST have three parts. These parts are merged with <code>"--"</code> seperator to create id.

1. <code>rel</code> constant
2. <code>relationship</code> constant
3. <code>UUID5 value</code> of <code>source_ref, relationship_name, target_ref</code> fields' values [namespace is MHD namespace with a constant <code>efb4f8e4-d08b-4979-916e-600c4985e7f2</code>]

```python
# Pattern for id property of MHD Relationship Object
^rel--[-a-zA-Z0-9]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$

# Example MHD Relationship Object id
rel--relationship--99be6a20-0e5a-4c2d-9177-f261193dc30c
```

### CvTerm

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**source**|required|str|Source of CV term. e.g., NCIT, EFO, etc.|
|**accession**|required|str|Accession number CV Term in CURIES format. e.g., EFO:0001742 |
|**name**|required|str|Label of CV Term. e.g., publication status |

### QuantitativeValue

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**value**|required|str or int or float|Value associated with CV Term. e.g., 2 |
|**unit**|optional|CV Term|Unit of value. [OBI, OBI:0000984, dose]|

### CvTermValue


|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**source**|required|str|Source of CV term. e.g., NCIT, EFO, etc.|
|**accession**|required|str|Accession number CV Term in CURIES format. e.g., NCIT:C189151 |
|**name**|required|str|Label of CV Term. e.g., Study Data Repository |
|**value**|required|str|Value associated with CV Term. e.g., MetaboLights |
|**unit**|optional|CV Term|Unit of value.|


### KeyValue

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**key**|required|<code>*str or CvTermObjectId or MhdObjectId or CvTerm*<code>|Key of the object. It can be a id of a node, str or CV Term|
|**value**|required|<code>*CvTermValueObjectId or CvTermObjectId or MhdObjectId or str or CvTerm or CvTermValue or QuantitativeValue*<code>|Value of the object. It can be a id of a node, str, CV Term or Cv Term Value|
