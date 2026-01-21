#!/bin/bash
# Test validation dataset with proper environment
export XLA_FLAGS=--xla_gpu_cuda_data_dir=$CONDA_PREFIX
python test_validation.py
