# Filter the metagenome json files for selected entries
#
# We use this to filter any extraneous entries that are not WGS

use strict;

my $wgs = shift || die "file with one id per line for entries we want to KEEP";
my %s;
open(IN, $wgs) || die "Can't open $wgs";
while(<IN>) {
	chomp;
	$s{$_}=1;
}
close IN;

my $f=shift || die "file to filter?";
open(IN, $f) || die "$f ??";
while (<IN>) {
	my @a=split /\t/;
	print if ($s{$a[0]});
}
close IN;
