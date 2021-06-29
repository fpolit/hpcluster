# Scripts to automate configuration of an HPC cluster (UPDATE)
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

(I am in the *master* node) First of all, we need to create a `SSH key` to identify us in every node with the same password (even if the password of each node is diferent).
To do that run `ssh-keygen`, but rename with the following name `~/.ssh/id_rsa_cluster`. Then add each `slave` node to `/etc/hosts` in the following form  `IP_NODE  NAME_NODE` (one per line)
Then, we need export our public key (`~/.ssh/id_rsa_cluster.pub`) to all the other nodes (even itself). To do that run `exportkey.sh` bash script.

```bash
  $ ./exportkey.sh ~/.ssh/id_rsa_cluster.pub USER NODELIST
```
where `USER` is the slave node's user and `NODELIST` is a regular expresion of the node (e.g. if your nodes were called *node00*, *node01*, ..., *node20*), then `NODELIST` will be `nodes[00-20]` (check [python-hostlist](https://www.nsc.liu.se/~kent/python-hostlist/) for more details)


Now, we need to install *pdsh* in all the nodes (Sorry, but you said me that you are going to show me a vectorized way?. Yes. I'm sure you haven't thought of running `pdsh.py` script in each node. Any way run `vector_pdsh.py`)

```bash
  $ python3 vector_pdsh.py NODELIST
```
where `NODELIST` is a regular expresion like above. After installing `pdsh`, we need to create a ssh key but witout passphrase (save it in as `~/.ssh/id_rsa_pdsh`).
Then, share the public key of the generated SSh key (use `exportkey.sh` script and *root* in `USER` variable) and add `export PDSH_SSH_ARGS="-i ~/.ssh/id_rsa_pdsh"` to your `~/.bashrc` file.

Now, we are going to check if pdsh was configured sucessfully, but before, refresh you terminal (reconnect to the node if your are using SSH, or relog if you are in the master node).

```bash
  $ pdsh -w root@NODELIST hostame
  # expected output
  # NODE00 : NODE00
  # NODE01 : NODE01
  # MORE NODES' output
 ```
 
COMMING SOON.
