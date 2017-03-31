# This script installs geant4

# various paths
export BASE=`pwd`
export BUILD=$BASE/build # this is where the build files are stored
export INSTALL=$BASE/install
export SRC=$BASE/source # this is where the geant4 source code lies
export DATADIR=$BASE/datadir
export ORIGIN=https://github.com/Geant4/geant4.git
export GEANT4SH=$INSTALL/bin/geant4.sh

mkdir $BUILD
mkdir $INSTALL
mkdir $SRC

# get prerequisites
sudo apt-get install cmake gcc g++ make qt5-default --yes






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
    -DCMAKE_BUILD_MULTITHREADED=OFF\

cd $BUILD

make -j4
make install

cd $BASE

echo consider adding 
echo source $GEANT4SH 
echo to your .bashrc
