#!/usr/bin/env python3
#
# automatization of openmpi installation with pmix ans slurm support
#
# Status: DEBUGGED - date: Jun 3 2021
#
# Warnings:
# Check output of bash process and quit execution if it fails
#
# Maintainer: glozanoa <glozanoa@uni.pe>

import os
from sbash import Bash
from fineprint.status import print_status, print_successful
from fineprint.color import ColorStr

from pkg import Package


class OpenMPI(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None):
        depends = {
            "gcc": {"Centos": "gcc.x86_64"},
            "pmix": {"CentOS": "https://github.com/fpolit/ama-framework/blob/master/depends/cluster/pmix.py"}
        }

        makedepends = {
            "make": {"Centos": "make.x86_64"},
            "wget": {"Centos": "wget.x86_64"}
        }
        self.prefix = "/usr/local/openmpi" # default prefix
        super().__init__("openmpi",
                         pkgver=pkgver,
                         source=source,
                         depends=depends,
                         makedepends=makedepends,
                         build_path = build_path,
                         uncompressed_dir= uncompressed_dir)

    def set_prefix(self, prefix):
        self.prefix = os.path.abspath(os.path.expanduser(prefix))

    def build(self):
        print_status(f"Building {self.pkgname}-{self.pkgver}")
        print(ColorStr("It can take a while, so go for a coffee ...").StyleBRIGHT)

        flags = [
            f"--prefix={self.prefix}",
            "--with-pmix=/usr",
            "--with-pmi",
            "--with-slurm"
        ]

        configure = "./configure " + " ".join(flags)
        Bash.exec(configure, where=self.uncompressed_path)
        Bash.exec("make", where=self.uncompressed_path)

    def install(self):
        super().install()
        print_successful(f"Package {self.pkgname}-{self.pkgver} was sucefully installed in {self.prefix}")

        print_status("Adding openmpi to you PATH")

        openmpi2path = f"""
### exporting openmpi to the PATH
export OPENMPI_HOME={self.prefix}
export PATH=$PATH:$OPENMPI_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$OPENMPI_HOME/lib
        """

        with open(os.path.expanduser("~/.bashrc"), 'a') as bashrc:
            bashrc.write(openmpi2path)

        # exporting OpenMPI to the PATH
        openmpi_bin = os.path.join(self.prefix, "bin")
        os.environ['PATH'] += f":{openmpi_bin}"
