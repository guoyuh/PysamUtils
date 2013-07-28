#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser
from common import return_file_basename
import pysam


def main():
    """ reassign mapping qualities in a bam file """
    
    
    usage = "usage: %prog [options] file.bam"
    parser = OptionParser(usage)
    parser.add_option("--DMQ", type="int", dest="dmq", default=60, help="default mapping quality to set")
    
    
    (options, args)=parser.parse_args()    


    bamfilename=args[0]
    basename=return_file_basename(bamfilename)
    pybamfile = pysam.Samfile(bamfilename, "rb" )
    
    bamfile_withRG_name=basename+".dmq.bam"
    dmqbamfile = pysam.Samfile(bamfile_withRG_name, "wb", header=pybamfile.header)
    
    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)
        
    sys.stderr.write("writing new bam file with new default mapping quality tag  alignment record  ...\n")
    
    for read in pybamfile.fetch():
        read.mapq = options.dmq
        dmqbamfile.write(read)
    
    


if __name__ == "__main__":
    main()