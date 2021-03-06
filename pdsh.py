#!/usr/bin/env python3
#
# automatization of pdsh installation
#
# Status: DEBUGGED - date: Jun 24 2021
# TESTED DISTRIBUTIONS: [Centos Strem 8]
#
# Warnings:
# Check output of bash process and quit execution if it fails
#
# Maintainer: glozanoa <glozanoa@uni.pe>

import os
import distro
from tabulate import tabulate
from sbash import Bash
from fineprint.status import print_status, print_successful, print_failure
from fineprint.color import ColorStr

from pkg import Package, BuildablePackage
from linux_requirements import install_requirements



class Pdsh(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None, prefix="/usr/local/pdsh"):
        depends = {
            "ssh": {"Centos": "libssh.x86_64"},
        }

        makedepends = {
            "make": {"Centos": "make.x86_64"},
            "wget": {"Centos": "wget.x86_64"}
        }

        super().__init__("pdsh",
                         pkgver=pkgver,
                         source=source,
                         depends=depends,
                         makedepends=makedepends,
                         build_path = build_path,
                         uncompressed_dir= uncompressed_dir,
                         prefix=prefix)


    def build(self):
        print_status(f"Building {self.pkgname}-{self.pkgver}")
        print(ColorStr("It can take a while, so go for a coffee ...").StyleBRIGHT)

        #import pdb; pdb.set_trace()
        Bash.exec("./bootstrap", where=self.uncompressed_path)
        flags = [
            f"--prefix={self.prefix}",
            "--with-ssh"
        ]

        configure = "./configure " + " ".join(flags)
        Bash.exec(configure, where=self.uncompressed_path)
        Bash.exec("make", where=self.uncompressed_path)

    def install(self):
        print_status(f"Installing {self.pkgname}-{self.pkgver} in {self.prefix}")
        #import pdb; pdb.set_trace()

        Bash.exec("sudo make install", where=self.uncompressed_path)

        print_status("Adding pdsh to the PATH")
        pdsh2path = f"""
# Adding PDSH to the PATH
export PDSH_RCMD_TYPE=ssh
export PDSH_HOME={self.prefix}
export PATH=$PATH:$PDSH_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PDSH_HOME/lib
            """

        with open(os.path.expanduser("~/.bashrc"), 'a') as bashrc:
            bashrc.write(pdsh2path)
        

if __name__ == "__main__":
    parser = Package.cmd_parser()
    parser.add_argument("--prefix", default="/usr/local/pdsh",
                        metavar="/usr/local/pdsh",
                        help="Location to install PDSH")
    args = parser.parse_args()

    build_path = os.path.abspath(os.path.expanduser(args.build_dir))

    bpkg = BuildablePackage(name='pdsh', version='2.34',
                            source='https://github.com/chaos/pdsh/releases/download/pdsh-2.34/pdsh-2.34.tar.gz',
                            pkg=Pdsh, build_path=build_path, uncompressed_dir='pdsh-2.34',
                            prefix=args.prefix)

    pretty_name_distro = distro.os_release_info()['pretty_name']
    print_status(f"Installing the following packages in {pretty_name_distro}")
    bpkg_table = [[bpkg.name, bpkg.version, bpkg.source]]
    print(tabulate(bpkg_table, headers=["Package", "Version", "Source"], tablefmt="pretty"))

    while True:
            short_answer = input("Proceed with installation? (y/n) ")
            short_answer = short_answer.lower()
            if short_answer in ['y', 'yes', 'n', 'no']:
                if short_answer in ['n', 'no']:
                    print_failure("Installation was canceled")
                    exit(1)
                else:
                    break


    install_requirements(distro.id(), pkgs=["pdsh"])

    PkgClass = bpkg.pkg
    pkg = PkgClass(**bpkg.init_options())

    installation_options = { # default installation options
        'no_confirm': True,
        'avoid_download': False,
        'avoid_uncompress': False,
        'avoid_check': True
    }

    if args.only_compile:
        installation_options['avoid_download'] = True
        installation_options['avoid_uncompress'] = True

    if args.avoid_download:
        installation_options['avoid_download'] = True

    if args.avoid_uncompress:
        installation_options['avoid_uncompress'] = True

    pkg.doall(**installation_options)