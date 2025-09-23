from pathlib import Path

from mhd_model.convertors.sdrf.mhd2sdrf import create_sdrf_files
from scripts.utils import set_basic_logging_config

if __name__ == "__main__":
    set_basic_logging_config()
    mtbls_public_ftp_base_url: str = (
        "ftp://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public"
    )

    files = list(Path("tests/data/mhd_data/legacy").glob("*.mhd.json"))
    for file in files:
        sdrf_file_root_path = "tests/data/sdrf_files/legacy"
        Path(sdrf_file_root_path).mkdir(parents=True, exist_ok=True)

        create_sdrf_files(str(file), sdrf_file_root_path)
