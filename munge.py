#!/usr/bin/env python3
#
# automatization of munge installation
#
# Status: DEBUGGED - date May 31 2021
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


class Munge(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None):
        depends = {
            "gcc": {"Centos": "gcc.x86_64"},
            "OpenSSL": {"Centos": "openssl-devel.x86_64"},
            "libevent": {"Centos": "libevent-devel.x86_64"},
            "zlib": {"Centos": "zlib-devel.x86_64"}
        }

        makedepends = {
            "make": {"Centos": "make.x86_64"},
            "wget": {"Centos": "wget.x86_64"}
        }

        super().__init__("munge",
                         pkgver=pkgver,
                         source=source,
                         depends=depends,
                         makedepends=makedepends,
                         build_path=build_path,
                         uncompressed_dir=uncompressed_dir)

    def build(self):
        print_status(f"Building {self.pkgname}-{self.pkgver}")
        print(ColorStr("It can take a while, so go for a coffee ...").StyleBRIGHT)

        Bash.exec("./bootstrap", where=self.uncompressed_path)
        flags = [
            "--prefix=/usr",
            "--sysconfdir=/etc",
            "--localstatedir=/var",
            "--libdir=/usr/lib64"
        ]

        configure = "./configure " + " ".join(flags)
        Bash.exec(configure, where=self.uncompressed_path)
        Bash.exec("make", where=self.uncompressed_path)

    def install(self):
        print_status(f"Installing {self.pkgname}-{self.pkgver}")
        #import pdb; pdb.set_trace()

        Bash.exec("sudo make install", where=self.uncompressed_path)

        print_status(f"Configuring {self.pkgname}-{self.pkgver} package")
        configure = [
            "sudo useradd -s /bin/bash -d /var/log/munge munge",
            "sudo chown munge:munge -R /var/log/munge/",

            "sudo chown munge:munge /etc/munge/",
            "sudo chmod 700 /etc/munge/",

            "sudo chown munge:munge /var/lib/munge/",
            "sudo chmod 711 /var/lib/munge/",

            "sudo chmod 700 /var/log/munge"
        ]

        for cmd in configure:
            print(cmd)
            Bash.exec(cmd)

        print_status("Now create munge key in /etc/munge using mungekey.Then initialize munge service")


if __name__ == "__main__":
    parser = Package.cmd_parser()
    args = parser.parse_args()

    build_path = os.path.abspath(os.path.expanduser(args.build_dir))

    bpkg = BuildablePackage(name='munge', version='0.5.14',
                    source='https://github.com/dun/munge/archive/refs/tags/munge-0.5.14.tar.gz',
                    pkg=Munge, build_path=build_path, uncompressed_dir='munge-munge-0.5.14')
    
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
    import pdb; pdb.set_trace()
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