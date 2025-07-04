# Metabolomics Hub Common Data Model Nodes

## MHD Domain Objects

### Assay

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|Its value MUST be <code>**assay**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**repository_identifier**|**required**|<code>*str*<code>|An assay identifier that uniquely identifies the assay in repository<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the assay. It SHOULD be unique in a study<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**metadata_file_ref**|**required**|<code>*MhdObjectId*<code>|Target node type: <code>**metadata-file**</code><br>Validation Rule:<br> <code>Target node type: <code>**metadata-file**</code></code>|
|**technology_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [OBI, OBI:0000470, mass spectrometry assay],<br>* [OBI, OBI:0000623, NMR spectroscopy assay]</code>|
|**analysis_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [OBI, OBI:0003097, liquid chromatography mass spectrometry assay],<br>* [OBI, OBI:0003110, gas chromatography mass spectrometry assay],<br>* [OBI, OBI:0000470, mass spectrometry assay],<br>* [OBI, OBI:0000623, NMR spectroscopy assay]</code>|
|**measurement_methodology_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**descriptor**</code><br>Validation Rules:<br> <code>Target node type: <code>**descriptor**</code><br>Allowed CV Terms:<br>* [MSIO, MSIO:0000100, targeted metabolite profiling],<br>* [MSIO, MSIO:0000101, untargeted metabolite profiling],<br>* [OBI, OBI:0000366, metabolite profiling assay]</code>|
|**protocol_refs**|optional|<code>*list[MhdObjectId]*<code>|The id properties of protocols used in assay. A protocol is a defined and standardized procedure followed to collect, prepare, or analyze biological samples<br>Target node type: <code>**protocol**</code><br>Validation Rule:<br> <code>Target node type: <code>**protocol**</code></code>|
|**sample_run_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**sample-run**</code><br>Validation Rule:<br> <code>Target node type: <code>**sample-run**</code></code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|described-as|describes|descriptor|0|N|A link to a descriptor that describes the assay.|
|assay|follows|used-in|protocol|0|N|A link to a protocol conducted in assay.|
|assay|has-derived-data-file|created-in|derived-data-file|0|N|A link to a descriptor that describes the assay.|
|assay|part-of|has-assay|study|1|1|A link to a study that the assay was conducted as part of it to generate data addressing study objectives<br>**Required min count in the dataset: 1.**|


**Embedded Relationships**: <code>descriptor, metadata-file, protocol, sample-run</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|derived-data-file|created-in|has-derived-data-file|assay|0|N||
|descriptor|describes|described-as|assay|0|N||
|protocol|used-in|follows|assay|0|N||
|study|has-assay|part-of|assay|1|N|**Required min count in the dataset: 1.**|

### Characteristic Definition

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**characteristic-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**characteristic_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**characteristic-type**</code><br>Validation Rules:<br> <code>Target node type: <code>**characteristic-type**</code><br>Allowed CV Terms:<br>* [NCIT, NCIT:C14250, organism],<br>* [NCIT, NCIT:C103199, organism part],<br>* [EFO, EFO:0000408, disease],<br>* [EFO, EFO:0000324, cell type]</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-definition|has-instance|instance-of|characteristic-value|0|N|**Required min count in the dataset: 2.**<br><br>Target Validation Rules:<br><code>-----<br>**Conditional - (Organism)**<br>[Source characteristic_type_ref.accession = NCIT:C14250]<br>Ontology Sources:ENVO, NCBITAXON<br>Exceptions:<br>Allowed Other Sources: wikidata<br>-----<br>**Conditional - (Organism part)**<br>[Source characteristic_type_ref.accession = NCIT:C103199]<br>Ontology Sources:UBERON, BTO, NCIT<br>Exceptions:<br>Allowed Other Sources: wikidata<br>-----<br>**Conditional - (Disease)**<br>[Source characteristic_type_ref.accession = EFO:0000408]<br>Ontology Sources:DOID, HP, MP<br>-----<br>**Conditional - (Cell type)**<br>[Source characteristic_type_ref.accession = EFO:0000324]<br>Ontology Sources:CL</code><br>-----|
|characteristic-definition|used-in|has-characteristic-definition|study|0|N|**Required min count in the dataset: 2.**|


**Embedded Relationships**: <code>characteristic-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|instance-of|has-instance|characteristic-definition|1|N|**Required min count in the dataset: 2.**|
|study|has-characteristic-definition|used-in|characteristic-definition|2|N|**Required min count in the dataset: 2.**|

### Derived Data File

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**derived-data-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|**required**|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|optional|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|derived-data-file|created-in|has-derived-data-file|assay|0|N||
|derived-data-file|created-in|has-derived-data-file|study|1|1||
|derived-data-file|described-as|describes|descriptor|0|N|A link to a descriptor that describes the derived data file.|
|derived-data-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|has-derived-data-file|created-in|derived-data-file|0|N|A link to a descriptor that describes the assay.|
|descriptor|describes|described-as|derived-data-file|0|N||
|metadata-file|references|referenced-in|derived-data-file|0|N||
|study|has-derived-data-file|created-in|derived-data-file|0|N||

### Factor Definition

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**factor-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**factor_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**factor-type**</code><br>Validation Rules:<br> <code>Target node type: <code>**factor-type**</code><br>Allowed CV Terms:<br>* [EFO, EFO:0000408, disease]</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-definition|has-instance|instance-of|factor-value|0|N|Target Validation Rule:<br><code>-----<br>**Conditional - (Disease)**<br>[Source factor_type_ref.accession = EFO:0000408]<br>Ontology Sources:DOID, HP, MP</code><br>-----|
|factor-definition|used-in|has-factor-definition|study|0|N||


**Embedded Relationships**: <code>factor-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-value|instance-of|has-instance|factor-definition|1|N||
|study|has-factor-definition|used-in|factor-definition|0|N||

### Metabolite

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**metabolite**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**metadata-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|**required**|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|**required**|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|**required**|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|metadata-file|describes|has-metadata-file|study|1|N|**Required min count in the dataset: 1.**|
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
|study|has-metadata-file|describes|metadata-file|1|N|**Required min count in the dataset: 1.**|
|supplementary-file|referenced-in|references|metadata-file|0|N||

### Organization

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**organization**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**repository_identifier**|optional|<code>*str*<code>||
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
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
|organization|manages|managed-by|project|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|organization|0|N||
|person|affiliated-with|affiliates|organization|0|N||
|project|coordinated-by|coordinates|organization|0|N||
|project|funded-by|funds|organization|0|N||
|project|managed-by|manages|organization|0|N||

### Parameter Definition

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**parameter-definition**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**parameter_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target node type: <code>**parameter-type**</code><br>Validation Rule:<br> <code>Target node type: <code>**parameter-type**</code></code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-definition|has-instance|instance-of|parameter-value|0|N|**Required min count in the dataset: 1.**<br>Target Validation Rule:<br><code>-----<br>**Conditional - (Mass spectrometry instrument)**<br>[Source parameter_type_ref.accession = MSIO:0000171]<br>Allowed Parent CV Terms:<br>* [MS, MS:1000031, instrument model]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: Yes<br>Excluded CV Terms:<br>* [MS, MS:1000491, Dionex instrument model],<br>* [MS, MS:1000488, Hitachi instrument model]</code><br>-----|


**Embedded Relationships**: <code>parameter-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-value|instance-of|has-instance|parameter-definition|1|N|**Required min count in the dataset: 1.**|
|protocol|has-parameter-definition|defined-in|parameter-definition|0|N|**Required min count in the dataset: 1.**|

### Person

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The value of this property MUST be 'person'<br>Its value MUST be <code>**person**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**full_name**|optional|<code>*str*<code>|Full name of person|
|**orcid**|optional|<code>*str*<code>|ORCID identifier of person<br><br>Example: <br><code>"1234-0001-8473-1713"<br>"1234-0001-8473-171X"</code>|
|**emails**|optional|<code>*list[EmailStr]*<code>|Email addresses of person|
|**phones**|optional|<code>*list[str]*<code>|Phone number of person (with international country code)<br><br>Example: <br><code>[<br>  "+449340917271",<br>  "00449340917271"<br>]</code>|
|**addresses**|optional|<code>*list[str]*<code>||


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|person|affiliated-with|affiliates|organization|0|N||
|person|author-of|has-author|publication|0|N||
|person|contributes|has-contributor|project|0|N||
|person|contributes|has-contributor|study|0|N||
|person|described-as|describes|descriptor|0|N||
|person|principal-investigator-of|has-principal-investigator|study|0|N|**Required min count in the dataset: 1.**|
|person|submits|submitted-by|study|0|1|**Required min count in the dataset: 1.**|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|person|0|N||
|organization|affiliates|affiliated-with|person|0|N||
|project|has-contributor|contributes|person|0|N||
|publication|has-author|author-of|person|0|N||
|study|has-contributor|contributes|person|0|N||
|study|has-principal-investigator|principal-investigator-of|person|0|N|**Required min count in the dataset: 1.**|
|study|submitted-by|submits|person|1|N|**Required min count in the dataset: 1.**|

### Project

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**project**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**title**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**description**|optional|<code>*str*<code>||
|**grant_identifiers**|optional|<code>*list[Annotated]*<code>||
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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**protocol**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>||
|**protocol_type_ref**|**required**|<code>*CvTermObjectId*<code>|Target CV term type: <code>**protocol-type**</code><br>Validation Rules:<br> <code>Target node type: <code>**protocol-type**</code><br>Allowed CV Terms:<br>* [EFO, EFO:0005518, sample collection protocol],<br>* [MS, MS:1000831, sample preparation],<br>* [CHMO, CHMO:0000470, mass spectrometry],<br>* [OBI, OBI:0200000, data transform],<br>* [MI, MI:2131, metabolite identification],<br>* [CHMO, CHMO:0001000, chromatography],<br>* [EFO, EFO:0003969, treatment protocol],<br>* [CHMO, CHMO:0001024, capillary electrophoresis],<br>* [MS, MS:1000058, flow injection analysis]<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**description**|**required**|<code>*str*<code>||
|**parameter_definition_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**parameter-definition**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|protocol|described-as|describes|descriptor|0|N||
|protocol|has-parameter-definition|defined-in|parameter-definition|0|N|**Required min count in the dataset: 1.**|
|protocol|used-in|follows|assay|0|N||
|protocol|used-in|has-protocol|study|1|N|**Required min count in the dataset: 1.**|


**Embedded Relationships**: <code>protocol-type</code>


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|follows|used-in|protocol|0|N|A link to a protocol conducted in assay.|
|descriptor|describes|described-as|protocol|0|N||
|study|has-protocol|used-in|protocol|0|N|**Required min count in the dataset: 1.**|

### Publication

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**publication**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**title**|**required**|<code>*str*<code>||
|**doi**|**required**|<code>*str*<code>||
|**pub_med_id**|optional|<code>*str*<code>||
|**authors**|optional|<code>*list[Annotated]*<code>||


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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**raw-data-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|**required**|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|**required**|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|optional|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|raw-data-file|created-in|has-raw-data-file|study|1|1|**Required min count in the dataset: 1.**|
|raw-data-file|described-as|describes|descriptor|0|N||
|raw-data-file|referenced-in|references|metadata-file|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|raw-data-file|0|N||
|metadata-file|references|referenced-in|raw-data-file|0|N||
|study|has-raw-data-file|created-in|raw-data-file|1|N|**Required min count in the dataset: 1.**|

### Result File

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**result-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|**required**|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|**required**|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**extension**|optional|<code>*str*<code>|The extension of file. It MUST contain all extensions (e.g., .raw, .mzML, .d.zip, .raw.zip, etc.)|


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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**repository_identifier**|**required**|<code>*str*<code>||
|**additional_identifiers**|optional|<code>*list[CvTermValue]*<code>||
|**subject_refs**|**required**|<code>*list[MhdObjectId]*<code>|Minimum length: <code>1</code><br>Target node type: <code>**subject**</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|sample|derived-from|source-of|subject|1|N||
|sample|described-as|describes|descriptor|0|N||
|sample|has-factor-value|value-of|factor-value|0|N||
|sample|used-in|has-sample|study|1|1||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|sample|0|N||
|factor-value|value-of|has-factor-value|sample|1|N||
|study|has-sample|used-in|sample|0|N||
|subject|source-of|derived-from|sample|1|N||

### Sample Run

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample-run**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|optional|<code>*str*<code>||
|**sample_ref**|**required**|<code>*MhdObjectId*<code>|Target node type: <code>**sample**</code>|
|**sample_run_configuration_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**sample-run-configuration**</code>|
|**raw_data_file_refs**|**required**|<code>*list[MhdObjectId]*<code>|Minimum length: <code>1</code><br>Target node type: <code>**raw-data-file**</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**derived_data_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**derived-data-file**</code>|
|**result_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**result-file**</code>|
|**supplementary_file_refs**|optional|<code>*list[MhdObjectId]*<code>|Target node type: <code>**supplementary-file**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|sample-run|described-as|describes|descriptor|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|sample-run|0|N||

### Sample Run Configuration

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**sample-run-configuration**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**protocol_ref**|**required**|<code>*MhdObjectId*<code>|Target node type: <code>**protocol**</code>|
|**parameter_value_refs**|optional|<code>*list[MhdObjectId or CvTermObjectId or CvTermValueObjectId]*<code>|Target node type: <code>**parameter-value**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|descriptor|describes|described-as|sample-run-configuration|0|N||

### Study

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**study**</code>|
|**created_by_ref**|**required**|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**mhd_identifier**|**required**|<code>*str*<code>|Minimum length: <code>8</code><br>Validation Rule:<br> <code>Min Length: 8, Required</code>|
|**repository_identifier**|optional|<code>*str*<code>||
|**additional_identifiers**|optional|<code>*list[KeyValue]*<code>|Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**title**|**required**|<code>*str*<code>|Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**description**|**required**|<code>*str*<code>|Minimum length: <code>5</code><br>Validation Rule:<br> <code>Min Length: 5, Required</code>|
|**submission_date**|**required**|<code>*datetime*<code>||
|**public_release_date**|**required**|<code>*datetime*<code>||
|**dataset_license**|**required**|<code>*HttpUrl*<code>|<br>Example: <br><code>"https://creativecommons.org/publicdomain/zero/1.0"</code>|
|**dataset_uri_list**|optional|<code>*list[KeyValue]*<code>||
|**related_datasets**|optional|<code>*list[KeyValue]*<code>||
|**protocol_refs**|**required**|<code>*list[MhdObjectId]*<code>|Target node type: <code>**protocol**</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|study|defines|defined-in|characteristic-type|2|N|**Required min count in the dataset: 2.**|
|study|described-as|describes|descriptor|0|N||
|study|has-assay|part-of|assay|1|N|**Required min count in the dataset: 1.**|
|study|has-characteristic-definition|used-in|characteristic-definition|2|N|**Required min count in the dataset: 2.**|
|study|has-contributor|contributes|person|0|N||
|study|has-derived-data-file|created-in|derived-data-file|0|N||
|study|has-factor-definition|used-in|factor-definition|0|N||
|study|has-metadata-file|describes|metadata-file|1|N|**Required min count in the dataset: 1.**|
|study|has-principal-investigator|principal-investigator-of|person|0|N|**Required min count in the dataset: 1.**|
|study|has-protocol|used-in|protocol|0|N|**Required min count in the dataset: 1.**|
|study|has-publication|describes|publication|0|N||
|study|has-raw-data-file|created-in|raw-data-file|1|N|**Required min count in the dataset: 1.**|
|study|has-repository-keyword|keyword-of|descriptor|0|N||
|study|has-result-file|created-in|result-file|0|N||
|study|has-sample|used-in|sample|0|N||
|study|has-submitter-keyword|keyword-of|descriptor|0|N|Target Validation Rule:<br><code>-----<br>Allow any valid CV Term<br>Exceptions:<br>Allowed Placeholder Values: source='' accession=''<br>Allowed Other Sources: wikidata</code><br>-----|
|study|has-supplementary-file|created-in|supplementary-file|0|N||
|study|part-of|has-study|project|0|N||
|study|reports|reported-in|metabolite|0|N||
|study|submitted-by|submits|person|1|N|**Required min count in the dataset: 1.**|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|part-of|has-assay|study|1|1|A link to a study that the assay was conducted as part of it to generate data addressing study objectives<br>**Required min count in the dataset: 1.**|
|characteristic-definition|used-in|has-characteristic-definition|study|0|N|**Required min count in the dataset: 2.**|
|characteristic-type|defined-in|defines|study|1|1|**Required min count in the dataset: 2.**|
|data-provider|provides|provided-by|study|0|N||
|derived-data-file|created-in|has-derived-data-file|study|1|1||
|descriptor|describes|described-as|study|0|N||
|descriptor|keyword-of|has-repository-keyword|study|0|N||
|factor-definition|used-in|has-factor-definition|study|0|N||
|factor-type|used-in|use-factor-type|study|0|N||
|metabolite|reported-in|reports|study|1|N||
|metadata-file|describes|has-metadata-file|study|1|N|**Required min count in the dataset: 1.**|
|person|contributes|has-contributor|study|0|N||
|person|principal-investigator-of|has-principal-investigator|study|0|N|**Required min count in the dataset: 1.**|
|person|submits|submitted-by|study|0|1|**Required min count in the dataset: 1.**|
|project|has-study|part-of|study|0|N||
|protocol|used-in|has-protocol|study|1|N|**Required min count in the dataset: 1.**|
|publication|describes|has-publication|study|0|1||
|raw-data-file|created-in|has-raw-data-file|study|1|1|**Required min count in the dataset: 1.**|
|result-file|created-in|has-result-file|study|1|N||
|sample|used-in|has-sample|study|1|1||
|supplementary-file|created-in|has-supplementary-file|study|1|N||

### Subject

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**subject**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|optional|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term|
|**name**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**subject_type**|optional|<code>*CvTerm*<code>||
|**repository_identifier**|**required**|<code>*str*<code>|Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|subject|described-as|describes|descriptor|0|N||
|subject|has-characteristic-value|value-of|characteristic-value|2|N||
|subject|source-of|derived-from|sample|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-value|value-of|has-characteristic-value|subject|1|N||
|descriptor|describes|described-as|subject|0|N||
|sample|derived-from|source-of|subject|1|N||

### Supplementary File

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*MhdObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the object<br>Its value MUST be <code>**supplementary-file**</code>|
|**created_by_ref**|optional|<code>*CvTermValueObjectId*<code>|The id property of the data-provider who created the object<br>Target CV term type: <code>**data-provider**</code><br>Validation Rule:<br> <code>Allow any valid CV Term<br>Exceptions:<br>Allowed Other Sources: wikidata</code>|
|**tags**|optional|<code>*list[KeyValue]*<code>|Key-value tags related to the object|
|**descriptors**|optional|<code>*list[CvTerm]*<code>|Descriptors of the object|
|**external_references**|optional|<code>*list[KeyValue]*<code>|External references related to the object|
|**uri_list**|**required**|<code>*list[KeyValue]*<code>|URI list related to the object. Key MUST be uri type CV Term<br>Minimum length: <code>1</code><br>Validation Rule:<br> <code>Min Length: 1, Required</code>|
|**name**|**required**|<code>*str*<code>|Name of the file. File MUST be a file (not folder or link).It MAY be relative path (e.g., FILES/study.txt) or a file in a compressed file (e.g., FILES/study.zip#data/metadata.tsv)<br>Minimum length: <code>2</code><br>Validation Rule:<br> <code>Min Length: 2, Required</code>|
|**size**|optional|<code>*int*<code>|The size of the file in bytes, representing the total amount of data contained in the file|
|**hash_sha256**|optional|<code>*str*<code>|The SHA-256 cryptographic hash of the file content, used to verify file integrity and ensure that the file has not been altered|
|**format_ref**|**required**|<code>*CvTermObjectId*<code>|The structure or encoding used to store the contents of the file, typically indicated by its extension (e.g., .txt, .csv, .mzML, .raw, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
|**compression_format_ref**|optional|<code>*CvTermObjectId*<code>|The structure or encoding used to compress the contents of the file, typically indicated by its extension (e.g., .zip, .tar, .gz, etc.)<br>Target CV term type: <code>**descriptor**</code><br>Validation Rule:<br> <code>Allowed Parent CV Terms:<br>* [EDAM, EDAM:1915, Format]<br>Allow parent CV Term: No<br>Allow only leaf CV Terms: No</code>|
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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**characteristic-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-type|defined-in|defines|study|1|1|**Required min count in the dataset: 2.**|
|characteristic-type|type-of|has-type|characteristic-value|0|N|**Required min count in the dataset: 2.**|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|study|defines|defined-in|characteristic-type|2|N|**Required min count in the dataset: 2.**|

### Characteristic Value

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
|characteristic-value|instance-of|has-instance|characteristic-definition|1|N|**Required min count in the dataset: 2.**|
|characteristic-value|value-of|has-characteristic-value|subject|1|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|characteristic-definition|has-instance|instance-of|characteristic-value|0|N|**Required min count in the dataset: 2.**|
|characteristic-type|type-of|has-type|characteristic-value|0|N|**Required min count in the dataset: 2.**|
|subject|has-characteristic-value|value-of|characteristic-value|2|N||

### Data Provider

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
|data-provider|provides|provided-by|study|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|

### Descriptor

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


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|assay|described-as|describes|descriptor|0|N|A link to a descriptor that describes the assay.|
|derived-data-file|described-as|describes|descriptor|0|N|A link to a descriptor that describes the derived data file.|
|metabolite|described-as|describes|descriptor|0|N||
|organization|described-as|describes|descriptor|0|N||
|person|described-as|describes|descriptor|0|N||
|project|described-as|describes|descriptor|0|N||
|protocol|described-as|describes|descriptor|0|N||
|publication|described-as|describes|descriptor|0|N||
|raw-data-file|described-as|describes|descriptor|0|N||
|result-file|described-as|describes|descriptor|0|N||
|sample|described-as|describes|descriptor|0|N||
|sample-run|described-as|describes|descriptor|0|N||
|study|described-as|describes|descriptor|0|N||
|study|has-repository-keyword|keyword-of|descriptor|0|N||
|study|has-submitter-keyword|keyword-of|descriptor|0|N||
|subject|described-as|describes|descriptor|0|N||
|supplementary-file|described-as|describes|descriptor|0|N||

### Factor Type

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**factor-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-type|type-of|has-type|factor-value|0|N||
|factor-type|used-in|use-factor-type|study|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|

### Factor Value

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


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|factor-definition|has-instance|instance-of|factor-value|0|N||
|factor-type|type-of|has-type|factor-value|0|N||
|sample|has-factor-value|value-of|factor-value|0|N||

### Metabolite Identifier

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

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**parameter-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-type|type-of|has-type|parameter-value|0|N||


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-value|has-type|type-of|parameter-type|1|N|**Required min count in the dataset: 1.**|

### Parameter Value

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
|parameter-value|has-type|type-of|parameter-type|1|N|**Required min count in the dataset: 1.**|
|parameter-value|instance-of|has-instance|parameter-definition|1|N|**Required min count in the dataset: 1.**|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|
|parameter-definition|has-instance|instance-of|parameter-value|0|N|**Required min count in the dataset: 1.**|
|parameter-type|type-of|has-type|parameter-value|0|N||

### Protocol Type

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**protocol-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|

### Uri Type

**Properties**

|Property Name|Necessity|Type|Description|
|-------------|---------|----|-----------|
|**id**|optional|<code>*CvTermObjectId*<code>|The id property uniquely identifies the object|
|**type**|optional|<code>*MhdObjectType*<code>|The type property identifies type of the CV Term object<br>Its value MUST be <code>**uri-type**</code>|
|**source**|optional|<code>*str*<code>|Ontology source name|
|**accession**|optional|<code>*str*<code>|Accession number of CV term in compact URI format|
|**name**|optional|<code>*str*<code>|Label of CV term|


**Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|


**Reverse Node Relationships**

|Source|Relationship|Reverse Name|Target|Min|Max|Description|
|------|------------|------------|------|---|---|-----------|

