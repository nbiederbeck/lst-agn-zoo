# LST AGN Zoo

## Installation

```
git submodule update --init
```

Also make sure to have an environment activated where snakemake and astropy are installed.
Create such an environment with

```
mamba env create -f lst-agn-analysis/workflow/envs/snakemake.yml
conda activate snakemake
```

## Usage

```
make
```
