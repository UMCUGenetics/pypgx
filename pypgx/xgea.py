import configparser
from os import mkdir
from os.path import realpath

from .sgea import sgea
from .common import logging, LINE_BREAK1, is_chr, get_gene_table

logger = logging.getLogger(__name__)

def xgea(conf: str) -> None:
    """Run per-project genotyping for multiple genes with SGE (2).

    This command runs the per-project genotyping pipeline by submitting 
    jobs to the Sun Grid Engine (SGE) cluster. The main difference between
    ``xgea`` and ``xgep`` is that the former uses Genome Analysis Tool 
    Kit (GATK) v4 while the latter uses GATK v3.

    Args:
        conf (str): Configuration file.

    .. note::

        SGE, Stargazer, and GATK must be pre-installed.

    This is what a typical configuration file for ``xgea`` looks like:

        .. code-block:: python

            # File: example_conf.txt
            # Do not make any changes to this section.
            [DEFAULT]
            mapping_quality = 1
            output_prefix = pypgx
            control_gene = NONE
            qsub_options = NONE
            target_genes = ALL

            # Make any necessary changes to this section.
            [USER]
            fasta_file = reference.fa
            manifest_file = manifest.txt
            project_path = /path/to/project/
            genome_build = hg19
            data_type = wgs
            dbsnp_file = dbsnp.vcf
            control_gene = vdr
            target_genes = cyp2b6, cyp2d6

    This table summarizes the configuration parameters specific to ``xgea``:

        .. list-table::
           :widths: 25 75
           :header-rows: 1

           * - Parameter
             - Summary
           * - control_gene
             - Control gene or region.
           * - data_type
             - Data type (wgs, ts, chip).
           * - dbsnp_file
             - dbSNP VCF file.
           * - fasta_file
             - Reference FASTA file.
           * - genome_build
             - Genome build (hg19, hg38).
           * - manifest_file
             - Manifest file.
           * - mapping_quality
             - Minimum mapping quality for read depth.
           * - output_prefix
             - Output prefix.
           * - project_path
             - Output project directory.
           * - qsub_options
             - Options for qsub command.
           * - target_genes
             - Target genes.
    """
    gene_table = get_gene_table()

    # Log the configuration data.
    logger.info(LINE_BREAK1)
    logger.info("Configureation:")
    with open(conf) as f:
        for line in f:
            logger.info("    " + line.strip())
    logger.info(LINE_BREAK1)

    # Read the configuration file.
    config = configparser.ConfigParser()
    config.read(conf)

    # Parse the configuration data.
    project_path = realpath(config["USER"]["project_path"])
    manifest_file = realpath(config["USER"]["manifest_file"])
    dbsnp_file = realpath(config["USER"]["dbsnp_file"])
    fasta_file = realpath(config["USER"]["fasta_file"])
    mapping_quality = config["USER"]["mapping_quality"]
    output_prefix = config["USER"]["output_prefix"]
    target_genes = config["USER"]["target_genes"]
    control_gene = config["USER"]["control_gene"]
    data_type = config["USER"]["data_type"]
    genome_build = config["USER"]["genome_build"]
    qsub_options = config["USER"]["qsub_options"]

    t = [k for k, v in gene_table.items() if v["type"] == "target"]
    
    if target_genes == "ALL":
        select_genes = t
    else:
        select_genes = []
        for gene in target_genes.split(","):
            select_genes.append(gene.strip().lower())
        for gene in select_genes:
            if gene not in t:
                raise ValueError(f"Unrecognized target gene found: {gene}")

    # Make the project directories.
    mkdir(project_path)

    with open(f"{project_path}/example-qsub.sh", "w") as f:
        for select_gene in select_genes:
            f.write(f"sh {project_path}/{select_gene}/example-qsub.sh\n")


    for select_gene in select_genes:
        p = f"{project_path}/{select_gene}"

        s = (
            "# Do not make any changes to this section.\n"
            "[DEFAULT]\n"
            "mapping_quality = 1\n"
            "output_prefix = pypgx\n"
            "control_gene = NONE\n"
            "qsub_options = NONE\n"
            "\n"
            "# Make any necessary changes to this section.\n"
            "[USER]\n"
            f"fasta_file = {fasta_file}\n"
            f"manifest_file = {manifest_file}\n"
            f"project_path = {p}\n"
            f"target_gene = {select_gene}\n"
            f"control_gene = {control_gene}\n"
            f"genome_build = {genome_build}\n"
            f"data_type = {data_type}\n"
            f"dbsnp_file = {dbsnp_file}\n"
            f"qsub_options = {qsub_options}\n"
        )

        with open(f"{project_path}/conf-{select_gene}.txt", "w") as f:
            f.write(s)

        sgea(f"{project_path}/conf-{select_gene}.txt")