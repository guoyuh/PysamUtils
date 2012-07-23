#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser
import pysam

def yield_bedcoordinate(fh):
    """" yield a tuple of (chr, start,end) from bed file """
    for line  in fh:
        if '@' in line: continue
        fields=line.strip().split("\t")
        (chr, start, end) = fields[0:3]
        yield(chr, int(start), int(end) )

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--bedfile", type="string", dest="bedfile", help="bedfile")
    (options, args)=parser.parse_args()

    bedfh=open(options.bedfile, 'r')

    bamfilename=args[0]

    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)
    pybamfile = pysam.Samfile(bamfilename, "rb" )

    samfile = pysam.Samfile('random.bam', "rb" )
    header_keys=samfile.header.keys()
    readgroupToSample={}
    sampleset=[]
    for readgroup in  samfile.header['RG']:
        print readgroup
        readgroupToSample[ readgroup['ID'] ]=readgroup['SM']
        sampleset.append( readgroup['SM'] )
    sampleset=list( set(sampleset) )
    print sampleset


    for (chrom, start, end) in yield_bedcoordinate(bedfh):
        for pileupcolumn in pybamfile.pileup(chrom, start, end ):
            
            for pileupread in pileupcolumn.pileups:
                tags= dict( pileupread.alignment.tags )
                rg=tags['RG']
                if rg not in readgroupToSample.keys():
                    sys.stderr.write(rg +  " not in header of BAM!\n")
                    continue
            print 'coverage at base %s = %s %s %s' % (pileupcolumn.pos , pileupcolumn.n, rg,readgroupToSample[rg] )

    
    
if __name__ == "__main__":
    main()
