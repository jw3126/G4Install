#!/usr/bin/python3
from subprocess import run
import subprocess
from os.path import abspath
from os import chdir
import os
import multiprocessing

class GeantInstaller(object):

    # http://geant4.web.cern.ch/geant4/UserDocumentation/UsersGuides/InstallationGuide/html/ch02s03.html
    def __init__(self,
        qt=True,
        gdml=True,
        datadir="datadir",
        build_path="build",
        source_path="source",
        origin="https://github.com/Geant4/geant4.git",
        install_path="install",
        install_data=True,
        python=False,
        multithreaded=True,
        build_py_path="build_py",
        build_type="Release",
        cxx_standard=14,
        tag="master",
        nthreads=None
        ):  
        # Design:
        # The constructor does only bookkeeping.
        # It does not install anything, or create any directories 
        # or have other side effects
        #
        # The various methods are resposible for carrying out the actual build

        if nthreads is None:
            nthreads = multiprocessing.cpu_count() - 1
            nthreads = max(1, nthreads)
        self.nthreads = nthreads

        self.tag = tag
        self.origin = origin
        self.path = {
                "source":abspath(source_path),
                "build":abspath(build_path),
                "install":abspath(install_path),
                }

        self.build_steps = [
                self.mkdirs,
                self.clone,
                self.checkout,
                self.dependencies,
                self.cmake,
                self.make]

        self.packages = ["cmake", "gcc", "g++", "make", "libexpat1-dev"]

        self.cmake_options = {
            "DGEANT4_INSTALL_DATA":"ON",
            "DCMAKE_BUILD_TYPE":build_type,
            "DCMAKE_INSTALL_PREFIX":self.path["install"],
            }

        if install_data:
            self.cmake_options["DGEANT4_INSTALL_DATA"]="ON"
        else:
            self.cmake_options["DGEANT4_INSTALL_DATA"]="OFF"
        
        if cxx_standard is not None:
            self.cmake_options["DGEANT4_BUILD_CXXSTD"]=cxx_standard

        if gdml:
            self.packages.append("libxerces-c-dev")
            self.cmake_options["DGEANT4_USE_GDML"]="ON"

        if qt:
            self.packages.append("qt5-default")
            self.cmake_options["DGEANT4_USE_QT"]="ON"

        if datadir is not None: # and install_data:
            self.path["datadir"] = abspath(datadir)
            self.cmake_options["DGEANT4_INSTALL_DATADIR"]=self.path["datadir"]

        if multithreaded:
            self.cmake_options["DGEANT4_BUILD_MULTITHREADED"]="ON"

        if python:
            assert not multithreaded
            assert build_py_path is not None
            self.packages.append("libboost-python-dev")
            self.path["build_py"] = abspath(build_py_path)
            self.build_steps.append(self.python)

        self.build_steps.append(self.finish)

    def mkdirs(self):
        for path in self.path.values():
            os.makedirs(path,exist_ok=True)
        return []

    def clone(self):
        cmd =["git", "clone", self.origin, self.path["source"], ]
        return [cmd]

    def checkout(self):
        chdir(self.path["source"])
        cmd = ["git", "checkout", self.tag]
        return [cmd]


    def dependencies(self):
        return [(["sudo", "apt-get", "install"] + self.packages + ["--yes"])]


    def cmake(self): 
        chdir(self.path["build"])
        cmd = ["cmake", self.path["source"], ]
        cmd += ["-{}={}".format(key, val) for (key, val) in self.cmake_options.items()]
        return [cmd]


    def make(self):
        chdir(self.path["build"])
        return [["make", "-j{}".format(self.nthreads)], ["make", "install"]]


    def python(self):
        chdir(self.path["build_py"])
        os.environ["GEANT4_INSTALL"] = self.path["install"]
        cmake_path = os.path.join(self.path["source"], "environments", "g4py")
        return [["cmake", cmake_path], ["make", "-j{}".format(self.nthreads)], ["make", "install"]]

    
    def run(self):
        for step in self.build_steps:
            cmds = step()
            for cmd in cmds:
                run(cmd)

    def finish(self):
        g4sh_dir = os.path.join(self.path["install"], "bin")
        g4sh = os.path.join(g4sh_dir, "geant4.sh")
        chdir(g4sh_dir)
        subprocess.call(g4sh)
        msg = """Consider adding 
            #### Geant 4
            source {}
            to your .bashrc
            """.format(g4sh)
        return [["echo", msg]]


if __name__ == "__main__":
    GeantInstaller(
            multithreaded=False,
            build_type="Release",
            python=False,
            qt=False,
            tag="v10.3.3",
            install_data=True,
            ).run()
