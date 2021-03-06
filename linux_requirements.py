#!/usr/bin/env python3
#
# Install GNU/Linux packages needed to install cluster's packages
#
# Status: TESTED DISTRIBUTIONS = (centos stream 8, )
#
#
# Maintainer: glozanoa <glozanoa@uni.pe>

from typing import List
from sbash import Bash
from fineprint.status import print_status

requirements = {
    'centos':{
        "munge": ["openssl-devel.x86_64", "libevent-devel.x86_64", "zlib-devel.x86_64"],
        "pdsh": ["libssh.x86_64"],
        "pmix": ["libevent-devel.x86_64", "zlib-devel.x86_64"],
        "slurm": ["gtk2-devel.x86_64", "pam-devel.x86_64",
                    "mysql-devel.x86_64", "mysql-libs.x86_64",
                    "readline-devel.x86_64",
                    "hwloc-libs.x86_64",
                    "rrdtool.x86_64"],
        "john": ["openssl-devel.x86_64"]
    },

    'kali':{
        'munge': ['libevent-dev','libssl-dev'],
        'pdsh': ['libssh-dev'],
        'pmix': ['zlib1g-dev', 'libevent-dev'],
        'slurm': ['libpam-slurm', 'libgtk2.0-dev'] # add package
    },

    'ubuntu':{
        'munge': ['libevent-dev','libssl-dev'],
        'pdsh': [],
        'pmix': ['zlib1g-dev'],
        'slurm': [] # add package
    },
    'arch':{
        "munge": ['openssl', 'libevent', 'zlib'],
        "pdsh": ['libssh'],
        "pmix": ['libevent', 'zlib'],
        "slurm": ['gtk2','pam']
    },
}

build_requirements = {
    'centos':{
        'group': ["'Development Tools'"],
        'package': ['make.x86_64', 'wget.x86_64']
    },
    'kali':{
        'package': ['python3-venv', 'autoconf', 'automake', 'libtool', 'libtool-bin'] #add autoconf package
    },
    'ubuntu':{
        'package': ['python3-venv'] #add autoconf package
    },
    'arch':{
        'package': ['base-devel', 'wget']
    }
}

def install_requirements(distro_id, *, pkgs :List[str] = None, 
                        avoid_build_requirements:bool = False,
                        only_build_requirements:bool = False):
    #import pdb; pdb.set_trace()
    if not avoid_build_requirements:
        print_status("Installing build requirements")
        for requirement_type, require in build_requirements[distro_id].items():
            if require:
                if requirement_type == "group":
                    if distro_id == "centos":
                        Bash.exec(f"sudo yum -y group install {' '.join(require)}")

                elif requirement_type == "package":
                    if distro_id == "centos":
                        Bash.exec(f"sudo yum -y install {' '.join(require)}")

                    elif distro_id in ["kali", "ubuntu"]:
                        Bash.exec(f"sudo apt -y install {' '.join(require)}")

                    elif distro_id == "arch":
                        Bash.exec(f"sudo pacman -S {' '.join(require)} --noconfirm")

    if not only_build_requirements:
        print_status("Installing package requirements")
        os_requirements = requirements[distro_id]
        pkgs_requirements = {}
        if pkgs:
            for pkg in pkgs:
                if pkg in os_requirements:
                    pkgs_requirements[pkg] = os_requirements[pkg]
        else:
            pkgs_requirements = os_requirements

        for pkg, require in pkgs_requirements.items():
            if require:
                print_status(f"Installing {pkg}'s {distro_id} dependencies")
                if distro_id == "centos":
                    Bash.exec(f"sudo yum -y install {' '.join(require)}")
                elif distro_id in ["kali", "ubuntu"]:
                    Bash.exec(f"sudo apt -y install {' '.join(require)}")
                elif distro_id == "arch":
                    Bash.exec(f"sudo pacman -S {' '.join(require)} --noconfirm")
