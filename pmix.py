#!/usr/bin/env python3
#
# automatization of pmix installation
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


class Pmix(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None):
        depends = {
            "gcc": {"Centos": "gcc.x86_64"},
            "libevent": {"Centos": "libevent-devel.x86_64"},
            "zlib": {"CentOS": "zlib-devel.x86_64 "},
            "munge": {"Linux": "https://github.com/fpolit/ama-framework/blob/master/depends/cluster/munge.py"},
        }

        makedepends = {
            "make": {"Centos": "make.x86_64"},
            "wget": {"Centos": "wget.x86_64"}
        }

        super().__init__("pmix",
                         pkgver=pkgver,
                         source=source,
                         depends=depends,
                         makedepends=makedepends,
                         build_path=build_path,
                         uncompressed_dir=uncompressed_dir)

    def build(self):
        print_status(f"Building {self.pkgname}-{self.pkgver}")
        print(ColorStr("It can take a while, so go for a coffee ...").StyleBRIGHT)

        Bash.exec("./autogen.pl", where=self.uncompressed_path)
        flags = [
            "--prefix=/usr",
            "--with-libevent",
            "--with-zlib",
            "--with-munge"
        ]

        configure = "./configure " + " ".join(flags)
        Bash.exec(configure, where=self.uncompressed_path)
        Bash.exec("make", where=self.uncompressed_path)

if __name__ == "__main__":
    parser = Package.cmd_parser()
    args = parser.parse_args()

    build_path = os.path.abspath(os.path.expanduser(args.build_dir))

    bpkg = BuildablePackage(name='pmix', version='3.2.3',
                            source='https://github.com/openpmix/openpmix/releases/download/v3.2.3/pmix-3.2.3.tar.gz',
                            pkg=Pmix, build_path=build_path, uncompressed_dir='pmix-3.2.3')

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

    install_requirements(distro.id(), pkgs=["pmix"])
    
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