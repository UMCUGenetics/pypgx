import configparser
from os import mkdir
from os.path import realpath
from .bam2vcf2 import bam2vcf2
from .common import logging, sm_tag, LINE_BREAK1, is_chr, get_gene_table, randstr

logger = logging.getLogger(__name__)

def _write_bam2gdf_shell(
        genome_build,
        target_gene,
        control_gene,
        bam_files,
        gdf_file,
        shell_file
    ):
    s = (
        "pypgx bam2gdf \\\n"
        f"  {genome_build} \\\n"
        f"  {target_gene} \\\n"
        f"  {control_gene} \\\n"
        f"  {gdf_file} \\\n"
    )

    for seq_id in bam_files:
        s += f"  {bam_files[seq_id][0]} \\\n"

    with open(shell_file, "w") as f:
        f.write(s)

def _write_bam2vcf_shell(
        fasta_file,
        target_gene,
        project_path,
        genome_build,
        bam_files
    ):
    s = (
        "pypgx bam2vcf \\\n"
        f"  bcftools \\\n"
        f"  {fasta_file} \\\n"
        f"  {target_gene} \\\n"
        f"  {project_path}/pypgx.vcf \\\n"
        f"  {genome_build} \\\n"
    )

    for seq_id in bam_files:
        s += f"  {bam_files[seq_id][0]} \\\n"

    with open(f"{project_path}/shell/bam2vcf.sh", "w") as f:
        f.write(s)

def _write_bam2vcf2_shell(
        fasta_file,
        manifest_file,
        project_path,
        target_gene,
        genome_build,
        qsub_options,
        java_options,
        dbsnp_file
    ):
    s = (
        "# Do not make any changes to this section.\n"
        "[DEFAULT]\n"
        "qsub_options = NONE\n"
        "java_options = NONE\n"
        "dbsnp_file = NONE\n"
        "\n"
        "# Make any necessary changes to this section.\n"
        "[USER]\n"
        f"fasta_file = {fasta_file}\n"
        f"manifest_file = {manifest_file}\n"
        f"project_path = {project_path}/bam2vcf2\n"
        f"target_gene = {target_gene}\n"
        f"genome_build = {genome_build}\n"
        f"qsub_options = {qsub_options}\n"
        f"java_options = {java_options}\n"
        f"dbsnp_file = {dbsnp_file}\n"
    )

    with open(f"{project_path}/conf.txt", "w") as f:
        f.write(s)

    bam2vcf2(f"{project_path}/conf.txt")

def _write_stargazer_shell(
        snp_caller,
        data_type,
        genome_build,
        target_gene,
        project_path,
        control_gene
    ):

    if snp_caller == "bcftools":
        vcf_file = "$p/pypgx.vcf"
    else:
        vcf_file = "$p/bam2vcf2/bam2vcf2.vcf"

    s = (
        f"p={project_path}\n"
        "\n"
        "stargazer \\\n"
        f"  {data_type} \\\n"
        f"  {genome_build} \\\n"
        f"  {target_gene} \\\n"
        f"  {vcf_file} \\\n"
        "  $p/stargazer \\\n"
    )

    if control_gene != "NONE":
        s += (
            f"  --cg {control_gene} \\\n"
            f"  --gdf $p/pypgx.gdf \\\n"
        )

    with open(f"{project_path}/shell/stargazer.sh", "w") as f:
        f.write(s)

def _write_qsub_shell(
        snp_caller,
        qsub_options,
        control_gene,
        project_path
    ):
    q = "qsub -e $p/log -o $p/log"

    if qsub_options != "NONE":
        q += f" {qsub_options}"

    s = (
        "#!/bin/bash\n"
        "\n"
        f"p={project_path}\n"
        f"j={randstr()}\n"
        "\n"
    )

    if control_gene != "NONE":
        s += f"{q} -N $j-bam2gdf $p/shell/bam2gdf.sh\n"

    if snp_caller == "bcftools":
        s += f"{q} -N $j-bam2vcf $p/shell/bam2vcf.sh\n"

        if control_gene == "NONE":
            s += f"{q} -hold_jid $j-bam2vcf -N $j-stargazer $p/shell/stargazer.sh\n"
        else:
            s += f"{q} -hold_jid $j-bam2gdf,$j-bam2vcf -N $j-stargazer $p/shell/stargazer.sh\n"

    else:
        with open(f"{project_path}/bam2vcf2/example-qsub.sh") as f:
            for line in f:
                if line.startswith("qsub"):
                    s += line.replace("$p", "$p/bam2vcf2")

        if control_gene == "NONE":
            s += f"{q} -hold_jid $j-post-hc -N $j-stargazer $p/shell/stargazer.sh\n"
        else:
            s += f"{q} -hold_jid $j-bam2gdf,$j-post-hc -N $j-stargazer $p/shell/stargazer.sh\n"

    with open(f"{project_path}/example-qsub.sh", "w") as f:
        f.write(s)

def sgep(conf: str) -> None:
    """Convert BAM files to a genotype file [SGE].

    This command runs the per-project genotyping pipeline by submitting 
    jobs to the Sun Grid Engine (SGE) cluster.

    Args:
        conf (str): Configuration file.

    .. warning::

        BCFtools, SGE and Stargazer must be pre-installed.

    This is what a typical configuration file for ``sgep`` looks like:

        .. code-block:: python

            # File: example_conf.txt
            # To execute:
            #   $ pypgx sgep example_conf.txt
            #   $ sh ./myproject/example-qsub.sh

            # Do not make any changes to this section.
            [DEFAULT]
            control_gene = NONE
            qsub_options = NONE

            # Make any necessary changes to this section.
            [USER]
            fasta_file = reference.fa
            manifest_file = manifest.txt
            project_path = ./myproject
            target_gene = cyp2d6
            genome_build = hg19
            data_type = wgs
            control_gene = vdr
            snp_caller = gatk
            qsub_options = -V -l mem_requested=10G
            snp_caller = gatk

    This table summarizes the configuration parameters specific to ``sgep``:

        .. list-table::
           :widths: 25 75
           :header-rows: 1

           * - Parameter
             - Summary
           * - control_gene
             - Control gene or region.
           * - data_type
             - Data type (wgs, ts, chip).
           * - fasta_file
             - Reference FASTA file.
           * - genome_build
             - Genome build (hg19, hg38).
           * - manifest_file
             - Manifest file.
           * - project_path
             - Output project directory.
           * - qsub_options
             - Options for qsub command.
           * - snp_caller
             - SNP caller (‘gatk’ or ‘bcftools’).
           * - target_gene
             - Target gene.
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
    fasta_file = realpath(config["USER"]["fasta_file"])
    genome_build = config["USER"]["genome_build"]
    target_gene = config["USER"]["target_gene"]
    control_gene = config["USER"]["control_gene"]
    data_type = config["USER"]["data_type"]
    qsub_options = config["USER"]["qsub_options"]
    snp_caller = config["USER"]["snp_caller"]
    java_options = config["USER"]["java_options"]
    dbsnp_file = config["USER"]["dbsnp_file"]

    # Read the manifest file.
    bam_files = {}
    with open(manifest_file) as f:
        header = next(f).strip().split("\t")
        i1 = header.index("sample_id")
        i2 = header.index("bam")
        for line in f:
            fields = line.strip().split("\t")
            sample_id = fields[i1]
            bam = fields[i2]
            seq_id = sm_tag(bam)
            bam_files[seq_id] = (bam, sample_id)

    # Sort the samples by name since GATK does this.
    bam_files = {k: v for k, v in sorted(bam_files.items(), key=lambda item: item[0])}

    # Log the number of samples.
    logger.info(f"Number of samples: {len(bam_files)}")

    # Make the project directories.
    mkdir(project_path)
    mkdir(f"{project_path}/shell")
    mkdir(f"{project_path}/log")

    t = [is_chr(v[0]) for k, v in bam_files.items()]
    if all(t):
        chr_str = "chr"
    elif not any(t):
        chr_str = ""
    else:
        raise ValueError("Mixed types of SN tags found.")

    target_region = gene_table[target_gene][f"{genome_build}_region"].replace("chr", "")

    if control_gene != "NONE":
        _write_bam2gdf_shell(
            genome_build,
            target_gene,
            control_gene,
            bam_files,
            f"{project_path}/pypgx.gdf",
            f"{project_path}/shell/bam2gdf.sh"
        )

    if snp_caller == "bcftools":
        _write_bam2vcf_shell(
            fasta_file,
            target_gene,
            project_path,
            genome_build,
            bam_files
        )

    elif snp_caller == "gatk":
        _write_bam2vcf2_shell(
            fasta_file,
            manifest_file,
            project_path,
            target_gene,
            genome_build,
            qsub_options,
            java_options,
            dbsnp_file
        )

    else:
        raise ValueError(f"Incorrect SNP caller: {snp_caller}")

    _write_stargazer_shell(
        snp_caller,
        data_type,
        genome_build,
        target_gene,
        project_path,
        control_gene
    )

    _write_qsub_shell(
        snp_caller,
        qsub_options,
        control_gene,
        project_path
    )
