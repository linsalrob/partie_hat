
##############################################################################
#                                                                            #
# run_focus.sh                                                               #
#                                                                            #
# This script is designed to process a file called ids.txt and run           #
# focus on each entry in that file. Note we assume that ids.txt              #
# has one fastq.gz file per line. We convert that to fasta                   #
# and then run focus, remove the fasta file, and compress the                #
# focus output.                                                              #
#                                                                            #
# (c) Rob Edwards, 2018                                                      #
#                                                                            #
##############################################################################




export PATH=$PATH:$HOME/bin
mkdir -p process
cd process
for FQ in $(cat ../ids.txt); do
	ID=$(echo $FQ | sed -e 's/.fastq.gz//') 
	FA=$(echo $FQ | sed -e 's/.fastq.gz/.fasta/')
	gunzip -c  /nas/wrangler/NCBI/SRA/Downloads/fastq/$FQ | ~/bin/fastq2fasta - $FA
	python2.7 ~/FOCUS/focus.py -m 0.001 -q $FA
	rm $FA
	mv ${FA}__output.txt ${ID}_focus.txt
	gzip ${ID}_focus.txt
done

