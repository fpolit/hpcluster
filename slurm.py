#!/usr/bin/env python3
#
# automatization of slurm installation
#
# Status: DEBUGGED - date: Jun 24 2021
# TESTED DISTRIBUTIONS: [Centos Strem 8]
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


class Slurm(Package):
    def __init__(self, *, pkgver, source, build_path, uncompressed_dir=None):
        depends = {
            "gcc": {"CentOS": "gcc.x86_64"},
            "pmix": {"Linux": "ADD_LINK2SCRIPT"},
            "gtk2": {"CentOS": "gtk2-devel.x86_64"},
            "pam": {"CentOS": "pam-devel.x86_64"}
            }

        makedepends = {
            "make": {"CentOS": "make.x86_64"},
            "wget": {"CentOS": "wget.x86_64"}
        }

        super().__init__("slurm",
                         pkgver=pkgver,
                         source=source,
                         depends=depends,
                         makedepends=makedepends,
                         build_path = build_path,
                         uncompressed_dir= uncompressed_dir)

    def build(self):
        print_status(f"Building {self.pkgname}-{self.pkgver}")
        print(ColorStr("It can take a while, so go for a coffee ...").StyleBRIGHT)

        print_status("Running autreconf")
        Bash.exec("autoreconf", where=self.uncompressed_path)
        flags = [
            "--disable-developer",
            "--disable-debug",
            "--enable-optimizations",
            "--prefix=/usr",
            "--sbindir=/usr/bin",
            "--sysconfdir=/etc/slurm-llnl",
            "--localstatedir=/var",
            "--with-pmix=/usr",
    	    "--with-hwloc",
	        "--with-rrdtool",
            "--with-munge"
        ]
        configure = "./configure " + " ".join(flags) 
        Bash.exec(configure, where=self.uncompressed_path)
        
        #import pdb; pdb.set_trace()
        Bash.exec("make", where=self.uncompressed_path)

    def install(self):
        print_status(f"Installing {self.pkgname}-{self.pkgver}")
        Bash.exec("sudo make install", where=self.uncompressed_path)

        print_status(f"Configuring {self.pkgname}-{self.pkgver} package")

        configurations = [
            'sudo install -D -m644 etc/slurm.conf.example    "/etc/slurm-llnl/slurm.conf.example"',
            'sudo install -D -m644 etc/slurmdbd.conf.example "/etc/slurm-llnl/slurmdbd.conf.example"',
            'sudo install -D -m644 LICENSE.OpenSSL           "/usr/share/licenses/slurm/LICENSE.OpenSSL"',
            'sudo install -D -m644 COPYING           "/usr/share/licenses/slurm/COPYING"',
            'sudo install -D -m755 etc/init.d.slurm      "/etc/rc.d/slurm"',
            'sudo install -D -m755 etc/init.d.slurmdbd   "/etc/rc.d/slurmdbd"',
            'sudo install -D -m644 etc/slurmctld.service "/usr/lib/systemd/system/slurmctld.service"',
            'sudo install -D -m644 etc/slurmd.service    "/usr/lib/systemd/system/slurmd.service"',
            'sudo install -D -m644 etc/slurmdbd.service  "/usr/lib/systemd/system/slurmdbd.service"',
            'sudo install -d -m755 "/var/log/slurm-llnl"',
            'sudo install -d -m755 "/var/lib/slurm-llnl"',
            'sudo useradd -r -c "slurm daemon" -u 64030 -s /bin/nologin -d /var/log/slurm-llnl slurm',
            'sudo install -d -m700 "/var/spool/slurm/d"',
            'sudo install -d -m700 -o slurm -g slurm "/var/spool/slurm/ctld"'
        ]

        for cmd in configurations:
            print(cmd)
            Bash.exec(cmd, where=self.uncompressed_path)


if __name__ == "__main__":
    parser = Package.cmd_parser()
    args = parser.parse_args()

    build_path = os.path.abspath(os.path.expanduser(args.build_dir))

    bpkg = BuildablePackage(name='slurm', version='20.02.7',
                            source='https://download.schedmd.com/slurm/slurm-20.02.7.tar.bz2',
                            pkg=Slurm, build_path=build_path, uncompressed_dir='slurm-20.02.7')

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


    install_requirements(distro.id(), pkgs=["slurm"])


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
