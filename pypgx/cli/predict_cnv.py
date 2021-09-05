import sys

from ..api import utils

import fuc
import pysam

description = f"""
This command will predict CNV based on copy number data.

Usage examples:
  $ pypgx {fuc.api.common._script_name()} input.zip output.zip
"""

def create_parser(subparsers):
    parser = fuc.api.common._add_parser(
        subparsers,
        fuc.api.common._script_name(),
        help='Predict CNV based on copy number data.',
        description=description,
    )
    parser.add_argument(
        'input',
        help='Result file with the semantic type CovFrame[CopyNumber].'
    )
    parser.add_argument(
        'output',
        help='Result file with the semantic type TSV[CNVCalls].'
    )

def main(args):
    result = utils.predict_cnv(args.input)
    result.to_file(args.output)
