# PATRIC Data

We combine our SRA data with the data from the [PATRIC BRC](https://www.patricbrc.org/) to identify where bacteria come from and how they might be aligned in the environment.

We start with the [PATRIC metadata](ftp://ftp.patricbrc.org/RELEASE_NOTES/genome_metadata) (166MB) (a tab-separated values file that has all the metadata for the organisms in PATRIC) and our [isolation sources](isolation_sources.tsv) file that has the isolation source text and our controlled vocabulary environment that describes that isolation source.

* [PATRIC metadata](patric_metadata.tsv.gz) this is the version of the PATRIC metadata that we used to create the subsequent files.
* [metadata and environments](patric_metadata_environments.tsv.gz) has that PATRIC metadata together with the environment listed in our [isolation sources](isolation_sources.tsv) file. Basically we join those two files on the first column from isolation sources and the 36th column from the metadata file. This contains all the entries in  [PATRIC metadata](patric_metadata.tsv.gz) whether or not they have an environment.
* [genomes environments](patric_genomes_environments.tsv) has tuples of [genome id, genome name, organism name, taxon id, isolation source, Environment]. This only contains those organisms for which the environment is currently annotated.
