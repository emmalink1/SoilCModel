#!/bin/bash -l        
#SBATCH --time=0:10:00
#SBATCH --ntasks=3
#SBATCH --mem=10g
#SBATCH --tmp=10g
#SBATCH --mail-type=NONE  
#SBATCH --mail-user=link0126@umn.edu 
#SBATCH -A eshook

python3 MVP2.py
