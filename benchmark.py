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


def process_line(line: str) -> list[Any]:
    """Parse a parameter line and return list

    Handles inconsistent whitespace around delimiters and values.

    :param line: Parameter line from the input text file.
    :return: List of values

    >>> seeds_list = process_line('seeds: 2, 3,4')
    >>> print(seeds_list)
    ['2', '3', '4']
    """

    # Splits once at colon
    _, value = line.split(':', 1)

    # Grab seeds regardless of surrounding spaces
    return [x.strip() for x in value.split(',')]


def process_errors(line: str) -> list[list[Any]]:
    """Similar to process_line() but process error pairs 
    instead.

    :param line: error pair to parse
    :return: List of list of error pairs

    >>> errors_list = process_errors([errors: 0.005:0.01,0.005:0.02])
    >>> print(errors_list)
    [[0.005, 0.01], [0.005, 0.02]]
    """
    # Splits once at colon
    _, value = line.split(':', 1)

    # split into error pairs
    line_split = [x.strip() for x in value.split(',')]

    # Split error pairs into list
    line_split2 = [errors.split(':') for errors in line_split]

    return line_split2


def main():

    # set up parser with arguements
    parser = argparse.ArgumentParser(description='Runs benchmarking pipeline')
    parser.add_argument('-i', '--input', help='input parameters text file', required=True)
    parser.add_argument('-a', '--aligner', help='Choose aligned minimap2 or bwa', required=False, default='minimap2')

    # parse arguements
    args = parser.parse_args()

    # Parse parameters .txt file to extracts elements
    with open(args.input) as f:
        for line in f:
            line = line.strip()

            # if empty line skip
            if not line:
                continue

            # Process seeds and add to list
            if line.lower().startswith('seed'):
                seeds = process_line(line)

            # Process coverages and add to list
            elif line.lower().startswith('coverages'):
                coverages = process_line(line)

            # Process chromosomes and add to list
            elif line.lower().startswith('chromosomes'):
                chromosomes = process_line(line)

            # Process error pairs and add to nested list
            elif line.lower().startswith('errors'):
                errors = process_errors(line)

            # Raise error if input file is wrong
            else:
                raise InputParamsError(
                "Invalid input file txt format. Expected the following format:\n"
                "coverages: 10, 20, 30\n"
                "seed: 4, 5, 6\n"
                "chromosomes: chr20, chr21\n"
                "errors: 0.01:0.05,0.002:0.004\n"
                "For more information, see the input format documentation:\n"
                "https://github.com/jcapecci09/variant-caller-benchmark/blob/main/README.md"
                )

    # use snakemake pipeline to benchmark tools at 
    # different replications (seeds), sequencing coverages, and chromosomes
    for chromosome in chromosomes:
        for error_pair in errors:
            for coverage in coverages:
                for seed in seeds:

                    # set output path
                    output = f'coverage{coverage}_seed{seed}_min-error{error_pair[0]}_max-error{error_pair[1]}'

                    # run pipeline
                    subprocess.run([
                        'snakemake',
                        '-s', 'pipelines/improved.smk',
                        '--cores', '4',
                        f'--rerun-incomplete',
                        '--config',
                        f'coverage={coverage}',
                        f'seed={seed}',
                        f'chromosome={chromosome}',
                        f'folder={output}',
                        f'aligner={args.aligner}',
                        f'min-err={error_pair[0]}',
                        f'max-err={error_pair[1]}'
                       
                    ], check=True)

        # Remove chromosome data to save memory
        shutil.rmtree(f"Data/{chromosome}")


if __name__ == '__main__':
    main()
    