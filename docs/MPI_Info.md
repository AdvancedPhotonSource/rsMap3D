# Overview

This document covers the topics related to usage of the MPI and parallelized components of RSMap3d. 

# Installation

NOTE: Requires MPI to have Remote Memory Access capabilities. Highly recommended that installations implement MPI >= 3.0. 

## Recommended Installation Through Conda

1. Create a default environment with python=3.6 `conda create -y -n rsMapMPI python=3.6`
2. Activate Environment: `conda activate rsMapMPI`
3. Install MPI and MPI4py with conda: `conda install -y -c conda-forge mpi4py openmpi`
4. Install requirements with pip: `pip install PyQt5==5.15.6 xrayutilities==1.7.3 spec2nexus==2021.1.11 vtk==9.1.0`
5. Install rsMap from root dir: `pip install .`

# Usage

MPI is implemented through a similar interface to the standard RSMap library files. Due to MPIRun launching many processes in parallel, the GUI is not supported for MPI. A script has been provded as a starting point.

## Running the Program

The program can be run via the local mpi run command. In the default installation this is `mpirun -n [num_procs] python [script].py`

On ALCF systems, this would be run with `aprun -n [num_procs] -N [num_procs per node] python [script].py`

## Script Usage

A script `Scripts/mpiMapSpecAngleScan.py` has been provided as a starting point. The script takes in a .json config file pointing to data files. The path can be provided as a command line argument: `mpiMapSpecAngleScan.py path/to/config.json` If no path is provided, the script searches for `config.json` in the CWD. 

The config format is as follows:
```json
{
    "scan_range": "[int]-[int]",
    "project_dir":"path/to/project",
    "spec_file":"spec_file (NOTE: relative to project dir)",
    "detector_config":"dtc_file (NOTE: relative to project dir)",
    "instrument_config":"inst_file (NOTE: relative to project dir)"
}

```


## Class API Changes

MPI is implemented in new classes based on the original classes.Due to sharp edges, they are located in source files with the `mpi` prefix. The constructors of MPI classes will require an additional argument: the `mpiComm`. When creating your own scripts, this can be created via the following block of code. It is also highly recommended to use the process rank to prevent the program from repeating script work. 

```python
from mpi4py import MPI

mpiComm = MPI.COMM_WORLD
mpiRank = mpiComm.Get_rank()

if mpiRank == 0: # 0th process only
    # Do singleton logging, work, etc. 
```

Operations like `dataSource.loadSource()` and `gridMapper.doMap()` are now **SYNCHRONOUS**. This means ALL scripts have to enter the same branch for them to complete. The program will _hang_ (not exit) at synchronization points. As an example:

```python
if mpiRank == 2:
    time.sleep(10)

gridMapper.doMap() # All process will be forced to wait till process 2 enters this function in 10 seconds

if mpiRank != 2: # This will cause the program to hang indefinitely
    gridMapper.doMap()
```




# Sharp Edges

A major sharp edge is `num scans >= num cores`. If a run only uses 10 scans, no more than 10 cores may be applied. Therefore this parallelization only improves larger runs. The `Scripts/mpiMapSpecAngleScan.py` script checks for this and raises an error if otherwise. It's highly recommended that your scripts do the same. 

Parallelization also introduces sharp edges related to the gridder and loading of data. 

## Gridder

Two gridder settings are required for this form of parallelization to work:

1. Normalization must be off. This is the default in xrayutilities==1.7.3.
2. The gridder must be a static size. This is hard-coded false in the mpigridmapper.py file. 

The gridder is passed through MPI channels `nlog(n)` times (where n = num_procs) during the program. An extremely large gridder size may increase runtimes. 

## Loading

Loading of data into the datasource is parallelized. As such, a datasource merging operation is required. This is implemented via the following block and functions in `MpiSector33SpecDataSource.py`: 

```python
scanData = self.exportScans()
scanData = self.mpiMergeSources(scanData)

scanData = self.mpiComm.bcast(scanData, root=0)
self.importScans(scanData)
```

If your implementation requires additional data to be loaded, `exportScans` and `importScans` will need to be modified. If the data is not list or dict based, `mpiMergeSources` will need modification. Custom merge operations can be added to the conditional in the merge method. Any new data being passed through MPI must be able to be pickled. 

# Performance Characteristics

This section will cover expected program performance and recommendations for optimizing runs. 

## Performance Factors

The program adds a `nlog(n)` operation where `n = num_procs` to both loading and gridding. The length of a single operation depends primarily on the size of data being passed through a MPI pipe. This means single-node runs will perform this operation faster than multi-node runs. 

Otherwise, gridding is expected to scale with a factor of `1/(2^n)`. Loading is expected to scale the same, but may be limited by disk access speeds. 

## Recommended Settings

While multi-threading is applied by xrayutilities, it only affects about <5% of execution time. As such, the main parameter to vary is the number of processes. Through testing we recommend `num_procs = num MPI slots` as a reasonable starting point. Experiment with your system to find what works best. 