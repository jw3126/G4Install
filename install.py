#!/usr/bin/python3
from subprocess import run
import subprocess
from os.path import abspath
from os import chdir
import os

class Installer(object):

    # http://geant4.web.cern.ch/geant4/UserDocumentation/UsersGuides/InstallationGuide/html/ch02s03.html
    def __init__(self,
        qt=True,
        gdml=True,
        datadir="datadir",
        build_path="build",
        source_path="source",
        origin="https://github.com/Geant4/geant4.git",
        install_path="install",
        python=False,
        multithreaded=True,
        build_py_path="build_py",
        ):  
        # Design:
        # The constructor does only bookkeeping.
        # It does not install anything, or create any directories 
        # or have other side effects
        #
        # The various methods are resposible for carrying out the actual build

        self.origin = origin
        self.path = {
                "source":abspath(source_path),
                "build":abspath(build_path),
                "install":abspath(install_path),
                }

        self.build_steps = [
                self.mkdirs,
                self.clone,
                self.dependencies,
                self.cmake,
                self.make]

        self.packages = ["cmake", "gcc", "g++", "make", "libexpat1-dev"]

        self.cmake_options = {
            "DGEANT4_INSTALL_DATA":"ON",
            "DCMAKE_BUILD_TYPE":"Release",
            "DCMAKE_INSTALL_PREFIX":self.path["install"],
            }

        if gdml:
            self.packages.append("libxerces-c-dev")
            self.cmake_options["DGEANT4_USE_GDML"]="ON"

        if qt:
            self.packages.append("qt5-default")
            self.cmake_options["DGEANT4_USE_QT"]="ON"

        if datadir is not None:
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


    def dependencies(self):
        return [(["sudo", "apt-get", "install"] + self.packages + ["--yes"])]


    def cmake(self): 
        chdir(self.path["build"])
        cmd = ["cmake", self.path["source"], ]
        cmd += ["-{}={}".format(key, val) for (key, val) in self.cmake_options.items()]
        return [cmd]


    def make(self):
        chdir(self.path["build"])
        return [["make", "-j4"], ["make", "install"]]


    def python(self):
        chdir(self.path["build_py"])
        os.environ["GEANT4_INSTALL"] = self.path["install"]
        cmake_path = os.path.join(self.path["source"], "environments", "g4py")
        return [["cmake", cmake_path], ["make", "-j4"], ["make", "install"]]

    
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
            source {}
            to your .bashrc
            """.format(g4sh)
        return [["echo", msg]]


if __name__ == "__main__":
    Installer(
            multithreaded=True,
            python=False
            ).run()
