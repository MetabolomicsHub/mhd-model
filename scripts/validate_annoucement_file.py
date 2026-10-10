import logging
import pathlib

from mhd_model.utils import setup_basic_logging_config
from mhd_model.validation import validate_announcement_file

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # ontology_lookup_file_path = ".db/ontology_lookup.db"
    ontology_lookup_file_path = None
    setup_basic_logging_config()
    result = validate_announcement_file(
        announcement_file_path=pathlib.Path("example_input_01.json"),
        ontology_lookup_file_path=ontology_lookup_file_path,
    )
    for message in result or []:
        logger.error(message)
