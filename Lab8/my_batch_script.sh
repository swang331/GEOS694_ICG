#!/bin/bash
#SBATCH --job-name="hello world!"     # Job name
#SBATCH --partition=t1small
#SBATCH --nodes=2                     # Number of nodes
#SBATCH --ntasks-per-node=1           # Number of tasks per node
#SBATCH --output=%j_%x.out
#SBATCH --time=00:00:05

srun echo "Hello"
srun echo $SLURM_JOB_NODELIST
srun echo $SLURM_JOB_CPUS_PER_NODE
srun sleep 10
srun echo "World"
