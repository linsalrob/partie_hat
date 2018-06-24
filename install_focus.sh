
##############################################################################
#                                                                            #
# install_focus.sh                                                           #
#                                                                            #
# Install FOCUS on a new linux installation                                  #
#                                                                            #
# This script assumes you have a bare-bones centos or ubuntu installation    #
# and want to install focus with our novel 7-mer database that covers strain #
# sources and environments.                                                  #
# We also install two requirements - one for focus: jellyfish and one for    #
# analyzing DNA sequences - fastq2fasta.                                     #
#                                                                            #
# (c) Rob Edwards, 2018                                                      #
#                                                                            #
##############################################################################

export PATH=$PATH:$HOME/bin
echo "export PATH=$PATH:$HOME/bin" >> ~/.bashrc
sudo pip2.7 install numpy scipy

# INSTALL FOCUS AND GET THE DATABASE
git clone https://github.com/linsalrob/FOCUS.git
mkdir -p FOCUS/db
cd FOCUS/db
curl -ko k7.gz https://edwards.sdsu.edu/data/FOCUS/db_20180613/k7.gz 
gunzip k7.gz  &

# INSTALL FASTQ2FASTA and JELLYFISH
mkdir ~/bin
cd ~/bin
curl -o fastq2fasta.cpp https://raw.githubusercontent.com/linsalrob/EdwardsLab/master/bin/fastq2fasta.cpp
c++ -o fastq2fasta fastq2fasta.cpp 
curl -Lo jellyfish https://github.com/gmarcais/Jellyfish/releases/download/v1.1.12/jellyfish-linux
chmod +x jellyfish 

mkdir ~/process
cd ~/process
