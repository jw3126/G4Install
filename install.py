from subprocess import run

class Installer(object):

    def __init__(;
        qt,
        gdml,
        datadir,
        build_path="build",
        source_path="source",
        origin="https://github.com/Geant4/geant4.git",
        install_path="install",

        ):  

        commands = ["git clone {origin} {source}".format(**locals())]

        packages = ["cmake", "gcc", "g++", "make"]

        cmake_options = {
            "DGEANT4_INSTALL_DATA":"ON",
            "DCMAKE_BUILD_TYPE":"Release",
            "DCMAKE_INSTALL_PREFIX": ,
        
            }

        if gdml:
            packages.append("libxerces-c-dev")
            cmake_options["DGEANT4_USE_GDML"]="ON"

        if qt:
            packages.append("qt5-default")
            cmake_options["DGEANT4_USE_QT"]="ON"

        if datadir is not None:
            cmake_options["DGEANT4_INSTALL_DATADIR"]=datadir


        self.packages = packages
        self.cmake_options = cmake_options
        self.commands = commands
    

    def install_dependencies(self):
        run(["sudo apt-get install]" + self.packages])


    def install_geant4(self):
        cmd = "cmake" 
        


