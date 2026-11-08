""" 
command line wrapper to run snakefile

Author: Jimmy Capecci
"""

# import libraries
import argparse
from typing import Any
import subprocess
import shutil


class InputParamsError(Exception):
    """Will raise error if input param.txt file is invalid"""
    pass


def process_line(line: str, list_to_extend: list[Any]):
    """Parse a parameter line and extend a list with its values.

    Handles inconsistent whitespace around delimiters and values.

    :param line: Parameter line from the input text file.
    :param list_to_extend: List to extend with the parsed values.

    >>> seeds_list = []
    >>> process_line('seeds: 2, 3,4', seeds_list)
    >>> print(seeds_list)
    ['2', '3', '4']
    """

    # Splits once at colon
    _, value = line.split(':', 1)

    # Grab seeds regardless of surrounding spaces
    list_to_extend.extend(x.strip() for x in value.split(','))


def main():

    # set up parser with arguements
    parser = argparse.ArgumentParser(description='Runs benchmarking pipeline')
    parser.add_argument('-i', '--input', help='input parameters text file', required=True)


    # parse arguements
    args = parser.parse_args()

    # Create seeds, chromosome and coverages lists
    seeds = []
    chromosomes = []
    coverages = []

    with open(args.input) as f:
        for line in f:
            line = line.strip()

            # if empty line skip
            if not line:
                continue

            # Process seeds and add to list
            if line.lower().startswith('seed'):
                process_line(line, seeds)

            # Process coverages and add to list
            elif line.lower().startswith('coverages'):
                process_line(line, coverages)

            # Process chromosomes and add to list
            elif line.lower().startswith('chromosomes'):
                process_line(line, chromosomes)

            # Raise error if input file is wrong
            else:
                raise InputParamsError(
                "Invalid input file txt format. Expected the following format:\n"
                "coverages: 10, 20, 30\n"
                "seed: 4, 5, 6\n"
                "chromosomes: chr20, chr21\n\n"
                "For more information, see the input format documentation:\n"
                "https://github.com/jcapecci09/variant-caller-benchmark/blob/main/README.md"
                )

    # use snakemake pipeline to benchmark tools at 
    # different replications (seeds), sequencing coverages, and chromosomes
    for chromosome in chromosomes:
        for coverage in coverages:
            for seed in seeds:

                # set output path
                output = f'coverage{coverage}_seed{seed}'

                # run pipeline
                subprocess.run([
                    'snakemake',
                    '--cores', '4',
                    '--config',
                    f'coverage={coverage}',
                    f'seed={seed}',
                    f'chromosome={chromosome}',
                    f'folder={output}',
                ], check=True)

        # Remove chromosome data to save memory
        shutil.rmtree(f"Data/{chromosome}")


if __name__ == '__main__':
    main()
    