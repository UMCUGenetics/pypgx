import pydoc
import subprocess

import pypgx
import pypgx.api
from pypgx.api import utils
from pypgx.cli import commands

submodules = ['genotype', 'pipeline', 'plot', 'utils']

credit = """
..
   This file was automatically generated by docs/create.py.
"""

pypgx_help = subprocess.run(['pypgx', '-h'], capture_output=True, text=True, check=True).stdout
pypgx_help = '\n'.join(['   ' + x for x in pypgx_help.splitlines()])

submodule_help = ''

for submodule in submodules:
    description = pydoc.getdoc(getattr(pypgx.api, submodule)).split('\n\n')[0].replace('\n', ' ')
    submodule_help += f'- **{submodule}** : {description}\n'

d = dict(credit=credit, pypgx_help=pypgx_help, submodule_help=submodule_help)

# -- README.rst ---------------------------------------------------------------

readme = """
{credit}
README
******

.. image:: https://badge.fury.io/py/pypgx.svg
    :target: https://badge.fury.io/py/pypgx

.. image:: https://readthedocs.org/projects/pypgx/badge/?version=latest
    :target: https://pypgx.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Introduction
============

The main purpose of the PyPGx package is to provide a unified platform for pharmacogenomics (PGx) research.

The package is written in Python, and supports both command line interface (CLI) and application programming interface (API) whose documentations are available at the `Read the Docs <https://pypgx.readthedocs.io/en/latest/>`_.

Your contributions (e.g. feature ideas, pull requests) are most welcome.

| Author: Seung-been "Steven" Lee
| Email: sbstevenlee@gmail.com
| License: MIT License

Installation
============

The following packages are required to run PyPGx:

.. parsed-literal::

   fuc
   scikit-learn

There are various ways you can install PyPGx. The recommended way is via conda (`Anaconda <https://www.anaconda.com/>`__):

.. code-block:: text

   $ conda install -c bioconda pypgx

Above will automatically download and install all the dependencies as well. Alternatively, you can use pip (`PyPI <https://pypi.org/>`__) to install PyPGx and all of its dependencies:

.. code-block:: text

   $ pip install pypgx

Finally, you can clone the GitHub repository and then install PyPGx locally:

.. code-block:: text

   $ git clone https://github.com/sbslee/pypgx
   $ cd pypgx
   $ pip install .

The nice thing about this approach is that you will have access to development versions that are not available in Anaconda or PyPI. For example, you can access a development branch with the ``git checkout`` command. When you do this, please make sure your environment already has all the dependencies installed.

Archive file, semantic type, and metadata
=========================================

In order to efficiently store and transfer data, PyPGx uses the ZIP archive file format (``.zip``) which supports lossless data compression. Each archive file created by PyPGx has a metadata file (``metadata.txt``) and a data file (e.g. ``data.tsv``, ``data.vcf``). A metadata file contains important information about the data file within the same archive, which is expressed as pairs of ``=``-separated keys and values (e.g. ``Assembly=GRCh37``):

.. list-table::
    :widths: 20 40 40
    :header-rows: 1

    * - Metadata
      - Description
      - Examples
    * - ``Assembly``
      - Reference genome assembly.
      - ``GRCh37``, ``GRCh38``
    * - ``Control``
      - Control gene.
      - ``VDR``, ``chr1:10000-20000``
    * - ``Gene``
      - Target gene.
      - ``CYP2D6``, ``GSTT1``
    * - ``Platform``
      - NGS platform.
      - ``WGS``, ``Targeted``
    * - ``Program``
      - Name of the phasing program.
      - ``Beagle``
    * - ``Samples``
      - Samples used for inter-sample normalization.
      - ``NA07000,NA10854,NA11993``
    * - ``SemanticType``
      - Semantic type of the archive.
      - ``CovFrame[CopyNumber]``, ``Model[CNV]``

Notably, all archive files have defined semantic types, which allows us to ensure that the data that is passed to a PyPGx command (CLI) or method (API) is meaningful for the operation that will be performed. Below is a list of currently defined semantic types:

- ``CovFrame[CopyNumber]``
    * CovFrame for storing target gene's per-base copy number which is computed from read depth with control statistics.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Platform``, ``Control``, ``Samples``.
- ``CovFrame[ReadDepth]``
    * CovFrame for storing target gene's per-base read depth which is computed from BAM files.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Platform``.
- ``Model[CNV]``
    * Model for calling CNV in target gene.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Control``.
- ``SampleTable[Alleles]``
    * TSV file for storing target gene's candidate star alleles for each sample.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Program``.
- ``SampleTable[CNVCalls]``
    * TSV file for storing target gene's CNV call for each sample.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Control``.
- ``SampleTable[Genotypes]``
    * TSV file for storing target gene's genotype call for each sample.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``.
- ``SampleTable[Results]``
    * TSV file for storing various results for each sample.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``.
- ``SampleTable[Statistcs]``
    * TSV file for storing control gene's various statistics on read depth for each sample. Used for converting target gene's read depth to copy number.
    * Requires following metadata: ``Control``, ``Assembly``, ``SemanticType``, ``Platform``.
- ``VcfFrame[Consolidated]``
    * VcfFrame for storing target gene's consolidated variant data.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Program``.
- ``VcfFrame[Imported]``
    * VcfFrame for storing target gene's raw variant data.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``.
- ``VcfFrame[Phased]``
    * VcfFrame for storing target gene's phased variant data.
    * Requires following metadata: ``Gene``, ``Assembly``, ``SemanticType``, ``Program``.

Getting help
============
For detailed documentations on the CLI and API, please refer to the `Read the Docs <https://pypgx.readthedocs.io/en/latest/>`_.

For getting help on the CLI:

.. code-block:: text

   $ pypgx -h

{pypgx_help}

For getting help on a specific command (e.g. call-genotypes):

.. code-block:: text

   $ pypgx call-genotypes -h

Below is the list of submodules available in the API:

{submodule_help}

For getting help on a specific submodule (e.g. utils):

.. code:: python3

   >>> from pypgx.api import utils
   >>> help(utils)

CLI examples
============

Run NGS pipeline for CYP2D6:

.. code-block:: text

   $ pypgx run-ngs-pipeline \\
   CYP2D6 \\
   CYP2D6-pipeline \\
   --vcf input.vcf \\
   --panel ref.vcf \\
   --tsv input.tsv \\
   --control-statistics control-statistics-VDR.zip

API examples
============

Predict phenotype based on two haplotype calls:

.. code:: python3

    >>> import pypgx
    >>> pypgx.predict_phenotype('CYP2D6', '*4', '*5')   # Both alleles have no function
    'Poor Metabolizer'
    >>> pypgx.predict_phenotype('CYP2D6', '*5', '*4')   # The order of alleles does not matter
    'Poor Metabolizer'
    >>> pypgx.predict_phenotype('CYP2D6', '*1', '*22')  # *22 has uncertain function
    'Indeterminate'
    >>> pypgx.predict_phenotype('CYP2D6', '*1', '*1x2') # Gene duplication
    'Ultrarapid Metabolizer'
    >>> pypgx.predict_phenotype('CYP2B6', '*1', '*4')   # *4 has increased function
    'Rapid Metabolizer'
""".format(**d)

readme_file = f'{utils.PROGRAM_PATH}/README.rst'

with open(readme_file, 'w') as f:
    f.write(readme.lstrip())

# -- cli.rst -----------------------------------------------------------------

cli = """
{credit}

CLI
***

Introduction
============

This section describes the command line interface (CLI) for PyPGx.

For getting help on the CLI:

.. code-block:: text

   $ pypgx -h

{pypgx_help}

For getting help on a specific command (e.g. call-genotypes):

.. code-block:: text

   $ pypgx call-genotypes -h

""".format(**d)

for command in commands:
    s = f'{command}\n'
    s += '=' * (len(s)-1) + '\n'
    s += '\n'
    s += '.. code-block:: text\n'
    s += '\n'
    s += f'   $ pypgx {command} -h\n'
    command_help = subprocess.run(['pypgx', command, '-h'], capture_output=True, text=True, check=True).stdout
    command_help = '\n'.join(['   ' + x for x in command_help.splitlines()])
    s += command_help + '\n'
    s += '\n'
    cli += s

cli_file = f'{utils.PROGRAM_PATH}/docs/cli.rst'

with open(cli_file, 'w') as f:
    f.write(cli.lstrip())

# -- api.rst -----------------------------------------------------------------

api_file = f'{utils.PROGRAM_PATH}/docs/api.rst'

api = """
{credit}
API
***

Introduction
============

This section describes the application programming interface (API) for PyPGx.

Below is the list of submodules available in the API:

{submodule_help}

For getting help on a specific submodule (e.g. utils):

.. code:: python3

   from pypgx.api import utils
   help(utils)

""".format(**d)

for submodule in submodules:
    s = f'pypgx.{submodule}\n'
    s += '=' * (len(s)-1) + '\n'
    s += '\n'
    s += f'.. automodule:: pypgx.api.{submodule}\n'
    s += '   :members:\n'
    s += '\n'
    api += s

with open(api_file, 'w') as f:
    f.write(api.lstrip())
