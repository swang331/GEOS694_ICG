#!/bin/bash
#SBATCH --job-name=atm_profile
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --output=atm_profile_%j.out

python /home/swang18/atm_profile.py
