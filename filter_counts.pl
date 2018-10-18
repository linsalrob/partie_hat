# Filter the metagenome count files for selected entries
#
# We use this to filter any extraneous entries that are not WGS

use strict;

my $wgs = shift || die "file with one id per line for entries we want to KEEP";
open(IN, $wgs) || die "Can't open $wgs";
my %s;
while(<IN>) {
	chomp;
	$s{$_}=1;
}
close IN;

my $f=shift || die "file to filter?";
open(IN, $f) || die "$f ??";
my $l=<IN>;
chomp($l);
my @h=split /\t/, $l;
my @want = (0);
for my $i (1 .. $#h) {if ($s{$h[$i]}) {push @want, $i}}
print STDERR "Keeping ", $#want, " out of ", $#h, " entries\n";

my @o;
map {push @o, $h[$_]} @want;
print join("\t", @o), "\n";


while (<IN>) {
	chomp;
	@h=split /\t/;
	undef @o;
	map {push @o, $h[$_]} @want;
	print join("\t", @o), "\n";

}
close IN;
