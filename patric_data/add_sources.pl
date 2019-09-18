use strict;

my %env;
open(IN, "isolation_sources.tsv") || die "$! isolation_sources.tsv";
while (<IN>) {
	chomp;
	my @a=split /\t/;
	$env{$a[0]}=$a[1];
}
close IN;

$env{"isolation_source"} = "environment";

open(IN, "gunzip -c patric_metadata.tsv.gz |") || die "$! reading from patric_metadata.tsv.gz";
open(OUT, "| gzip > patric_metadata_environments.tsv.gz") || die "$! Writing to gzip";
open(GE, ">patric_genomes_environments.tsv") || die "$! patric_genomes_environments.tsv";
while (<IN>) {
	chomp;
	my @a=split /\t/;
	if ($env{lc($a[35])}) {$a[66] = $env{lc($a[35])}}
	else {$a[66] = ""}
	print OUT join("\t", @a), "\n";
	if ($a[66]) {print GE join("\t", @a[0 .. 3, 35, 66]), "\n"}
}
close IN;
close OUT;
close GE;



