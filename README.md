# Scripts to automate compilation of packages
Here you can find python scripts to automate the installation of packages needed to configure a cluster of computers.

## Usage
First you need to install the python requirements.
```bash
  $ python3 -m pip install -r requirements.txt
```

Then to install `Pdsh`, `Munge`, `pmix`, `Slurm`, `PySlurm` and `OpenMPI`
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
Tested GNU/Linux distributions:
* Centos 8
