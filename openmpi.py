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

from pkg import Package, BuildablePackage


class OpenMPI(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None, 
                prefix:str = "/usr/local/openmpi"):
        depends = {
            "gcc": {"Centos": "gcc.x86_64"},
            "pmix": {"CentOS": "https://github.com/fpolit/ama-framework/blob/master/depends/cluster/pmix.py"}
        }

        makedepends = {
            "make": {"Centos": "make.x86_64"},
            "wget": {"Centos": "wget.x86_64"}
        }
        super().__init__("openmpi",
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


if __name__ == "__main__":
    parser = Package.cmd_parser()
    parser.add_argument("--prefix", default="/usr/local/openmpi",
                        help="Location to install OpenMPI")
    args = parser.parse_args()

    build_path = os.path.abspath(os.path.expanduser(args.build_dir))

    bpkg =  BuildablePackage(name='openmpi', version='4.1.1',
                            source='https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.1.tar.gz',
                            pkg=OpenMPI, build_path=build_path, uncompressed_dir='openmpi-4.1.1',
                            prefix=args.openmpi_prefix)

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