import sys

from ..api import plot

import fuc
import pysam

description = f"""
Plot allele fraction profile from VcfFrame[Imported].
"""

def create_parser(subparsers):
    parser = fuc.api.common._add_parser(
        subparsers,
        fuc.api.common._script_name(),
        help='Plot allele fraction profile with VCF data.',
        description=description,
    )
    parser.add_argument(
        'imported_variants',
        metavar='imported-variants',
        help='Archive file with the semantic type VcfFrame[Imported].'
    )
    parser.add_argument(
        '--path',
        metavar='PATH',
        help='Create plots in this directory.'
    )
    parser.add_argument(
        '--samples',
        metavar='TEXT',
        nargs='+',
        help='Create plots only for these samples.'
    )
    parser.add_argument(
        '--fontsize',
        metavar='FLOAT',
        type=float,
        default=25,
        help='Text fontsize (default: 25).'
    )

def main(args):
    plot.plot_vcf_allele_fraction(
        args.imported_variants, path=args.path, samples=args.samples,
        fontsize=args.fontsize
    )
