coverage = config["coverage"]
chromosome = config['chromosome']
seed = config['seed']
folder  = config['folder']

rule all:
    input:
        f'Data/{chromosome}/{folder}/benchmarking/collected.done'

# ==========================================================
# Handle chromosome reference
# ==========================================================

# Download individual chromosome reference sequences (FASTA) from the UCSC hg38 (GRCh38) genome assembly.
rule download_reference:
    output:
        f'Data/{chromosome}/{chromosome}.fa.gz'

    shell:
        '''
        mkdir -p Data/{chromosome}
        wget \
        'https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/{chromosome}.fa.gz' \
        -O {output}
        '''

# Decompress the downloaded chromosome reference FASTA files
rule decompress_reference:
    input:
        f'Data/{chromosome}/{chromosome}.fa.gz'

    output:
        f'Data/{chromosome}/{chromosome}.fa'

    shell:
        '''
        gunzip -c {input} > {output}
        '''

# Index reference FASTA files for efficient sequence retrieval
rule index_reference:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa'

    output:
        f'Data/{chromosome}/{chromosome}.fa.fai'

    shell:
        '''
        samtools faidx {input.ref}
        '''

# ==========================================================
# holodeck simulation and preparing for variant callers
# ==========================================================

# Generate a truth VCF containing simulated genetic variants
# Uses the reference genome and a specified random seed to generate SNPs
rule generate_truth_vcf:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        index = f'Data/{chromosome}/{chromosome}.fa.fai'

    output:
        vcf = f'Data/{chromosome}/{folder}/simulated/truth.vcf'

    shell:
        '''
        mkdir -p Data/{chromosome}/{folder}/simulated

        holodeck mutate \
        -r {input.ref} \
        -o {output.vcf} \
        --snp-rate 0.001 \
        --seed {seed}
        '''

# Simulate paired-end sequencing reads using the reference genome and truth VCF
# Generates FASTQ files containing simulated reads
rule generate_reads:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        vcf = f'Data/{chromosome}/{folder}/simulated/truth.vcf'

    output:
        r1 = f'Data/{chromosome}/{folder}/simulated/sim.r1.fastq.gz',
        r2 = f'Data/{chromosome}/{folder}/simulated/sim.r2.fastq.gz'

    shell:
        '''
        mkdir -p Data/{chromosome}/{folder}/simulated

        holodeck simulate \
        -r {input.ref} \
        -v {input.vcf} \
        -o Data/{chromosome}/{folder}/simulated/sim \
        --coverage {coverage} \
        --seed {seed}
        '''

# Align simulated reads using minimap2
rule align_reads:
    threads: 4
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        r1 = f'Data/{chromosome}/{folder}/simulated/sim.r1.fastq.gz',
        r2 = f'Data/{chromosome}/{folder}/simulated/sim.r2.fastq.gz'

    output:
        bam = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam',
        bam_index = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam.bai'

    shell:
        '''
        mkdir -p Data/{chromosome}/{folder}/aligned

        minimap2 \
            -ax sr \
            -R '@RG\\tID:sample1\\tSM:sample1\\tPL:ILLUMINA' \
            -t {threads} \
            {input.ref} \
            {input.r1} \
            {input.r2} \
            | samtools sort \
            -o {output.bam}

        samtools index {output.bam}
        '''

# ==========================================================
# variant calling, BCFtools, FreeBayes,
# and GATK HaplotypeCaller
# ==========================================================

# perform bcftools
rule benchmark_bcftools:
    threads: 1

    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        bam = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam',
        bam_index = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam.bai'
    
    output:
        vcf = f'Data/{chromosome}/{folder}/vcfs/bcftools.vcf.gz',
        bench = f'Data/{chromosome}/{folder}/benchmarking/bcftools.txt'

    shell:
        '''
        mkdir -p $(dirname {output.vcf})
        mkdir -p $(dirname {output.bench})
        /usr/bin/time -v -o {output.bench} \
        bash -c '
            bcftools mpileup \
                -Ou \
                -f {input.ref} \
                {input.bam} \
            | bcftools call \
                -mv \
                -Oz \
                -o {output.vcf}
            '
        
        '''

# Perform freebayes
rule benchmark_freebayes:
    threads: 1

    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        bam = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam',
        bam_index = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam.bai'

    output:
        vcf = f'Data/{chromosome}/{folder}/vcfs/freebayes.vcf.gz',
        bench = f'Data/{chromosome}/{folder}/benchmarking/freebayes.txt'

    shell:
        '''
        mkdir -p $(dirname {output.vcf})
        mkdir -p $(dirname {output.bench})

        /usr/bin/time -v -o {output.bench} \
        freebayes \
            -f {input.ref} \
            {input.bam} \
        | bgzip -c > {output.vcf}
        '''

# Generate a sequence dictionary required by GATK.
rule create_sequence_dictionary:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa'

    output:
        dict = f'Data/{chromosome}/{chromosome}.dict'

    shell:
        '''
        gatk CreateSequenceDictionary \
            -R {input.ref} \
            -O {output.dict}
        '''

# Perform gatk haplotypecaller
rule benchmark_gatk_haplotypecaller:
    threads: 1

    input: 
        ref = f'Data/{chromosome}/{chromosome}.fa',
        bam = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam',
        dict = f'Data/{chromosome}/{chromosome}.dict',
        bam_index = f'Data/{chromosome}/{folder}/aligned/minimap2_sorted.bam.bai'
    
    output: 
        vcf = f'Data/{chromosome}/{folder}/vcfs/gatk.vcf.gz',
        bench = f'Data/{chromosome}/{folder}/benchmarking/gatk.txt'
    
    shell:
        '''
        mkdir -p $(dirname {output.vcf})
        mkdir -p $(dirname {output.bench})
        /usr/bin/time -v -o {output.bench} \
        gatk HaplotypeCaller \
        -R {input.ref} \
        -I {input.bam} \
        -O {output.vcf}
        '''

# ==========================================================
# Evaluate variant callers and add to csvs
# ==========================================================

# normalize vcfs
rule normalize_vcf:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa',
        truth = f'Data/{chromosome}/{folder}/simulated/truth.vcf',
        bcf =  f'Data/{chromosome}/{folder}/vcfs/bcftools.vcf.gz',
        fb = f'Data/{chromosome}/{folder}/vcfs/freebayes.vcf.gz',
        gatk = f'Data/{chromosome}/{folder}/vcfs/gatk.vcf.gz'
    
    output:
        norm_truth = f'Data/{chromosome}/{folder}/simulated/truth_norm.vcf.gz',
        norm_truth_index = f'Data/{chromosome}/{folder}/simulated/truth_norm.vcf.gz.tbi',
        norm_bcf = f'Data/{chromosome}/{folder}/vcfs/bcftools_norm.vcf.gz',
        norm_bcf_index = f'Data/{chromosome}/{folder}/vcfs/bcftools_norm.vcf.gz.tbi',
        norm_fb = f'Data/{chromosome}/{folder}/vcfs/freebayes_norm.vcf.gz',
        norm_fb_index = f'Data/{chromosome}/{folder}/vcfs/freebayes_norm.vcf.gz.tbi',
        norm_gatk = f'Data/{chromosome}/{folder}/vcfs/gatk_norm.vcf.gz',
        norm_gatk_index = f'Data/{chromosome}/{folder}/vcfs/gatk_norm.vcf.gz.tbi'

    shell:
        '''
        bcftools norm -f {input.ref} -Oz -o {output.norm_truth} {input.truth}
        bcftools index -t {output.norm_truth}
        bcftools norm -f {input.ref} -Oz -o {output.norm_bcf} {input.bcf}
        bcftools index -t {output.norm_bcf}
        bcftools norm -f {input.ref} -Oz -o {output.norm_fb} {input.fb}
        bcftools index -t {output.norm_fb}
        bcftools norm -f {input.ref} -Oz -o {output.norm_gatk} {input.gatk}
        bcftools index -t {output.norm_gatk}
        '''

# Convert reference FASTA to RTG SDF format
rule format_reference:
    input:
        ref = f'Data/{chromosome}/{chromosome}.fa'

    output:
        sdf = directory(f'Data/{chromosome}/{chromosome}.sdf')

    shell:
        '''
        rtg format \
            -o {output.sdf} \
            {input.ref}
        '''

# evaluate bcftools using RTG tools
rule evaluate_bcftools:
    input:
        truth = f'Data/{chromosome}/{folder}/simulated/truth_norm.vcf.gz',
        calls = f'Data/{chromosome}/{folder}/vcfs/bcftools_norm.vcf.gz',
        sdf = f'Data/{chromosome}/{chromosome}.sdf'

    output:
        accuracy = f'Data/{chromosome}/{folder}/benchmarking/accuracy/bcftools_accuracy.txt'

    shell:
        '''
        set -e

        mkdir -p Data/{chromosome}/{folder}/benchmarking/accuracy

        rtg vcfeval \
            -b {input.truth} \
            -c {input.calls} \
            -t {input.sdf} \
            -o Data/{chromosome}/{folder}/benchmarking/accuracy/bcftools

        mv Data/{chromosome}/{folder}/benchmarking/accuracy/bcftools/summary.txt \
           {output.accuracy}

        rm -rf Data/{chromosome}/{folder}/benchmarking/accuracy/bcftools
        '''


# evaluate freebayes using RTG tools
rule evaluate_freebayes:
    input:
        truth = f'Data/{chromosome}/{folder}/simulated/truth_norm.vcf.gz',
        calls = f'Data/{chromosome}/{folder}/vcfs/freebayes_norm.vcf.gz',
        sdf = f'Data/{chromosome}/{chromosome}.sdf'

    output:
        accuracy = f'Data/{chromosome}/{folder}/benchmarking/accuracy/freebayes_accuracy.txt'

    shell:
        '''
        set -e

        mkdir -p Data/{chromosome}/{folder}/benchmarking/accuracy

        rtg vcfeval \
            -b {input.truth} \
            -c {input.calls} \
            -t {input.sdf} \
            -o Data/{chromosome}/{folder}/benchmarking/accuracy/freebayes

        mv Data/{chromosome}/{folder}/benchmarking/accuracy/freebayes/summary.txt \
           {output.accuracy}

        rm -rf Data/{chromosome}/{folder}/benchmarking/accuracy/freebayes
        '''


# evaluate GATK HaplotypeCaller using RTG tools
rule evaluate_gatk:
    input:
        truth = f'Data/{chromosome}/{folder}/simulated/truth_norm.vcf.gz',
        calls = f'Data/{chromosome}/{folder}/vcfs/gatk_norm.vcf.gz',
        sdf = f'Data/{chromosome}/{chromosome}.sdf'

    output:
        accuracy = f'Data/{chromosome}/{folder}/benchmarking/accuracy/gatk_accuracy.txt'

    shell:
        '''
        set -e

        mkdir -p Data/{chromosome}/{folder}/benchmarking/accuracy

        rtg vcfeval \
            -b {input.truth} \
            -c {input.calls} \
            -t {input.sdf} \
            -o Data/{chromosome}/{folder}/benchmarking/accuracy/gatk

        mv Data/{chromosome}/{folder}/benchmarking/accuracy/gatk/summary.txt \
           {output.accuracy}

        rm -rf Data/{chromosome}/{folder}/benchmarking/accuracy/gatk
        '''

# Append results to csv
rule append_to_csv:
    input:
        bcf_bench = f'Data/{chromosome}/{folder}/benchmarking/bcftools.txt',
        fb_bench = f'Data/{chromosome}/{folder}/benchmarking/freebayes.txt',
        bcf_acc = f'Data/{chromosome}/{folder}/benchmarking/accuracy/bcftools_accuracy.txt',
        fb_acc = f'Data/{chromosome}/{folder}/benchmarking/accuracy/freebayes_accuracy.txt',
        gatk_bench = f'Data/{chromosome}/{folder}/benchmarking/gatk.txt',
        gatk_acc = f'Data/{chromosome}/{folder}/benchmarking/accuracy/gatk_accuracy.txt'

    params:
        bench_dir = f'Data/{chromosome}/{folder}/benchmarking'

    output:
        f'Data/{chromosome}/{folder}/benchmarking/collected.done'

    shell:
        '''
        python scripts/collect_stats.py \
            -i {params.bench_dir} \
            -r {chromosome} \
            -c {coverage} \
            -s {seed}
        touch {output}
        '''
