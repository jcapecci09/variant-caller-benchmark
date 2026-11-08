# variant-caller-benchmark

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Conda](https://img.shields.io/badge/Conda-44A833?style=flat&logo=anaconda&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black) ![Snakemake](https://img.shields.io/badge/Snakemake-2496ED?style=flat) ![minimap2](https://img.shields.io/badge/minimap2-4B8BBE?style=flat)  ![BCFtools](https://img.shields.io/badge/BCFtools-5C6BC0?style=flat) ![GATK](https://img.shields.io/badge/GATK-008577?style=flat) ![FreeBayes](https://img.shields.io/badge/FreeBayes-6A5ACD?style=flat) ![RTG_Tools](https://img.shields.io/badge/RTG_Tools-607D8B?style=flat) ![Holodeck](https://img.shields.io/badge/Holodeck-B565A7?style=flat)

> Benchmarking Variant Callers for Germline Variant Detection using holodeck simulated data

---

## Introduction

This project compares FreeBayes, BCFtools Mpileup, and GATK HaplotypeCaller on how accurately and quickly they can identify germline genetic variants in simulated sequencing data. The pipeline uses [Holodeck](https://github.com/fg-labs/holodeck) to generate simulated variants and sequencing reads, then aligns the reads to a reference genome using Minimap2. The variant callers analyze the same aligned reads, and their results are compared against the original simulated variants to see how accurately they identify germline variants.

The pipeline uses BCFtools to normalize variant calls and RTG Tools to evaluate accuracy. It also records runtime and memory usage to compare the computational cost of each tool. Results are collected into a CSV file containing metrics such as precision, sensitivity, and F-measure, along with runtime and memory usage.

Users can change the sequencing coverage, random seed, and chromosome through command-line arguments. This makes it possible to test how different sequencing conditions affect variant-calling performance.

---

## Usage Instructions

### Requirements

- Linux
- Git
- Miniconda

**Windows users:** You can use [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to run this tool in a Linux environment.

### 1. Clone the repository

```bash
git clone https://github.com/jcapecci09/variant-caller-benchmark.git
cd variant-caller-benchmark
```

### 2. Install Miniconda

If Conda is not already installed, download and run the Miniconda installer:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Follow the installation prompts. After installation, reload your Bash configuration:

```bash
source ~/.bashrc
```

Verify the installation:

```bash
conda --version
```

### 3. Install dependencies

Create the Conda environment using the provided environment file:

```bash
conda env create -f variants.yml
```

### 4. Activate the environment

```bash
conda activate variants
```

### 5. Run the benchmark insert text file

```bash
python benchmark.py -i params.txt
```


---
## Input file

The input file must be a `params.txt` file containing comma-separated values in the following format:
```text
coverages: 10,5
seed: 4,3
chromosomes: chr20,chr21
```

**Note:** Update the comma-separated values to test different chromosomes, random seeds, or sequencing coverage levels.

The example above performs benchmarking at 10× and 5× coverage on chromosomes 20 and 21, using two different random seeds (replications).

---

## Output

The pipeline generates a CSV file called `results.csv` containing benchmarking results for each variant caller, including runtime, memory usage, and variant-calling performance metrics.

| Chromosome | Coverage | Seed | Tool | Time | Memory | True-pos-baseline | True-pos-call | False-pos | False-neg | Precision | Sensitivity | F-measure |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chr21 | 10 | 3 | gatk |	7:05.04	| 1616812 |	40780 |	42360 |	547 |	5284 |	0.9873 |	0.8853 |	0.9335 |
| chr21 |	10 | 3 | freebayes |	2:25.83 |	146244 |	42032 |	41929 |	4353 |	4032 |	0.9059 | 0.9125 |	0.9092 |
| chr21 |	10 |	3 |	bcftools | 2:19.93 |	87876 |	40616 |	42302 |	490 |	5448 |	0.9885 |	0.8817 |	0.9321 |
---

## Results

Work in progress. 

---

## Future Improvements
- Expand output metrics to include separate precision and sensitivity measurements for indels and SNPs.
- Create scripts to visualize benchmarking results using graphs.
