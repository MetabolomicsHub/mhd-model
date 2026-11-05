import logging
from pathlib import Path

from cachetools import cached

from mhd_model.shared.validation.cv_term_helper import CvTermHelper
from mhd_model.shared.validation.mhd_ontology_lookup_cv_term_helper import (
    MhdOntologyLookupCvTermHelper,
)
from mhd_model.shared.validation.ontology_lookup_cv_term_helper import (
    OntologyLookupCvTermHelper,
)

logger = logging.getLogger(__name__)


@cached(cache={})
def select_cv_term_helper(
    db_path: None | str, ontology_lookup_service_url: None | str = None
):
    if db_path and not Path(db_path).exists():
        logger.warning("%s path is defined but does not exist")
    if not db_path or not Path(db_path).exists():
        if ontology_lookup_service_url:
            return MhdOntologyLookupCvTermHelper(ontology_lookup_service_url)
        return CvTermHelper()
    return OntologyLookupCvTermHelper(db_path=db_path)
