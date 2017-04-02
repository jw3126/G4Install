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
            self.packages.append("libboost-python-dev")
            self.build_steps.append(self.python)

        self.build_steps.append(self.finish)

    def mkdirs(self):
        for path in self.path.values():
            os.makedirs(path,exist_ok=True)


    def clone(self):
        cmd =["git", "clone", self.origin, self.path["source"], ]
        print(cmd)
        run(cmd)


    def dependencies(self):
        run(["sudo", "apt-get", "install"] + self.packages + ["--yes"])


    def cmake(self): 
        chdir(self.path["build"])
        cmd = ["cmake", self.path["source"], ]
        cmd += ["-{}={}".format(key, val) for (key, val) in self.cmake_options.items()]
        run(cmd)


    def make(self):
        chdir(self.path["build"])
        run(["make", "-j4"])
        run(["make", "install"])


    def python(self):
        py_build_path = os.path.join(self.path["source"], "environments", "g4py", "build")
        os.makedirs(py_build_path, exist_ok=True)
        chdir(py_build_path)
        os.environ["GEANT4_INSTALL"] = self.path["install"]
        run(["cmake", ".."])
        run(["make", "-j4"])
        run(["make", "install"])

    
    def run(self):
        for step in self.build_steps:
            step()

    def finish(self):
        g4sh_dir = os.path.join(self.path["install"], "bin")
        g4sh = os.path.join(g4sh_dir, "geant4.sh")
        chdir(g4sh_dir)
        subprocess.call(g4sh)
        msg = """Consider adding 
            source {}
            to your .bashrc
            """.format(g4sh)
        print(msg)


if __name__ == "__main__":
    Installer(
            multithreaded=False,
            python=True
            ).run()

