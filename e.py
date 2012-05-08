#!/usr/bin/python

from optparse import OptionParser,OptionGroup
from esymmetric import *

op = OptionParser()

op.add_option("-i","--input",action="store",dest="input",help="Set the input file to be handled.")
op.add_option('-n','--new',action='store_true',dest='new',default=False,help='Generate a new SYMKEY when -s/--symmetric provided.')

group_symmetric = OptionGroup(op,'Symmetric Cipher Services','Provides symmetric encrypting and decrypting services.')
group_symmetric.add_option('-s','--symmetric',action='store_true',dest='symmetric',default=False,help='Tell me you are going to use functions under this service group.')

op.add_option_group(group_symmetric)

(options,args) = op.parse_args()

# Read verbose.
if options.symmetric == True:
    print "Will do symmetric jobs."
    if options.new == True:
        print "Will generate a new peerkey."
else:
    print "No verbose options received, not knowing what to do.\nYou may ask for help by adding --help option."
