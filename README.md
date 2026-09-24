# MetabolomicsHub Common Data Model and Utility Tools (mhd-model)

You can find documentation [on Github](https://metabolomicshub.github.io/mhd-model/)

## Repository Integration with Command Line Tool

Upon completing the MetabolomicsHub consortium agreement and repository registration, repositories may start MetabolomicsHub integration. A repository will use the submission endpoints to acquire an MHD accession number and make public dataset announcements.

You can use **mhd-cli** tool to create the required files for registration and use the most common MetabolomicsHub submission REST web service endpoints.

Before proceeding next steps, you need to install **mhd-cli** tool. Please ensure that python >=3.12 and pip commands are already installed.

### Step 1: Command Line Tool Installation

```bash
# ensure python version is equal or greater than 3.12. Otherwise install new Python version
python --version

# Insure your mhd-model library is up-to-date. Remove current installation from your environment.
pip uninstall mhd-model -y

# Ensure install the new mhd-model library
pip install mhd-model

# Check mhd-cli command line and its version
mhd-cli --version

# Check mhd-cli command line and its version
mhd-cli --help
#############################################################################
# Example output
#############################################################################
# Usage: mhd-cli [OPTIONS] COMMAND [ARGS]...
#   MetabomicsHub CLI with subcommands.
# Options:
#   --version   Show the version and exit.
#   -h, --help  Show this message and exit.
# Commands:
#   client    utilities to communicate with MHD Server.
#   create    utilities to create and convert files (announcement file, etc.).
#   validate  utilities to validate MetabolomicsHub files.
#############################################################################
```

### Step 2: Repository Registration

You can use *mhd-cli* command to create public key files for repository registration. You MUST keep the generated private keys in secure place.

MetabolomicsHub needs some information from repositories to store in the database. You need to share the following information (*not private key files*) with MetabolomicsHub:

- Repository Name: Name of the repository (*Case sensitive*). e.g. MetaboLights, Metabolomics Workbench
- Repository Short Name: Sort name of the repository (*Case sensitive*). e.g. mtbls, mw
- Repository Description: Short description about the repository
- Repository Logo URL: Repository logo URL
- Repository public keys: Public key file created by repositories. It will be used to validate repository REST API web service requests. MetabolomicsHub will request *two public keys* for production and test environments.

```bash
# create public and private key files
mhd-cli client key-pair create --output-folder mhd-production-keys
# This command creates public_key.pem and private_key.pem files in 'mhd-production-keys' subfolder

mhd-cli client key-pair create --output-folder mhd-test-keys
# This command creates public_key.pem and private_key.pem files in 'mhd-test-keys' subfolder

```

After receiving the required information, MetabolomicsHub will update the databases to allow the repository web service requests.

### Step 3: Create MHD API Tokens

A repository signed JWT token is required to create and delete a repository API token. You can use *mhd-cli* command to create a signed JWT token. Public and private key files are required to create a valid signed JWT token.

Notes:

- Signed JWT tokens MUST be created with public key shared with MetabolomicsHub
- Keep the signed JWT token in secure place.

```bash

mhd-cli client signed-jwt create --repository-name 'Metabolomics Workbench' --private-key-path mhd-production-keys/private_key.pem --public-key-path mhd-production-keys/private_key.pem  --output-file-path mhd-production-keys/signed-jwt.txt

# You can test the signed JWT token content
mhd-cli client signed-jwt show --signed-jwt-file-path mhd-production-keys/signed-jwt.txt

# For test environment
mhd-cli client signed-jwt create --repository-name 'Metabolomics Workbench' --private-key-path mhd-test-keys/private_key.pem --public-key-path mhd-test-keys/private_key.pem  --output-file-path mhd-test-keys/signed-jwt.txt

# You can test the signed JWT token content
mhd-cli client signed-jwt show --signed-jwt-file-path mhd-test-keys/signed-jwt.txt

```

If you have a valid signed JWT token, you can create an API token with a name. API tokens are not stored on MetabolomicsHub database and shown only once they are created. So keep them in a secure place.

```bash
export PRODUCTION_MHD_SERVER_URL="https://www.metabolomicshub.org/api/submission"
export TEST_MHD_SERVER_URL="https://www.metabolomicshub.org/test/api/submission"
# API token creation for production
mhd-cli client api-token create \
    --token-name prod-2026-09 \
    --signed-jwt-file-path mhd-production-keys/signed-jwt.txt \
    --mhd-server-url $PRODUCTION_MHD_SERVER_URL \
    --output-file-path mhd-production-keys/api-token-prod-2026-09.txt


# API token creation for test
mhd-cli client api-token create \
    --token-name test-2026-09 \
    --signed-jwt-file-path mhd-test-keys/signed-jwt.txt \
    --mhd-server-url $TEST_MHD_SERVER_URL \
    --output-file-path mhd-test-keys/api-token-test-2026-09.txt

```

### Step 4: Integration of MHD Dataset Accession

After completion of a dataset in repository, repositories will request an MHD accession for each MHD dataset.

```bash
##################################################################################
# STEP 1: STORE THE FOLLOWING INFORMATION IN DATABASE FOR EACH DATASET
#         - DATASET CATEGORY (MS MHD, MS LEGACY, OTHER, etc.),
#         - MHD VERSION (IF DATASET IS MS MHD OR LEGACY)
#         - MHD ACCESSION (IF DATASET IS MS MHD)
##################################################################################

##################################################################################
# STEP 2.1: REQUEST MHD ACCESSION FOR EACH MS MHD DATASET AFTER ITS COMPLETION
##################################################################################

export PRODUCTION_MHD_SERVER_URL="https://www.metabolomicshub.org/api/submission"
export TEST_MHD_SERVER_URL="https://www.metabolomicshub.org/test/api/submission"

# Get an MHD accession for a repository dataset on test MHD server
mhd-cli client fetch-mhd-accession \
    --dataset-repository-identifier ST912345 \
    --api-token-file-path mhd-test-keys/api-token-test-2026-09.txt \
    --mhd-server-url $TEST_MHD_SERVER_URL \
    --accession-type mhd

# If it is legacy dataset. Register it on test MHD server
mhd-cli client fetch-mhd-accession \
    --dataset-repository-identifier ST004212
    --api-token-file-path mhd-test-keys/api-token-test-2026-09.txt \
    --mhd-server-url $TEST_MHD_SERVER_URL \
    --accession-type legacy

##################################################################################
# STEP 3: UPDATE MS MHD DATASET METADATA (ADD ASSIGNED MHD ACCESSION)
##################################################################################

```

### Step 4: MHD Dataset Announcement Integration

After a dataset is public or there is a new revision for the dataset, repositories will generate MHD common data file, create an MHD announcement file and share the announcement file with MetabolomicsHub.

MHD common data file can be generated using repository specific convertors. After MHD file creation, repositories SHOULD validate its content to ensure alignment of MHD specification requirements.

If there a valid MHD common data file, the following commands can be used to create annoucement file and share with MetabolomicsHub.

Create MHD Announcement File and make an announcement for MHD datasets

```bash
##################################################################################
# STEP 1: CREATE MHD COMMON DATA FILE USING REPOSITORY SPECIFIC CONVERTOR
#         (USE CONVERTOR CLI TOOL OR API TO CREATE IT)
##################################################################################

##################################################################################
# STEP 2: CREATE AND VALIDATE MHD FILES
#         MHD COMMON DATA FILE & MHD ANNOUNCEMENT FILE
##################################################################################
# You have a dataset with repository id ST912345 and MHD accession ST912345.
# MHD common data file is on current path

mhd-cli validate mhd ./ST912345.mhd.json --mhd-id MHD000021

# target-mhd-common-data-file-url MUST be accessible after a study is public
mhd-cli create announcement --mhd-id MHD000021 \
    --mhd-common-data-file-path ./ST912345.mhd.json \
    --output-dir . \
    --output-filename ST912345.announcement.json \
    --target-mhd-common-data-file-url 'https://www.metabolomicsworkbench.org/data/mhd.php?STUDY_ID=ST004212'

mhd-cli validate announcement ./ST912345.announcement.json

##################################################################################
# STEP 3: MAKE STUDY PUBLIC AND HOST MHD COMMON DATA FILE ON INTERNET
##################################################################################
# ENSURE URL defined with target-mhd-common-data-file-url is accessible
# and downloadable as JSON file


##################################################################################
# STEP 4: ANNOUNCE PUBLIC DATASET
##################################################################################
export PRODUCTION_MHD_SERVER_URL="https://www.metabolomicshub.org/api/submission"
export TEST_MHD_SERVER_URL="https://www.metabolomicshub.org/test/api/submission"

# Announce an MHD announcement file for MHD studies
mhd-cli client announce \
    --dataset-repository-identifier ST912345 \
    --api-token-file-path mhd-test-keys/api-token-test-2026-09.txt \
    --mhd-server-url $TEST_MHD_SERVER_URL \
    --mhd-id MHD000021 \
    --announcement-reason 'initial publication' \
    --announcement-file-path ST912345.announcement.json
```

Create MHD Announcement File and make an announcement for Legacy datasets

```bash

##################################################################################
# STEP 1: (LEGACY DATASET) CREATE MHD COMMON DATA FILE USING REPOSITORY CONVERTOR
##################################################################################

##################################################################################
# STEP 2: (LEGACY DATASET) CREATE AND VALIDATE MHD FILES
##################################################################################
# You have a legacy dataset with repository id ST004083
# MHD common data file for the legacy dataset is on current path
mhd-cli validate mhd ./ST004083.mhd.json

# Target URL MUST be accessible after a study is public
mhd-cli create announcement --mhd-id ST004083 \
    --mhd-common-data-file-path ./ST004083.mhd.json \
    --output-dir . \
    --output-filename ST004083.announcement.json \
    --target-mhd-common-data-file-url 'https://www.metabolomicsworkbench.org/data/mhd.php?STUDY_ID=ST004212'

mhd-cli validate announcement ./ST004083.announcement.json

##################################################################################
# STEP 3: MAKE STUDY PUBLIC AND HOST MHD COMMON DATA FILE ON INTERNET
##################################################################################
# ENSURE URL defined with target-mhd-common-data-file-url is accessible
# and downloadable as JSON file


##################################################################################
# STEP 4: (LEGACY DATASET) ANNOUNCE PUBLIC DATASET
##################################################################################
# Announce an MHD announcement file for legacy studies
mhd-cli client announce \
    --dataset-repository-identifier ST004083 \
    --api-token-file-path mhd-test-keys/api-token-test-2026-09.txt \
    --mhd-server-url $TEST_MHD_SERVER_URL \
    --mhd-id ST004083 \
    --announcement-reason 'updated version' \
    --announcement-file-path ST004083.announcement.json

```

## Development Environment

Development environment for linux or mac

```bash

# install python package manager uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# add $HOME/.local/bin to your PATH, either restart your shell or run
export PATH=$HOME/.local/bin:$PATH

# install git from https://git-scm.com/downloads
# Linux command
apt update; apt install git -y

# Mac command
# brew install git

# clone project from github
git clone https://github.com/MetabolomicsHub/mhd_model.git

cd mhd-model

# install python if it is not installed
uv python install 3.12

# install python dependencies
uv sync

# install pre-commit to check repository integrity and format checking
uv run pre-commit

# open your IDE (vscode, pycharm, etc.) and set python interpreter as .venv/bin/python

```

## Example API Usage

```python
from mhd_model.mhd_client import MhdClient, MhdClientError

mhd_webservice_base_url = "https://www.metabolomicshub.org/test/api/submission"
api_token = "<your-api-token>"


def get_new_mhd_accession_example():
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_token)

    try:
        accession = mhd_client.get_new_mhd_accession(
            dataset_repository_identifier="MTBLS1234567", accession_type="mhd"
        )
        print("Accession: %s" % accession)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


def get_new_test_mhd_accession_example():
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_token)

    try:
        accession = mhd_client.get_new_mhd_accession(
            dataset_repository_identifier="MTBLS4444", accession_type="test"
        )
        print("Accession: %s" % accession)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


def submit_legacy_dataset_example():
    announcement_file_path = "MTBLS9876543.announcement.json"
    dataset_repository_id = "MTBLS9876543"
    announcement_reason = "Initial revision"
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_token)

    try:
        revision: SubmittedRevision = mhd_client.submit_announcement_file(
            dataset_repository_id=dataset_repository_id,
            mhd_id=None,
            file_path=announcement_file_path,
            announcement_reason=announcement_reason,
        )
        print("Revision: %s" % revision.revision)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)


def submit_mhd_dataset_example():
    announcement_file_path = "MTBLS9876543.announcement.json"
    mhd_id = "MHD0000001"
    dataset_repository_id = "MTBLS22222"
    announcement_reason = "Initial revision"
    mhd_client: MhdClient = MhdClient(mhd_webservice_base_url, api_token)

    try:
        revision: SubmittedRevision = mhd_client.submit_announcement_file(
            dataset_repository_id=dataset_repository_id,
            mhd_id=mhd_id,
            file_path=announcement_file_path,
            announcement_reason=announcement_reason,
        )
        print("Revision: %s" % revision.revision)
    except MhdClientError as ex:
        print("Error: %s" % ex.message)
```
