# MetabolomicsHub Common Data Model Nodes - MHD Legacy Profile

Profile Schema: <a href="https://metabolomicshub.github.io/mhd-model/schemas/v0_1/common-data-model-v0.1.legacy-profile.json" target="_blank">https://metabolomicshub.github.io/mhd-model/schemas/v0_1/common-data-model-v0.1.legacy-profile.json</a> 

## Required Nodes & Relationships 

 **Required MHD Nodes**

<code>Characteristic Definition, Metadata File, Person, Study</code>

 **Required MHD CV Terms**

<code>Characteristic Type, Characteristic Value, Data Provider</code>

The following graph shows only required nodes and required relationships. Relationships that start with 'embedded - ' show required node property.

``` mermaid
graph LR
  Characteristic_Definition[Characteristic Definition] ==>|embedded - characteristic_type_ref| Characteristic_Type[Characteristic Type];
  Study[Study] ==>|embedded - created_by_ref| Data_Provider[Data Provider];
  Characteristic_Definition[Characteristic Definition] ==>|has-type| Characteristic_Type[Characteristic Type];
  Characteristic_Definition[Characteristic Definition] ==>|used-in| Study[Study];
  Metadata_File[Metadata File] ==>|describes| Study[Study];
  Study[Study] ==>|provided-by| Data_Provider[Data Provider];
  Study[Study] ==>|has-characteristic-definition| Characteristic_Definition[Characteristic Definition];
  Study[Study] ==>|has-metadata-file| Metadata_File[Metadata File];
  Study[Study] ==>|submitted-by| Person[Person];
  Characteristic_Type[Characteristic Type] ==>|type-of| Characteristic_Definition[Characteristic Definition];
  Characteristic_Value[Characteristic Value] ==>|instance-of| Characteristic_Definition[Characteristic Definition];
  Data_Provider[Data Provider] ==>|provides| Study[Study];
```

**Required Relationships**

|Source Node|Relationship|Target Node|Min|Max|
|-----------|------------|-----------|---|---|
|Characteristic Definition|[embedded] - characteristic_type_ref|Characteristic Type|1|1|
|Characteristic Definition|has-type|Characteristic Type|1|1|
|Characteristic Definition|used-in|Study|1|N (unbounded)|
|Characteristic Type|type-of|Characteristic Definition|1|N (unbounded)|
|Characteristic Value|instance-of|Characteristic Definition|1|N (unbounded)|
|Data Provider|provides|Study|1|1|
|Metadata File|describes|Study|1|1|
|Study|[embedded] - created_by_ref|Data Provider|1|1|
|Study|has-characteristic-definition|Characteristic Definition|1|N (unbounded)|
|Study|has-metadata-file|Metadata File|1|N (unbounded)|
|Study|provided-by|Data Provider|1|1|
|Study|submitted-by|Person|1|N (unbounded)|

**Required Node Properties**

|Source Node|Property Name|
|-----------|------------|
|characteristic-definition|characteristic_type_ref|
|characteristic-definition|name|
|characteristic-type|name|
|data-provider|value|
|metadata-file|name|
|metadata-file|url_list|
|person|full_name|
|study|created_by_ref|
|study|dataset_url_list|
|study|description|
|study|public_release_date|
|study|repository_identifier|
|study|submission_date|
|study|title|

**Additional Requirements**

The following nodes are required with the specified value.

|Source Node|Minimum Node Count|Property / Relationship|Value|
|-----------|-----------|------------|------------|
|characteristic-definition|1|characteristic_type_ref|[NCIT, NCIT:C14250, organism]|

## MHD Domain Objects

### Assay

Assay node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|Its value MUST be <code>**assay**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**repository_identifier**|**required**|<code>*str*<code>|An assay identifier that uniquely identifies the assay in repository<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the assay. It SHOULD be unique in a study<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**metadata_file_ref**|optional|<code>*MhdObjectId*<code>|Target node type: <code>**metadata-file**</code><br>Validation Rule:<br> <code>Target node type: <code>**metadata-file**</code></code>|
|**technology_type_ref**|optional|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [OBI, OBI:0000470, mass spectrometry assay],<br>* [OBI, OBI:0000623, NMR spectroscopy assay]</code>|
|**assay_type_ref**|optional|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [OBI, OBI:0003097, liquid chromatography mass spectrometry assay],<br>* [OBI, OBI:0003110, gas chromatography mass spectrometry assay],<br>* [OBI, OBI:0000470, mass spectrometry assay],<br>* [OBI, OBI:0000623, NMR spectroscopy assay]</code>|
|**measurement_type_ref**|optional|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [MSIO, MSIO:0000100, targeted metabolite profiling],<br>* [MSIO, MSIO:0000101, untargeted metabolite profiling]</code>|
|**omics_type_ref**|optional|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [EDAM, EDAM:3172, Metabolomics],<br>* [EDAM, EDAM:0153, Lipidomics],<br>* [EDAM, EDAM:3955, Fluxomics]</code>|
|**protocol_refs**|optional|<code>*list[MhdObjectId]*<code>|The id properties of protocols used in assay. A protocol is a defined and standardized procedure followed to collect, prepare, or analyze biological samples<br>Target node type: <code>**protocol**</code><br>Validation Rule:<br> <code>Target node type: <code>**protocol**</code></code>|
|**sample_run_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**sample-run**</code><br>Validation Rule:<br> <code>Target node type: <code>**sample-run**</code></code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|described-as|describes|descriptor|0|N|A link to a descriptor that describes the assay.|
|assay|follows|used-in|protocol|0|N|A link to a protocol conducted in assay.|
|assay|part-of|has-assay|study|1|1|A link to a study that the assay was conducted as part of it to generate data addressing study objectives|


**Embedded Relationships**: <code>descriptor, metadata-file, protocol, sample-run</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|assay|0|N||
|protocol|used-in|follows|assay|0|N||
|study|has-assay|part-of|assay|0|N||

### Characteristic Definition

Characteristic Definition node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**characteristic-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**characteristic_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**characteristic-type**</code><br>Validation Rules:<br> <code>Target node type: <code>**characteristic-type**</code><br>Allowed CV Terms:<br>* [NCIT, NCIT:C14250, organism],<br>* [NCIT, NCIT:C103199, organism part],<br>* [EFO, EFO:0000408, disease],<br>* [EFO, EFO:0000324, cell type]</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-definition|has-instance|instance-of|characteristic-value|0|N|Target Validation Rule:<br><code>-----<br>**Conditional - (Organism)**<br>[Source characteristic_type_ref.accession = NCIT:C14250]<br>Allow any valid CV Term<br>Exceptions:<br>Allowed Placeholder Values: source='' accession=''<br>Allowed Other Sources: wikidata, ILX</code><br>-----|
|characteristic-definition|has-type|type-of|characteristic-type|1|1||
|characteristic-definition|used-in|has-characteristic-definition|study|1|N||


**Embedded Relationships**: <code>characteristic-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-type|type-of|has-type|characteristic-definition|1|N||
|characteristic-value|instance-of|has-instance|characteristic-definition|1|N||
|study|has-characteristic-definition|used-in|characteristic-definition|1|N|**Required min count in the dataset: 1.**|

### Derived Data File

Derived Data File node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**derived-data-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|**required**|<code>*list[AnyUrl]*<code>|URL list related to the object<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_refs**|optional|<code>*list[CvTermObjectId]*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.). List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|**required**|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|derived-data-file|created-in|has-derived-data-file|study|1|1||
|derived-data-file|described-as|describes|descriptor|0|N|A link to a descriptor that describes the derived data file.|
|derived-data-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|derived-data-file|0|N||
|metadata-file|references|referenced-in|derived-data-file|0|N||
|study|has-derived-data-file|created-in|derived-data-file|0|N||

### Factor Definition

Factor Definition node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**factor-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**factor_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target node type: <code>**factor-type**</code><br>Validation Rule:<br> <code>Target node type: <code>**factor-type**</code></code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-definition|has-instance|instance-of|factor-value|0|N||
|factor-definition|has-type|type-of|factor-type|1|1||
|factor-definition|used-in|has-factor-definition|study|1|N||


**Embedded Relationships**: <code>factor-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-type|type-of|has-type|factor-definition|1|N||
|factor-value|instance-of|has-instance|factor-definition|1|N||
|study|has-factor-definition|used-in|factor-definition|0|N||

### Metabolite

Metabolite node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**metabolite**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|metabolite|described-as|describes|descriptor|0|N||
|metabolite|identified-as|reported-identifier-of|metabolite-identifier|0|N|Target Validation Rule:<br><code>-----<br>Allowed Parent CV Terms:<br>* [CHEMINF, CHEMINF:000464, chemical database identifier]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code><br>-----|
|metabolite|reported-in|reports|study|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|metabolite|0|N||
|metabolite-identifier|reported-identifier-of|identified-as|metabolite|1|N||
|study|reports|reported-in|metabolite|0|N||

### Metadata File

Metadata File node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**metadata-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|**required**|<code>*list[AnyUrl]*<code>|URL list related to the object<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_refs**|optional|<code>*list[CvTermObjectId]*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.). List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|optional|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|metadata-file|described-as|describes|descriptor|0|N||
|metadata-file|describes|has-metadata-file|study|1|1|**Required min count in the dataset: 1.**|
|metadata-file|referenced-in|references|metadata-file|0|N||
|metadata-file|references|referenced-in|derived-data-file|0|N||
|metadata-file|references|referenced-in|raw-data-file|0|N||
|metadata-file|references|referenced-in|result-file|0|N||
|metadata-file|references|referenced-in|supplementary-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|derived-data-file|referenced-in|references|metadata-file|0|N||
|descriptor|describes|described-as|metadata-file|0|N||
|metadata-file|referenced-in|references|metadata-file|0|N||
|raw-data-file|referenced-in|references|metadata-file|0|N||
|result-file|referenced-in|references|metadata-file|0|N||
|study|has-metadata-file|describes|metadata-file|1|N||
|supplementary-file|referenced-in|references|metadata-file|0|N||

### Organization

Organization node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**organization**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**repository_identifier**|optional|<code>*str*<code>||
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**department**|optional|<code>*str*<code>||
|**unit**|optional|<code>*str*<code>||
|**address**|optional|<code>*str*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|organization|affiliates|affiliated-with|person|0|N||
|organization|coordinates|coordinated-by|project|0|N||
|organization|described-as|describes|descriptor|0|N||
|organization|funds|funded-by|project|0|N||
|organization|funds|funded-by|study|0|N||
|organization|manages|managed-by|project|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|organization|0|N||
|person|affiliated-with|affiliates|organization|0|N||
|project|coordinated-by|coordinates|organization|0|N||
|project|funded-by|funds|organization|0|N||
|project|managed-by|manages|organization|0|N||
|study|funded-by|funds|organization|0|N||

### Parameter Definition

Parameter Definition node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**parameter-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**parameter_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target node type: <code>**parameter-type**</code><br>Validation Rule:<br> <code>Target node type: <code>**parameter-type**</code></code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-definition|has-instance|instance-of|parameter-value|0|N||
|parameter-definition|has-type|type-of|parameter-type|1|1||
|parameter-definition|used-in|has-parameter-definition|protocol|1|N||


**Embedded Relationships**: <code>parameter-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-type|type-of|has-type|parameter-definition|1|N||
|parameter-value|instance-of|has-instance|parameter-definition|1|N||
|protocol|has-parameter-definition|used-in|parameter-definition|0|N||

### Person

Person node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The value of this property MUST be 'person'<br>Its value MUST be <code>**person**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**full_name**|**required**|<code>*str*<code>|Full name of person<br>Minimum length: <code>5</code><br>Validation Rule:<br> <code>Min Length: 5, Required</code>|
|**orcid**|optional|<code>*str*<code>|ORCID identifier of person<br><br>Example: <br><code>"1234-0001-8473-1713"<br>"1234-0001-8473-171X"</code>|
|**email_list**|optional|<code>*list[EmailStr]*<code>|Email addresses of person|
|**phone_list**|optional|<code>*list[str]*<code>|Phone number of person (with international country code)<br><br>Example: <br><code>"['+449340917271', '00449340917271']"</code>|
|**address_list**|optional|<code>*list[str]*<code>|Addresses of person|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|person|affiliated-with|affiliates|organization|0|N||
|person|author-of|has-author|publication|0|N||
|person|contributes|has-contributor|project|0|N||
|person|contributes|has-contributor|study|0|N||
|person|described-as|describes|descriptor|0|N||
|person|principal-investigator-of|has-principal-investigator|study|0|N||
|person|submits|submitted-by|study|0|N|**Required min count in the dataset: 1.**|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|person|0|N||
|organization|affiliates|affiliated-with|person|0|N||
|project|has-contributor|contributes|person|0|N||
|publication|has-author|author-of|person|0|N||
|study|has-contributor|contributes|person|0|N||
|study|has-principal-investigator|principal-investigator-of|person|0|N||
|study|submitted-by|submits|person|1|N|**Required min count in the dataset: 1.**|

### Project

Project node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**project**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**title**|**required**|<code>*str*<code>|Minimum length: <code>5</code><br>Validation Rule:<br> <code>Min Length: 5, Required</code>|
|**description**|optional|<code>*str*<code>||
|**grant_identifier_list**|optional|<code>*list[Annotated]*<code>||
|**doi**|optional|<code>*str*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|project|coordinated-by|coordinates|organization|0|N||
|project|described-as|describes|descriptor|0|N||
|project|funded-by|funds|organization|0|N||
|project|has-contributor|contributes|person|0|N||
|project|has-publication|describes|publication|0|N||
|project|has-study|part-of|study|0|N||
|project|managed-by|manages|organization|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|project|0|N||
|organization|coordinates|coordinated-by|project|0|N||
|organization|funds|funded-by|project|0|N||
|organization|manages|managed-by|project|0|N||
|person|contributes|has-contributor|project|0|N||
|publication|describes|has-publication|project|0|N||
|study|part-of|has-study|project|0|N||

### Protocol

Protocol node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**protocol**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>||
|**protocol_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**protocol-type**</code><br>Validation Rules:<br> <code>Target node type: <code>**protocol-type**</code><br>Allowed CV Terms:<br>* [EFO, EFO:0005518, sample collection protocol],<br>* [MS, MS:1000831, sample preparation],<br>* [CHMO, CHMO:0000470, mass spectrometry],<br>* [OBI, OBI:0200000, data transform],<br>* [MI, MI:2131, metabolite identification],<br>* [CHMO, CHMO:0001000, chromatography],<br>* [EFO, EFO:0003969, treatment protocol],<br>* [CHMO, CHMO:0001024, capillary electrophoresis],<br>* [MS, MS:1000058, flow injection analysis]<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**description**|optional|<code>*str*<code>|Validation Rule:<br> <code></code>|
|**parameter_definition_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**parameter-definition**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|protocol|described-as|describes|descriptor|0|N||
|protocol|has-parameter-definition|used-in|parameter-definition|0|N||
|protocol|has-type|type-of|protocol-type|1|1||
|protocol|used-in|follows|assay|0|N||
|protocol|used-in|has-protocol|study|1|N||


**Embedded Relationships**: <code>protocol-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|follows|used-in|protocol|0|N|A link to a protocol conducted in assay.|
|descriptor|describes|described-as|protocol|0|N||
|parameter-definition|used-in|has-parameter-definition|protocol|1|N||
|protocol-type|type-of|has-type|protocol|1|N||
|study|has-protocol|used-in|protocol|0|N||

### Publication

Publication node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**publication**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**title**|**required**|<code>*str*<code>||
|**doi**|**required**|<code>*str*<code>||
|**pubmed_id**|optional|<code>*str*<code>||
|**author_list**|optional|<code>*list[Annotated]*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|publication|described-as|describes|descriptor|0|N||
|publication|describes|has-publication|project|0|N||
|publication|describes|has-publication|study|0|1||
|publication|has-author|author-of|person|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|publication|0|N||
|person|author-of|has-author|publication|0|N||
|project|has-publication|describes|publication|0|N||
|study|has-publication|describes|publication|0|N||

### Raw Data File

Raw Data File node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**raw-data-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|**required**|<code>*list[AnyUrl]*<code>|URL list related to the object<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_refs**|optional|<code>*list[CvTermObjectId]*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.). List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|**required**|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|raw-data-file|created-in|has-raw-data-file|study|1|N||
|raw-data-file|described-as|describes|descriptor|0|N||
|raw-data-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|raw-data-file|0|N||
|metadata-file|references|referenced-in|raw-data-file|0|N||
|study|has-raw-data-file|created-in|raw-data-file|0|N||

### Result File

Result File node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**result-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|**required**|<code>*list[AnyUrl]*<code>|URL list related to the object<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_refs**|optional|<code>*list[CvTermObjectId]*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.). List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|**required**|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|result-file|created-in|has-result-file|study|1|N||
|result-file|described-as|describes|descriptor|0|N||
|result-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|result-file|0|N||
|metadata-file|references|referenced-in|result-file|0|N||
|study|has-result-file|created-in|result-file|0|N||

### Sample

Sample node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**repository_identifier**|**required**|<code>*str*<code>||
|**additional_identifier_list**|optional|<code>*list[CvTermValue]*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|sample|derived-from|source-of|subject|1|N||
|sample|derived-from|source-of|specimen|0|N||
|sample|described-as|describes|descriptor|0|N||
|sample|has-characteristic-value|value-of|characteristic-value|0|N||
|sample|has-factor-value|value-of|factor-value|0|N||
|sample|used-in|has-sample|study|1|1||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|value-of|has-characteristic-value|sample|0|N||
|descriptor|describes|described-as|sample|0|N||
|factor-value|value-of|has-factor-value|sample|1|N||
|specimen|source-of|derived-from|sample|1|N||
|study|has-sample|used-in|sample|0|N||
|subject|source-of|derived-from|sample|0|N||

### Sample Run

Sample Run node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample-run**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|optional|<code>*str*<code>||
|**sample_ref**|optional|<code>*MhdObjectId*<code>|Target node type: <code>**sample**</code><br>Validation Rule:<br> <code>Target node type: <code>**sample**</code></code>|
|**sample_run_configuration_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**sample-run-configuration**</code>|
|**raw_data_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**raw-data-file**</code><br>Validation Rule:<br> <code>Target node type: <code>**raw-data-file**</code></code>|
|**derived_data_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**derived-data-file**</code>|
|**result_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**result-file**</code>|
|**supplementary_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**supplementary-file**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|sample-run|described-as|describes|descriptor|0|N||


**Embedded Relationships**: <code>raw-data-file, sample</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|sample-run|0|N||

### Sample Run Configuration

Sample Run Configuration node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample-run-configuration**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**protocol_ref**|**required**|<code>*MhdObjectId*<code>|Target node type: <code>**protocol**</code><br>Validation Rule:<br> <code>Target node type: <code>**protocol**</code></code>|
|**parameter_value_refs**|optional|<code>*list[MhdObjectId or CvTermObjectId or CvTermValueObjectId]*<code>|Target node type: <code>**parameter-value**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|sample-run-configuration|described-as|describes|descriptor|0|N||


**Embedded Relationships**: <code>protocol</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|sample-run-configuration|0|N||

### Specimen

Specimen node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**specimen**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**repository_identifier**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**additional_identifier_list**|optional|<code>*list[CvTermValue]*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|specimen|derived-from|source-of|subject|1|N||
|specimen|described-as|describes|descriptor|0|N||
|specimen|has-characteristic-value|value-of|characteristic-value|0|N||
|specimen|source-of|derived-from|sample|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|value-of|has-characteristic-value|specimen|0|N||
|descriptor|keyword-of|has-repository-keyword|specimen|0|N||
|factor-value|value-of|has-factor-value|specimen|1|N||
|sample|derived-from|source-of|specimen|0|N||
|subject|source-of|derived-from|specimen|0|N||

### Study

Study node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: 1 </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**study**</code>|
|**created_by_ref**|**required**|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rules:<br> <code>Target node type: <code>**data-provider**</code><br>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**mhd_identifier**|optional|<code>*str*<code>||
|**repository_identifier**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**additional_identifier_list**|optional|<code>*list[CvTermValue]*<code>||
|**title**|**required**|<code>*str*<code>|Minimum length: <code>5</code><br>Validation Rule:<br> <code>Min Length: 5, Required</code>|
|**description**|**required**|<code>*str*<code>|Minimum length: <code>5</code><br>Validation Rule:<br> <code>Min Length: 5, Required</code>|
|**submission_date**|**required**|<code>*datetime*<code>||
|**public_release_date**|**required**|<code>*datetime*<code>||
|**license**|optional|<code>*HttpUrl*<code>|<br>Example: <br><code>"https://creativecommons.org/publicdomain/zero/1.0/"</code>|
|**grant_identifier_list**|optional|<code>*list[Annotated]*<code>||
|**dataset_url_list**|**required**|<code>*list[AnyUrl]*<code>||
|**related_dataset_list**|optional|<code>*list[KeyValue]*<code>||
|**protocol_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**protocol**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|study|described-as|describes|descriptor|0|N||
|study|funded-by|funds|organization|0|N||
|study|has-assay|part-of|assay|0|N||
|study|has-characteristic-definition|used-in|characteristic-definition|1|N|**Required min count in the dataset: 1.**|
|study|has-contributor|contributes|person|0|N||
|study|has-derived-data-file|created-in|derived-data-file|0|N||
|study|has-factor-definition|used-in|factor-definition|0|N||
|study|has-metadata-file|describes|metadata-file|1|N||
|study|has-principal-investigator|principal-investigator-of|person|0|N||
|study|has-protocol|used-in|protocol|0|N||
|study|has-publication|describes|publication|0|N||
|study|has-raw-data-file|created-in|raw-data-file|0|N||
|study|has-repository-keyword|keyword-of|descriptor|0|N||
|study|has-result-file|created-in|result-file|0|N||
|study|has-sample|used-in|sample|0|N||
|study|has-submitter-keyword|keyword-of|descriptor|0|N||
|study|has-supplementary-file|created-in|supplementary-file|0|N||
|study|part-of|has-study|project|0|N||
|study|provided-by|provides|data-provider|1|1||
|study|reports|reported-in|metabolite|0|N||
|study|submitted-by|submits|person|1|N|**Required min count in the dataset: 1.**|


**Embedded Relationships**: <code>data-provider</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|part-of|has-assay|study|1|1|A link to a study that the assay was conducted as part of it to generate data addressing study objectives|
|characteristic-definition|used-in|has-characteristic-definition|study|1|N||
|data-provider|provides|provided-by|study|1|1||
|derived-data-file|created-in|has-derived-data-file|study|1|1||
|descriptor|describes|described-as|study|0|N||
|descriptor|keyword-of|has-repository-keyword|study|0|N||
|factor-definition|used-in|has-factor-definition|study|1|N||
|metabolite|reported-in|reports|study|1|N||
|metadata-file|describes|has-metadata-file|study|1|1|**Required min count in the dataset: 1.**|
|organization|funds|funded-by|study|0|N||
|person|contributes|has-contributor|study|0|N||
|person|principal-investigator-of|has-principal-investigator|study|0|N||
|person|submits|submitted-by|study|0|N|**Required min count in the dataset: 1.**|
|project|has-study|part-of|study|0|N||
|protocol|used-in|has-protocol|study|1|N||
|publication|describes|has-publication|study|0|1||
|raw-data-file|created-in|has-raw-data-file|study|1|N||
|result-file|created-in|has-result-file|study|1|N||
|sample|used-in|has-sample|study|1|1||
|supplementary-file|created-in|has-supplementary-file|study|1|N||

### Subject

Subject node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**subject**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|optional|<code>*list[AnyUrl]*<code>|URL list related to the object|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**subject_type_ref**|optional|<code>*CvTermObjectId*<code>||
|**repository_identifier**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**additional_identifier_list**|optional|<code>*list[CvTermValue]*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|subject|described-as|describes|descriptor|0|N||
|subject|has-characteristic-value|value-of|characteristic-value|0|N||
|subject|has-factor-value|value-of|factor-value|0|N||
|subject|source-of|derived-from|sample|0|N||
|subject|source-of|derived-from|specimen|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|value-of|has-characteristic-value|subject|0|N||
|descriptor|describes|described-as|subject|0|N||
|factor-value|value-of|has-factor-value|subject|0|N||
|sample|derived-from|source-of|subject|1|N||
|specimen|derived-from|source-of|subject|1|N||

### Supplementary File

Supplementary File node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**supplementary-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata, ILX</code>|
|**tag_list**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**external_reference_list**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**url_list**|**required**|<code>*list[AnyUrl]*<code>|URL list related to the object<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_refs**|optional|<code>*list[CvTermObjectId]*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.). List item order shows order of compressions. e.g. [tar format, gzip format] for tar.gz<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:format_1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|optional|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|supplementary-file|created-in|has-supplementary-file|study|1|N||
|supplementary-file|described-as|describes|descriptor|0|N||
|supplementary-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|supplementary-file|0|N||
|metadata-file|references|referenced-in|supplementary-file|0|N||
|study|has-supplementary-file|created-in|supplementary-file|0|N||

## MHD CV Term Objects

### Characteristic Type

Characteristic Type node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**characteristic-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|**required**|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-type|type-of|has-type|characteristic-definition|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-definition|has-type|type-of|characteristic-type|1|1||

### Characteristic Value

Characteristic Value node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermValueObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term Value object<br>Its value MUST be <code>**characteristic-value**</code>|
|**value**|optional|<code>*str or int or float or Decimal*<code>||
|**unit**|optional|<code>*UnitCvTerm*<code>||
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|instance-of|has-instance|characteristic-definition|1|N||
|characteristic-value|value-of|has-characteristic-value|subject|0|N||
|characteristic-value|value-of|has-characteristic-value|specimen|0|N||
|characteristic-value|value-of|has-characteristic-value|sample|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-definition|has-instance|instance-of|characteristic-value|0|N||
|sample|has-characteristic-value|value-of|characteristic-value|0|N||
|specimen|has-characteristic-value|value-of|characteristic-value|0|N||
|subject|has-characteristic-value|value-of|characteristic-value|0|N||

### Data Provider

Data Provider node is **required in the MHD Legacy Profile.** <code>Minimum: 1, Maximum: 1 </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermValueObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term Value object<br>Its value MUST be <code>**data-provider**</code>|
|**value**|**required**|<code>*str*<code>||
|**unit**|optional|<code>*UnitCvTerm*<code>||
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|data-provider|provides|provided-by|study|1|1||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|study|provided-by|provides|data-provider|1|1||

### Descriptor

Descriptor node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**descriptor**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|assay|0|N||
|descriptor|describes|described-as|study|0|N||
|descriptor|describes|described-as|metadata-file|0|N||
|descriptor|describes|described-as|raw-data-file|0|N||
|descriptor|describes|described-as|derived-data-file|0|N||
|descriptor|describes|described-as|supplementary-file|0|N||
|descriptor|describes|described-as|result-file|0|N||
|descriptor|describes|described-as|metabolite|0|N||
|descriptor|describes|described-as|organization|0|N||
|descriptor|describes|described-as|person|0|N||
|descriptor|describes|described-as|project|0|N||
|descriptor|describes|described-as|publication|0|N||
|descriptor|describes|described-as|protocol|0|N||
|descriptor|describes|described-as|sample|0|N||
|descriptor|describes|described-as|subject|0|N||
|descriptor|describes|described-as|sample-run|0|N||
|descriptor|describes|described-as|sample-run-configuration|0|N||
|descriptor|keyword-of|has-repository-keyword|study|0|N||
|descriptor|keyword-of|has-repository-keyword|specimen|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|described-as|describes|descriptor|0|N|A link to a descriptor that describes the assay.|
|derived-data-file|described-as|describes|descriptor|0|N|A link to a descriptor that describes the derived data file.|
|metabolite|described-as|describes|descriptor|0|N||
|metadata-file|described-as|describes|descriptor|0|N||
|organization|described-as|describes|descriptor|0|N||
|person|described-as|describes|descriptor|0|N||
|project|described-as|describes|descriptor|0|N||
|protocol|described-as|describes|descriptor|0|N||
|publication|described-as|describes|descriptor|0|N||
|raw-data-file|described-as|describes|descriptor|0|N||
|result-file|described-as|describes|descriptor|0|N||
|sample|described-as|describes|descriptor|0|N||
|sample-run|described-as|describes|descriptor|0|N||
|sample-run-configuration|described-as|describes|descriptor|0|N||
|specimen|described-as|describes|descriptor|0|N||
|study|described-as|describes|descriptor|0|N||
|study|has-repository-keyword|keyword-of|descriptor|0|N||
|study|has-submitter-keyword|keyword-of|descriptor|0|N||
|subject|described-as|describes|descriptor|0|N||
|supplementary-file|described-as|describes|descriptor|0|N||

### Factor Type

Factor Type node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**factor-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|**required**|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-type|type-of|has-type|factor-definition|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-definition|has-type|type-of|factor-type|1|1||

### Factor Value

Factor Value node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermValueObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term Value object<br>Its value MUST be <code>**factor-value**</code>|
|**value**|optional|<code>*str or int or float or Decimal*<code>||
|**unit**|optional|<code>*UnitCvTerm*<code>||
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-value|instance-of|has-instance|factor-definition|1|N||
|factor-value|value-of|has-factor-value|sample|1|N||
|factor-value|value-of|has-factor-value|specimen|1|N||
|factor-value|value-of|has-factor-value|subject|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-definition|has-instance|instance-of|factor-value|0|N||
|sample|has-factor-value|value-of|factor-value|0|N||
|subject|has-factor-value|value-of|factor-value|0|N||

### Metabolite Identifier

Metabolite Identifier node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**metabolite-identifier**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|metabolite-identifier|reported-identifier-of|identified-as|metabolite|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|metabolite|identified-as|reported-identifier-of|metabolite-identifier|0|N||

### Parameter Type

Parameter Type node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**parameter-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|**required**|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-type|type-of|has-type|parameter-definition|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-definition|has-type|type-of|parameter-type|1|1||

### Parameter Value

Parameter Value node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermValueObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term Value object<br>Its value MUST be <code>**parameter-value**</code>|
|**value**|optional|<code>*str or int or float or Decimal*<code>||
|**unit**|optional|<code>*UnitCvTerm*<code>||
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-value|instance-of|has-instance|parameter-definition|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-definition|has-instance|instance-of|parameter-value|0|N||

### Protocol Type

Protocol Type node is optional in the  MHD Legacy Profile. <code>Minimum: 0, Maximum: N (unbounded) </code>

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**protocol-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|**required**|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|protocol-type|type-of|has-type|protocol|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|protocol|has-type|type-of|protocol-type|1|1||


## Model Graph

The following graph shows all (required and optional) nodes and relationships.

``` mermaid
graph LR
  Assay[Assay] ==>|described-as| Descriptor[Descriptor];
  Assay[Assay] ==>|part-of| Study[Study];
  Assay[Assay] ==>|follows| Protocol[Protocol];
  Characteristic_Definition[Characteristic Definition] ==>|has-instance| Characteristic_Value[Characteristic Value];
  Characteristic_Definition[Characteristic Definition] ==>|has-type| Characteristic_Type[Characteristic Type];
  Characteristic_Definition[Characteristic Definition] ==>|used-in| Study[Study];
  Derived_Data_File[Derived Data File] ==>|referenced-in| Metadata_File[Metadata File];
  Derived_Data_File[Derived Data File] ==>|created-in| Study[Study];
  Derived_Data_File[Derived Data File] ==>|described-as| Descriptor[Descriptor];
  Factor_Definition[Factor Definition] ==>|has-type| Factor_Type[Factor Type];
  Factor_Definition[Factor Definition] ==>|has-instance| Factor_Value[Factor Value];
  Factor_Definition[Factor Definition] ==>|used-in| Study[Study];
  Metabolite[Metabolite] ==>|identified-as| Metabolite_Identifier[Metabolite Identifier];
  Metabolite[Metabolite] ==>|described-as| Descriptor[Descriptor];
  Metabolite[Metabolite] ==>|reported-in| Study[Study];
  Metadata_File[Metadata File] ==>|described-as| Descriptor[Descriptor];
  Metadata_File[Metadata File] ==>|referenced-in| Metadata_File[Metadata File];
  Metadata_File[Metadata File] ==>|describes| Study[Study];
  Metadata_File[Metadata File] ==>|references| Derived_Data_File[Derived Data File];
  Metadata_File[Metadata File] ==>|references| Raw_Data_File[Raw Data File];
  Metadata_File[Metadata File] ==>|references| Result_File[Result File];
  Metadata_File[Metadata File] ==>|references| Supplementary_File[Supplementary File];
  Organization[Organization] ==>|funds| Project[Project];
  Organization[Organization] ==>|funds| Study[Study];
  Organization[Organization] ==>|manages| Project[Project];
  Organization[Organization] ==>|coordinates| Project[Project];
  Organization[Organization] ==>|affiliates| Person[Person];
  Organization[Organization] ==>|described-as| Descriptor[Descriptor];
  Parameter_Definition[Parameter Definition] ==>|has-instance| Parameter_Value[Parameter Value];
  Parameter_Definition[Parameter Definition] ==>|has-type| Parameter_Type[Parameter Type];
  Parameter_Definition[Parameter Definition] ==>|used-in| Protocol[Protocol];
  Person[Person] ==>|described-as| Descriptor[Descriptor];
  Person[Person] ==>|affiliated-with| Organization[Organization];
  Person[Person] ==>|contributes| Project[Project];
  Person[Person] ==>|contributes| Study[Study];
  Person[Person] ==>|principal-investigator-of| Study[Study];
  Person[Person] ==>|submits| Study[Study];
  Person[Person] ==>|author-of| Publication[Publication];
  Project[Project] ==>|described-as| Descriptor[Descriptor];
  Project[Project] ==>|funded-by| Organization[Organization];
  Project[Project] ==>|managed-by| Organization[Organization];
  Project[Project] ==>|coordinated-by| Organization[Organization];
  Project[Project] ==>|has-contributor| Person[Person];
  Project[Project] ==>|has-publication| Publication[Publication];
  Project[Project] ==>|has-study| Study[Study];
  Protocol[Protocol] ==>|described-as| Descriptor[Descriptor];
  Protocol[Protocol] ==>|used-in| Assay[Assay];
  Protocol[Protocol] ==>|has-parameter-definition| Parameter_Definition[Parameter Definition];
  Protocol[Protocol] ==>|used-in| Study[Study];
  Protocol[Protocol] ==>|has-type| Protocol_Type[Protocol Type];
  Publication[Publication] ==>|described-as| Descriptor[Descriptor];
  Publication[Publication] ==>|describes| Project[Project];
  Publication[Publication] ==>|describes| Study[Study];
  Publication[Publication] ==>|has-author| Person[Person];
  Raw_Data_File[Raw Data File] ==>|described-as| Descriptor[Descriptor];
  Raw_Data_File[Raw Data File] ==>|created-in| Study[Study];
  Raw_Data_File[Raw Data File] ==>|referenced-in| Metadata_File[Metadata File];
  Result_File[Result File] ==>|described-as| Descriptor[Descriptor];
  Result_File[Result File] ==>|created-in| Study[Study];
  Result_File[Result File] ==>|referenced-in| Metadata_File[Metadata File];
  Sample[Sample] ==>|described-as| Descriptor[Descriptor];
  Sample[Sample] ==>|has-factor-value| Factor_Value[Factor Value];
  Sample[Sample] ==>|used-in| Study[Study];
  Sample[Sample] ==>|derived-from| Subject[Subject];
  Sample[Sample] ==>|derived-from| Specimen[Specimen];
  Sample[Sample] ==>|has-characteristic-value| Characteristic_Value[Characteristic Value];
  Sample_Run[Sample Run] ==>|described-as| Descriptor[Descriptor];
  Sample_Run_Configuration[Sample Run Configuration] ==>|described-as| Descriptor[Descriptor];
  Specimen[Specimen] ==>|described-as| Descriptor[Descriptor];
  Specimen[Specimen] ==>|has-characteristic-value| Characteristic_Value[Characteristic Value];
  Specimen[Specimen] ==>|source-of| Sample[Sample];
  Specimen[Specimen] ==>|derived-from| Subject[Subject];
  Study[Study] ==>|provided-by| Data_Provider[Data Provider];
  Study[Study] ==>|has-assay| Assay[Assay];
  Study[Study] ==>|funded-by| Organization[Organization];
  Study[Study] ==>|has-characteristic-definition| Characteristic_Definition[Characteristic Definition];
  Study[Study] ==>|has-derived-data-file| Derived_Data_File[Derived Data File];
  Study[Study] ==>|described-as| Descriptor[Descriptor];
  Study[Study] ==>|has-factor-definition| Factor_Definition[Factor Definition];
  Study[Study] ==>|has-repository-keyword| Descriptor[Descriptor];
  Study[Study] ==>|has-submitter-keyword| Descriptor[Descriptor];
  Study[Study] ==>|reports| Metabolite[Metabolite];
  Study[Study] ==>|has-metadata-file| Metadata_File[Metadata File];
  Study[Study] ==>|has-contributor| Person[Person];
  Study[Study] ==>|has-principal-investigator| Person[Person];
  Study[Study] ==>|submitted-by| Person[Person];
  Study[Study] ==>|part-of| Project[Project];
  Study[Study] ==>|has-protocol| Protocol[Protocol];
  Study[Study] ==>|has-publication| Publication[Publication];
  Study[Study] ==>|has-raw-data-file| Raw_Data_File[Raw Data File];
  Study[Study] ==>|has-result-file| Result_File[Result File];
  Study[Study] ==>|has-sample| Sample[Sample];
  Study[Study] ==>|has-supplementary-file| Supplementary_File[Supplementary File];
  Subject[Subject] ==>|described-as| Descriptor[Descriptor];
  Subject[Subject] ==>|has-characteristic-value| Characteristic_Value[Characteristic Value];
  Subject[Subject] ==>|source-of| Sample[Sample];
  Subject[Subject] ==>|has-factor-value| Factor_Value[Factor Value];
  Subject[Subject] ==>|source-of| Specimen[Specimen];
  Supplementary_File[Supplementary File] ==>|described-as| Descriptor[Descriptor];
  Supplementary_File[Supplementary File] ==>|created-in| Study[Study];
  Supplementary_File[Supplementary File] ==>|referenced-in| Metadata_File[Metadata File];
  Characteristic_Type[Characteristic Type] ==>|type-of| Characteristic_Definition[Characteristic Definition];
  Characteristic_Value[Characteristic Value] ==>|instance-of| Characteristic_Definition[Characteristic Definition];
  Characteristic_Value[Characteristic Value] ==>|value-of| Subject[Subject];
  Characteristic_Value[Characteristic Value] ==>|value-of| Specimen[Specimen];
  Characteristic_Value[Characteristic Value] ==>|value-of| Sample[Sample];
  Data_Provider[Data Provider] ==>|provides| Study[Study];
  Descriptor[Descriptor] ==>|describes| Assay[Assay];
  Descriptor[Descriptor] ==>|describes| Study[Study];
  Descriptor[Descriptor] ==>|describes| Metadata_File[Metadata File];
  Descriptor[Descriptor] ==>|describes| Raw_Data_File[Raw Data File];
  Descriptor[Descriptor] ==>|describes| Derived_Data_File[Derived Data File];
  Descriptor[Descriptor] ==>|describes| Supplementary_File[Supplementary File];
  Descriptor[Descriptor] ==>|describes| Result_File[Result File];
  Descriptor[Descriptor] ==>|describes| Metabolite[Metabolite];
  Descriptor[Descriptor] ==>|describes| Organization[Organization];
  Descriptor[Descriptor] ==>|describes| Person[Person];
  Descriptor[Descriptor] ==>|describes| Project[Project];
  Descriptor[Descriptor] ==>|describes| Publication[Publication];
  Descriptor[Descriptor] ==>|describes| Protocol[Protocol];
  Descriptor[Descriptor] ==>|describes| Sample[Sample];
  Descriptor[Descriptor] ==>|describes| Subject[Subject];
  Descriptor[Descriptor] ==>|describes| Sample_Run[Sample Run];
  Descriptor[Descriptor] ==>|describes| Sample_Run_Configuration[Sample Run Configuration];
  Descriptor[Descriptor] ==>|describes| Metabolite[Metabolite];
  Descriptor[Descriptor] ==>|keyword-of| Study[Study];
  Descriptor[Descriptor] ==>|keyword-of| Study[Study];
  Descriptor[Descriptor] ==>|keyword-of| Specimen[Specimen];
  Factor_Type[Factor Type] ==>|type-of| Factor_Definition[Factor Definition];
  Factor_Value[Factor Value] ==>|instance-of| Factor_Definition[Factor Definition];
  Factor_Value[Factor Value] ==>|value-of| Sample[Sample];
  Factor_Value[Factor Value] ==>|value-of| Specimen[Specimen];
  Factor_Value[Factor Value] ==>|value-of| Subject[Subject];
  Metabolite_Identifier[Metabolite Identifier] ==>|reported-identifier-of| Metabolite[Metabolite];
  Parameter_Type[Parameter Type] ==>|type-of| Parameter_Definition[Parameter Definition];
  Parameter_Value[Parameter Value] ==>|instance-of| Parameter_Definition[Parameter Definition];
  Protocol_Type[Protocol Type] ==>|type-of| Protocol[Protocol];
```
