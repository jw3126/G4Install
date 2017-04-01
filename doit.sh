#!/bin/bash
# This script installs geant4

# various paths
BASE=`pwd`
BUILD=$BASE/build # this is where the build files are stored
INSTALL=$BASE/install
SRC=$BASE/source # this is where the geant4 source code lies
DATADIR=$BASE/datadir
ORIGIN=https://github.com/Geant4/geant4.git
GEANT4SH=$INSTALL/bin/geant4.sh

mkdir $BUILD
mkdir $INSTALL
mkdir $SRC

# get prerequisites
sudo apt-get install cmake gcc g++ make --yes
sudo apt-get install qt5-default --yes
sudo apt-get install libexpat1-dev --yes

sudo apt-get install libxerces-c-dev --yes # for gdml


# get source and setup directories
git clone $ORIGIN $SRC



# the actual build
cd $BUILD 

# See
# http://geant4.web.cern.ch/geant4/UserDocumentation/UsersGuides/InstallationGuide/html/ch02s03.html
# for build options
cmake -DCMAKE_INSTALL_PREFIX=$INSTALL $SRC\
    -DGEANT4_INSTALL_DATA=ON\
    -DGEANT4_INSTALL_DATADIR=$DATADIR\
    -DGEANT4_USE_QT=ON\
    -DCMAKE_BUILD_TYPE=Release\
    -DGEANT4_BUILD_MULTITHREADED=OFF\
    -DGEANT4_USE_GDML=ON\

cd $BUILD

make -j4
make install

cd $BASE

source $GEANT4SH
echo consider adding 
echo source $GEANT4SH 
echo to your .bashrc


# G4PY
# sudo apt-get install libboost-all-dev --yes  # for g4py
# python does not like multi threading mode
sudo apt-get install libboost-python-dev --yes
export GEANT4_INSTALL=$INSTALL

G4PYBUILD=$SRC/environments/g4py/build
cd $G4PYBUILD
cmake ..
make
