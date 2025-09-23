import click

from mhd_model.convertors.sdrf.mhd2sdrf import create_sdrf_files


@click.command(name="sdrf", no_args_is_help=True)
@click.option(
    "--output-dir",
    default="outputs",
    help="Output directory for SDRF files",
)
@click.option(
    "--output-filename",
    default=None,
    help="SDRF filename (e.g., MHD000001_assay1.sdrf.tsv)",
)
@click.option(
    "--assay-name",
    default=None,
    help="Name of assay. If it is not defined, SDRF files will be created for all assays.",
)
@click.argument("mhd_study_id")
@click.argument("mhd_model_file_path")
def create_sdrf_file_task(
    mhd_study_id: str,
    mhd_model_file_path: str,
    assay_name: None | str,
    output_dir: None | str,
    output_filename: None | str,
):
    """Create SDRF file from MHD data model file.

    Args:

    mhd_study_id (str): MHD study identifier

    mhd_model_file_path (str): MHD data model path

    assay_name (str): Name of assay.
    If it is not defined, SDRF files will be created for all assays

    output_dir (str): Output directory of SDRF files.

    output_filename (str): Name of SDRF file. It is applicable if
    """
    try:
        sdrf_files = create_sdrf_files(
            mhd_model_file_path,
            output_dir,
            assay_name=assay_name,
            sdrf_output_filename=output_filename,
        )
        if sdrf_files:
            click.echo(f"{mhd_study_id}: {len(sdrf_files)} SDRF files created.")
        else:
            click.echo(f"There is no SDRF file for {mhd_study_id}.")
            exit(1)
    except Exception as ex:
        click.echo(f"{mhd_study_id} SDRF file creation failed. {str(ex)}")
        exit(1)
