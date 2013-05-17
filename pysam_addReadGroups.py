#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser
from common import return_file_basename
import pysam

def main():
    """ add a the RG tag to the sam/bam record as well as update the header
        right now assumes single sample in the sam/bam file so can only add one RG/SM tag
        output is written to file.RG.bam based on the input file.bam prefix """
    usage = "usage: %prog [options] file.bam"
    parser = OptionParser(usage)
    parser.add_option("--RG", type="string", dest="rgid", help="readgroup id")
    
    parser.add_option("--SM", type="string", dest="sm",  help="sample name")
    parser.add_option("--PL", type="string", dest="pl", default="illumina",  help="platform unit (of sequencing)")
    parser.add_option("--PI", type="string", dest="pi", default="350",help="insert size" )
    (options, args)=parser.parse_args()    


    bamfilename=args[0]
    basename=return_file_basename(bamfilename)
    
    
                    
    
    pybamfile = pysam.Samfile(bamfilename, "rb" )
    newheader=pybamfile.header
    newheader['RG']=[{'PI': options.pi, 'ID': options.rgid, 'PL': options.pl, 'SM': options.sm}]
    #print newheader
    bamfile_withRG_name=basename+".RG.bam"
    rgreads = pysam.Samfile(bamfile_withRG_name, "wb", header=newheader)
    
    
    
    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)
    
    sys.stderr.write("writing new bam file with RG tag in record and header ...\n")
    for read in pybamfile.fetch():
        read.tags = read.tags + [("RG",options.rgid)]
        rgreads.write(read)
    

    
if __name__ == "__main__":
    main()

