import logging

from mhd_model.log_utils import set_basic_logging_config
from scripts.update_ontology_sources import update_ontology_source_json
from scripts.update_profiles import update_schema_files
from scripts.update_v1_0_documentation import update_v1_0_documentation

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    set_basic_logging_config()
    update_schema_files()
    update_ontology_source_json()
    # update_v1_0_documentation()
    update_v1_0_documentation()
