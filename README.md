# variant-caller-benchmark

## Highlights 

## Description


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

### 5. Run the benchmark

```bash
python benchmark.py -c 30 -s 42 -r chr20
```

This command benchmarks variant callers using a sequencing coverage of 30×, a random seed of 42, and chromosome 20.


## Command-line Arguments

| Flag | Long Option | Description | Default |
|---|---|---|---|
| `-c` | `--coverage` | Sequencing coverage | `30` |
| `-s` | `--seed` | Random seed used to simulate reads | `42` |
| `-r` | `--chromosome` | Chromosome to download and benchmark | `chr20` |

All arguments are optional. If no arguments are provided, the pipeline uses the default values shown above.

## Output

The pipeline generates a CSV file containing benchmarking results for each variant caller, including runtime, memory usage, and variant-calling performance metrics.

| Chromosome | Coverage | Seed | Tool | Time | Memory | True-pos-baseline | True-pos-call | False-pos | False-neg | Precision | Sensitivity | F-measure |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chr20 | 30 | 42 | freebayes | 9:33.48 | 199384 | 72219 | 71918 | 370 | 1724 | 0.9949 | 0.9767 | 0.9857 |
| chr20 | 30 | 42 | bcftools | 6:10.28 | 105020 | 71716 | 74881 | 100 | 2227 | 0.9987 | 0.9699 | 0.9841 |

**Note:** GATK HaplotypeCaller support will be added in a future update.

## Methods






