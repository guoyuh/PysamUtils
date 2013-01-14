#!/usr/bin/env python
import pysam
import sys
from optparse import OptionParser
""" 
I want to do a hard filter against a variant catalog.  Print only those records that are not present in a
catalog VCF, like 1000G, dbSNP, ESP-GO variant catalogs.

I use the Tabix API from Pysam <http://code.google.com/p/pysam/>

Make sure the VCF files have been compressed using bgzip (which is part of the Tabix)
To download Tabix, go here <http://sourceforge.net/projects/samtools/files/tabix/>
For more information on bgzip see this: http://blastedbio.blogspot.com/2011/11/bgzf-blocked-bigger-better-gzip.html

"""

def main():

    if pysam.__version__ != '0.7':
        sys.stderr.write("need pysam version 0.7\n")
        sys.exit()


    usage = "%prog --catalogVcf catalog.vcf file.vcf\n\nhard filter records in file.vcf against  catalog.vcf\n"
    parser = OptionParser(usage)
    parser.add_option("--catalogVcf", type="string", dest="catalogvcf", default=None, help="VCF file of variant catalog to hard filter against")
    parser.add_option("--v", action="store_true", dest="reverse",  help="Print records that are present in variant catalog")

    (options, args)=parser.parse_args()
    vcfile=args[0]
    pysamTbi= pysam.Tabixfile(vcfile, "r")
    catalogTbi=pysam.Tabixfile(options.catalogvcf, "r")
    for row in pysamTbi.fetch():
        fields=row.split("\t")
        chr=fields[0]
        start=int(fields[1])-1
        end=start+1
    #print chr,start,end
    #print row
        regionstr=str(chr)+":"+str(start)+"-"+str(end)
        try:
            tabixrow=catalogTbi.fetch(regionstr).__next__()
            if options.reverse == True: print row
        except:
            if not options.reverse: print row 


if __name__ == "__main__":
    main()
