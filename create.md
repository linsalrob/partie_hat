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
| 28901.1301 | Salmonella enterica strain CFSAN045023 | 28901 | Bacteria | Proteobacteria | Gammaproteobacteria | Enterobacterales | Enterobacteriaceae | Salmonella | Salmonella enterica | Salmonella enterica PATRIC\|28901.1301

Note that the species includes PATRIC|genomeid.
