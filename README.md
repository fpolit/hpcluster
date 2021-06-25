# Scripts to automate configuration of an HPC cluster
Here you can find python scripts to automate the installation of packages needed to configure a cluster of computers.

## Usage
First you need to install the python requirements.
```bash
  $ python3 -m pip install -r requirements.txt
```

Then, to install `Pdsh`, `Munge`, `Pmix`, `Slurm`, `PySlurm` and `OpenMPI`
```bash
  $ python3 auto_install.py -b build --pdsh-prefix=PDSH_PREFIX --openmpi-prefix=OPENMPI_PREFIX
```
The above command will create a directory called **build**, where all the packages will be downloaded, uncompressed and compiled.

By default `PDSH_PREFIX` is `/usr/local/pdsh` and `OPENMPI_PREFIX` is `/usr/local/openmpi`. All the other packages (`Pmix`, `Munge`, `Slurm` and `Pyslurm` are installed in appropriated *paths*, check the scripts for more detail)

If you want to install only a single package then run its script (for example to install `Slurm`, run `slurm.py` script). For more detail run:
```bash
  $ python3 PKG_NAME.py -h
```

**NOTE:**  
* Tested GNU/Linux distributions:
  * Centos 8

* If you don't want to install a package, then list it in `--disable` flag (but be careful with dependencies)


### Suggestions
To avoid run `auto_install.py` script in each node (*good luck if you are responsible of 1000 nodes*), I will show you how we can **vectorize** the installation using **pdsh**.

First we need to install pdsh in all the nodes (Sorry, but you said me that you are going to show me a vectorized way?. Yes. I'm sure you haven't thought of running `pdsh.py` script in each node. Any way run `vector_pdsh.py`)

```bash
  $ python3 vector_pdsh.py nodes.txt
```

Where `nodes.txt` is a file that have all nodes' IP4s (one by line).

COMMING SOON.
