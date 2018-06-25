# How to create partie_hat


## Step 1. Create the FOCUS taxonomy file

I started with our [spreadsheet of annotated PATRIC data](patric_metadata_20180526_environments.tsv) and kept only those rows for which we have an Environment annotated in a sheet called [patric metadata 20180526 environments only](patric_metadata_20180526_environments_only.tsv).

Then, I selected just the first few columns of that spreadsheet to get the PATRIC ID, Organism name, taxonomy ID, etc. That way I'm working with a smaller spreadsheet for the rest of the work. This is a smaller file called [patric organisms](patric_organisms.tsv)
 
```
cut -f 1,2,3,4 patric_metadata_20180526_environments_only.tsv > patric_organisms.tsv
```

Next, I add the taxnomy to that file using the `patric_add_taxonomy.py` script from the [Edwards Lab repo](https://github.com/linsalrob/EdwardsLab).


```
python3 /home3/redwards/EdwardsLab/ncbi/patric_add_taxonomy.py -f patric_organisms.tsv -o patric_organisms_taxonomy.tsv 
```

To make sure all the rows have the same number of cells I use this perl oneliner:

```
perl -ne '@a=split /\t/; print "$#a\n"' patric_organisms_taxonomy.tsv | sort | uniq -c
```

FOCUS needs a file that has the source file name and then tab-separated values for _Kingdom, phylum, class, order, family, genus, species,_ and _strain_, but we don't have strain. Which is perfect, because I want to make sure we have included the PATRIC ID in our genome names in a way we can easily parse them from the FOCUS output. So I ammend the file with one more column for the strain.

```
perl -npe 'chomp; @a=split /\t/; $_.="\t$a[$#a] PATRIC|$a[0]\n"' patric_organisms_taxonomy.tsv > patric_organisms_taxonomy_strain.tsv
```

At this point I just manually edit the first line to change the column header of the last column to _strain_.

Now our strain information looks something like this for a _Salmonella Typhimurium_ strain:

| PATRIC ID | Name | Tax ID | Kingdom | phylum | class | order | family | genus | species | strain |
|---|---|---|---|---|---|---|---|---|---|--- |
| 28901.1301 | Salmonella enterica strain CFSAN045023 | 28901 | Bacteria | Proteobacteria | Gammaproteobacteria | Enterobacterales | Enterobacteriaceae | Salmonella | Salmonella enterica | Salmonella enterica PATRIC&#124;28901.1301

Note that the species includes PATRIC|genomeid.

## Step 2. Make new _k_-mer databases for FOCUS

We want to make a set of _k_-mer databases for [FOCUS](https://github.com/metageni/focus) that just have our well annotated bacteria in them.

I edited focus to allow users to specify their own database locations by adding a -b tag. This means we can run focus.py in parallel and process a lot of genomes at once. There are a couple of options for this, but for this option I'm going to use a multicore machine and use 30 different processes. _[Note: I've created a GitHub pull request for this, but you can also use my fork of FOCUS]_

By default, focus provides three different database sizes, _k_=6, _k_=7, and _k_=8. Each database has the first line dedicated to a header line, that has the taxonomic groups (kingdom, phylum, class, order, family, genus, species, and strain), and the remaining columns as the _k_-mer sequences. Then we have one entry per line that has the organism information and the counts associated with that organism. We can reuse the header lines from other files as necessary, and add our own organisms and counts to that file.


To create the focus databases, first, we rename the first column in the file to make it a pointer to a fasta file that we want to count k-mers for. We also use this opportunity to remove the extraneous columns from the file

```
perl -npe '@a=split /\t/; $a[0] = "\$HOME/PATRIC/fna/$a[0].fna"; splice(@a, 1, 3), $_=join("\t", @a)' patric_organisms_taxonomy_strain.tsv > files_to_process.txt
```

We now have a file called `files_to_process.txt` that has one entry per line that is only the filenames and taxa, including our new species designation. Note that to get here we used several intermediate files, if desired we could clean those up now. 

I want to process these in parallel since I have a machine with lots of memory and lots of cores. In this case, I'm going to run 30 jobs simultaneously. 

Let's start by splitting the input file, `files_to_process.txt` into 30 smaller files. It's easier if each of those has a numeric file name, and we want to ensure that the files are split by number of lines, rather than by number of bytes, so that each file starts and ends with a complete command. We use the `split` command for that:
 
```
split -d -l 2351 files_to_process.txt
```

This makes a series of files named x00, x01, x02, ... x28, x29.


Because we are going to process everything simultaneously it is much easier if we move everything to its own directory. We can always concatenate everything later (and we will ...). Lets make 30 directories, move the split files into those directories and rename them to input (in their own directories we don't mind if they all have the same name), and while we're at it make the db directory that focus needs to add to the database. The last thing focus needs is the first line of the database that just contains the header information. We'll steal that from another focus database while we're at it.

 
```
for JOB in $(seq 1 30); do
	mkdir $JOB;
	mv x$JOB $JOB/input;
	mkdir -p $JOB/output/db;
	for K in 6 7 8; do
		head -n 1 /usr/local/genome/focus/current/db/k$K > $JOB/output/db/k$K;
	done;
done
```

Notice that this did most of it, but there were a few errors. Split uses x00, x01, x02, ... and so we need to move those few files separately:

```
for JOB in $(seq 1 9); do mv x0$JOB $JOB/input; done
```

and finally the last one (just because I counted from 1 not 0 earlier):

```
mv x00 30/input
```
 

Now that we're all set with an input file, an output directory, and the basis of the _k_-mer database in each directory, we can run the same command each time. Note that I use the ampersand here to put the job in the background, but because I'm doing that in a _for_ loop I use echo to carry on.

```
CWD=$PWD; for JOB in $(seq 1 30); do cd $JOB; python2.7 ~/GitHubs/FOCUS/focus.py -b output/ -d input > stdout 2> stderr & echo $JOB; cd $CWD; done
```

We now have 30 instances of focus building us databases!

### Combine the _k_-mer databases

Once the processing is complete we need to combine the _k_-mer databases. Recall that each database has a header with the phylogenetic classification followed by the _k_-mer sequence, so we need to get that first. Then we can just concatenate the sequences from the partial databases. The order of the sequences in the databases doesn't matter.

```
for K in 6 7 8; do echo $K; head -n 1 1/output/db/k$K > db/k$K; grep -hv ^Kingdom &#42;/output/db/k$K >> db/k${K}.full; done
```

Then we need to filter out entries that are all zero. There is no point in keeping them in the database and we don't need to parse them each time we load it. These entries exist when the fasta file for the genome doesn't exist.

```
for K in 6 7 8; do perl -ne 'if (/^Kingdom/) {print; next} @a=split /\t/; $c=0; map {$c+=$a[$&#95;]} (9 .. $#a); print if ($c > 0)' db/k${K}.full > db/k$K; done
```

# Run FOCUS on a (some) metagenomes

Finally, we want to run FOCUS on some of the metagenomes to predict what environment they came from.

If we have a fastq file, we need to convert that to fasta, before we can start. For example, with a directory of fasta files, we can use:

```
for i in $(ls crAssphage&#95;fastq/); do echo $i; o=$(echo $i | sed -e 's/fastq.gz/fasta/'); gunzip -c crAssphage&#95;fastq/$i | fastq2fasta - crAssphage&#95;fasta/$o; done
```

and to run focus we can use one of two incantations:

For a single fasta file, you can call it directly.

For example:

```
python ~/GitHubs/FOCUS/focus.py  -b ./ -q crAssphage_fasta/SRR1462480_pass_2.fasta -m 0.00001
```

or for multiple fasta files in a directory you can run in STAMP mode, which creates tab-separated sheets with the output.

For example:

```
python ~/GitHubs/FOCUS/focus.py  -b ./ -q crAssphage_fasta/ -m 0.00001
```

I have placed the 7-mer file (which is the only one you need) on the web at [https://edwards.sdsu.edu/data/FOCUS/db_20180613/k7.gz](ttps://edwards.sdsu.edu/data/FOCUS/db_20180613/k7.gz)

# Run FOCUS on all the metagenomes

To do this, you'll need something like a large compute cluster, or perhaps access to [JetStream](https://kb.iu.edu/d/bfde)
from [xsede](https://portal.xsede.org). 

Start by installing FOCUS, the database, and a couple of dependencies using [the install script](install_focus.sh). This is quite straightforward, basically we download FOCUS from its
[git repo](https://github.com/linsalrob/FOCUS). We download our unique 7-mer database we created above and install that into the FOCUS working directory. Note that we only download and use the 7-mer database.
 Since we are not going to use 6- or 8-mers, we don't download or install them. Next, we install []Jellyfish](http://www.genome.umd.edu/jellyfish.html) ( version >= 2.0). Finally, because for this work we are going to deal 
with a lot of fastq files, we also install a simple [fastq-to-fasta](https://raw.githubusercontent.com/linsalrob/EdwardsLab/master/bin/fastq2fasta.cpp) converter that I wrote. This takes two parameters on
the command line: the first is either a file name or a hyphen to read from STDIN, the second is the filename to write the fasta output to.

Once we are set with the installation, we need a list of fastq ids to process. For this work we are going to process all the fastq files from every metagenome in the SRA &ndash; approximately 100,000 data sets! Our `ids.txt` file has
one fastq file per line, and all the fastq files are compressed with gzip.

The process that we complete, and is coded in [run_focus.sh](run_focus.sh) is
1. for each file we need to figure out the SRA ID (the name without fastq.gz) and a fasta output filename. We do these with sed
2. Uncompress the appropriate fastq file (note: you will need to change the path here!) and convert that to fasta using fastq2fasta
3. Run focus on the fasta file using our new database, ensuring that we increase (decrease?) the minimum percentage to 0.001 to get the rare species
4. Remove the fasta file &ndash; we don't need it anymore! 
5. Rename the output file and compress it using gzip

# Parse the output of FOCUS

Now that we have a directory of focus output files we want to create a table that has just the metagenome IDs (which we can get from the filename), and 
the genome ids (which we can get from the FOCUS output), and the abundance of that genome in that metagenome.

The code [parse_focus](parse_focus.py) reads all the files in the directory and creates just such a tsv file. It will take a while to run this code
as it has to iterate through every genome (tens of thousands) and every metagenome (also tens of thousands), so maybe go grab lunch ... or run it over night!

Once it is complete, we have a file that we can open in our favorite spreadsheet program ... well, almost. Remember it is thousands of entries by thousands of entries.

# Find some interesting metagenomes

We want to classify the metagenomes based on the abundance of genomes in the data. Before we try on the whole data set, we should try on just a few metagenomes.
Of course, it will be easiest to classify a few metagenomes if the abundance of bacteria in them is obvious - we'll know that we're getting the right answer! 

We can run this command:

```angular2html
	python3 ~/GitHubs/partie_hat/find_examples.py \
		-e patric_metadata_20180526_isolation_host_env.tsv \
		-f metagenome_counts_20180625.txt \
		-o dev_counts_sel.tsv \
		-c dev_counts_sel_envcounts.json \
		-m 75
```

The parameters here are:
* _-e_ the environments file that just has the tuple [genome id, isolation source, host, environment]
* _-f_ the metagenome counts that are generated by [parse_focus](parse_focus.py) 
* _-o_ the output file to write for the portion of the data. This file has the same format as the original full matrix but will be a lot quicker to load
* _-c_ a JSON file that has the metagenome IDs used and the sum of the percentages of each environment. The numbers should add up to 100%
* _-m_ the minimum percentage of the most abundant environment for us to keep this sample. If you increase this you will get fewer samples, and they will be more obviously from a single environment.
 The default is 90% which means the most abundant environment must contain 90% of the bacteria in the metagenome.


[**_Note_**: this code has a random factor, in that it only stores a subset of the data. Therefore each time you run it you will get different answers. Unless you always run it with -n >= the number of metagenomes you have!]

  

This command will create two files [dev_counts_sel](dev_counts_sel.tsv) and [dev_counts_sel_envcounts](dev_counts_sel_envcounts.json) that we are interested in. 







