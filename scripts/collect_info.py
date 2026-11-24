"""Append results from pipeline to results.csv

This script is heavily hardcoded. So, if anything changes in the snakefile
pipeline this script may have to be refactored. 

Example usage:
        python scripts/collect_info.py \
            --bcf benchmarking_data.txt all_variants.txt indels.txt non_indels.txt \
            --fb benchmarking_data.txt  all_variants.txt indels.txt non_indels.txt \
            --gatk benchmarking_data.txt all_variants.txt indels.txt non_indels.txt \
            --chromosome 22 \
            --coverage 10 \
            --seed 1

for the commands bcf, fb, and gatk. User must input data in the following order:

1. benchmarking_data: output for /usr/bin/time
2. all variants: Text file from rtg tools including all variants 
3. indels: Text file from rtg tools including only indel variants
4. non_indels: text file from rtg tools including all non indel variants [MNPs, SNPs, other]

Author: Jimmy Capecci
"""

# import libraries
from pathlib import Path
import argparse

def main():

    # set up  parser for command line support
    parser = argparse.ArgumentParser(description='Adds bench marking data to csv')

    # add arguments for command 
    parser.add_argument('--bcf', nargs='+', required=True, help='bcftools statistics')
    parser.add_argument('--fb', nargs='+', required=True, help='Freebayes statistics')
    parser.add_argument('--gatk', nargs='+', required=True, help='gatk HaplotypeCaller statistics')
    parser.add_argument('--chromosome', required=True, help='Chromosome being simulated')
    parser.add_argument('-c', '--coverage', required=True, help='Coverage used to simulate reads')
    parser.add_argument('-s', '--seed', required=True, help='Seed used to simulate reads')
    parser.add_argument('--min_err', required=True, help='Coverage used to simulate reads')
    parser.add_argument('--max_err', required=True, help='Seed used to simulate reads')

    # grab arguments from command line
    args = parser.parse_args()

    if len(args.bcf) != 4 or len(args.fb) != 4 or len(args.gatk) != 4:
        parser.error('Each caller must have exactly 4 input files')

    # set variables to command line arguments
    chromosome = args.chromosome
    coverage = args.coverage
    seed = args.seed
    max_err = args.max_err
    min_err = args.min_err

    # set output csv path and dictionary for collection
    output_csv = 'results.csv'
    data_collector = {}

    # if results.csv doesnt exist intialize it with headers
    if not Path(output_csv).exists():
        headers = ['Chromosome', 'Coverage', 'Seed', 'Min_err', 'Max_err', 'Tool', 'Time', 
               'Memory', 'True-pos-baseline', 'True-pos-call',
               'False-pos', 'False-neg', 'Precision', 'Sensitivity',
               'F-measure', 'Indel-True-pos-baseline', 'Indel-True-pos-call',
               'Indel-False-pos', 'Indel-False-neg', 'Indel-Precision', 'Indel-Sensitivity',
               'Indel-F-measure', 'Non-Indel-True-pos-baseline', 'Non-Indel-True-pos-call',
               'Non-Indel-False-pos', 'Non-Indel-False-neg', 'Non-Indel-Precision', 'Non-Indel-Sensitivity',
               'Non-Indel-F-measure']
        with open(output_csv, 'w') as o:
            o.write(','.join(headers) + '\n')
            

    # grab txt files that was output from /usr/bin/time
    time_paths = {'BCFtools': args.bcf[0], 'FreeBayes': args.fb[0], 'GATK HaplotypeCaller': args.gatk[0]}

    # string to match time and ram
    time_indicator = 'Elapsed (wall clock) time (h:mm:ss or m:ss):'
    ram_indicator = 'Maximum resident set size (kbytes):'

    # for each text file 
    for tool, path in time_paths.items():

        # Assign t and r to None as safety in case time and ram indicators aren't present
        t = None 
        r = None

        # With each benchmarking file
        with open(path, 'r') as f:
            for line in f:
                if time_indicator in line:
                    t = line.split(' ')[-1].strip() # grab time

                elif ram_indicator in line:
                    r = line.split(' ')[-1].strip() # grab ram

        data_collector[tool] = {'time': t, 'ram': r} # assign tool to time and ram


    # grab text files associated with accuracy
    # Each tool will have 3 files [all, indels, non-indels] in that order
    acc_paths = {
                 'BCFtools': [args.bcf[i] for i in range(1, 4)], 
                 'FreeBayes': [args.fb[i] for i in range(1, 4)], 
                 'GATK HaplotypeCaller': [args.gatk[i] for i in range(1, 4)]
                }

    # for each tool and its accuracy metrics [all, indels, non indels]
    for tool, acc_metrics in acc_paths.items():

        # Keep track of type of metric
        type_metric = ['', 'Indel-', 'Non-Indel-']

        # for each metric type 
        for i, metric_path in enumerate(acc_metrics):
            with open(metric_path, 'r') as f:
                f.readline()
                f.readline()
                line = f.readline().split() # grab statistics 

            # assign tool to each statistic for its metric type 
            data_collector[tool][type_metric[i] + 'True-pos-baseline'] = line[1]
            data_collector[tool][type_metric[i] + 'True-pos-call'] = line[2]
            data_collector[tool][type_metric[i] + 'False-pos'] = line[3]
            data_collector[tool][type_metric[i] + 'False-neg'] = line[4]
            data_collector[tool][type_metric[i] + 'Precision'] = line[5]
            data_collector[tool][type_metric[i] + 'Sensitivity'] = line[6]
            data_collector[tool][type_metric[i] + 'F-measure'] = line[-1]
 
    # write results to csv 
    with open(output_csv, 'a') as o:
        for key, stats_dict in data_collector.items():
            row = [chromosome, coverage, seed, min_err, max_err, key, *stats_dict.values()]
            o.write(','.join(row) + '\n')

if __name__ == '__main__':
    main()
