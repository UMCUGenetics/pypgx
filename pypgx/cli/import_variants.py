import sys

from ..api import utils

import fuc
import pysam

description = f"""
Import SNV and indel data for target gene.

The command will slice the input VCF for the target gene to create an archive
file with the semantic type VcfFrame[Imported] or VcfFrame[Consolidated].
"""

def create_parser(subparsers):
    parser = fuc.api.common._add_parser(
        subparsers,
        fuc.api.common._script_name(),
        description=description,
        help='Import SNV and indel data for target gene.',
    )
    parser.add_argument(
        'gene',
        help='Target gene.'
    )
    parser.add_argument(
        'vcf',
        help='Input VCF file must be already BGZF compressed (.gz) \n'
             'and indexed (.tbi) to allow random access.'
    )
    parser.add_argument(
        'imported_variants',
        metavar='imported-variants',
        help='Archive file with the semantic type \n'
             'VcfFrame[Imported] or VcfFrame[Consolidated].'
    )
    parser.add_argument(
        '--assembly',
        metavar='TEXT',
        default='GRCh37',
        help="Reference genome assembly (default: 'GRCh37') \n"
             "(choices: 'GRCh37', 'GRCh38')."
    )
    parser.add_argument(
        '--platform',
        metavar='TEXT',
        default='WGS',
        choices=['WGS', 'Targeted', 'Chip', 'LongRead'],
        help="Genotyping platform used (default: 'WGS') (choices: \n"
             "'WGS', 'Targeted', 'Chip', 'LongRead'). When the \n"
             "platform is 'WGS', 'Targeted', or 'Chip', the command \n"
             "will assess whether every genotype call in the sliced \n"
             "VCF is haplotype phased (e.g. '0|1'). If the sliced \n"
             "VCF is fully phased, the command will return \n"
             "VcfFrame[Consolidated] or otherwise \n"
             "VcfFrame[Imported]. When the platform is 'LongRead', \n"
             "the command will return VcfFrame[Consolidated] after \n"
             "applying the phase-extension algorithm to estimate \n"
             "haplotype phase of any variants that could not be \n"
             "resolved by read-backed phasing."
    )
    parser.add_argument(
        '--samples',
        metavar='TEXT',
        nargs='+',
        help='Specify which samples should be included for analysis \n'
             'by providing a text file (.txt, .tsv, .csv, or .list) \n'
             'containing one sample per line. Alternatively, you \n'
             'can provide a list of samples.'
    )
    parser.add_argument(
        '--exclude',
        action='store_true',
        help='Exclude specified samples.'
    )

def main(args):
    archive = utils.import_variants(
        args.gene, args.vcf, assembly=args.assembly, platform=args.platform,
        samples=args.samples, exclude=args.exclude
    )
    archive.to_file(args.imported_variants)
