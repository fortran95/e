#!/usr/bin/python

from optparse import OptionParser,OptionGroup

op = OptionParser()

op.add_option("-i","--input",action="store",dest="input",help="Set the input file to be handled.")

group_symmetric = OptionGroup(op,'Symmetric Cipher Services','Provides symmetric encrypting and decrypting services.')
group_symmetric.add_option('-s','--symmetric',action='store_true',dest='symmetric',help='Tell me you are going to use functions under this service group.')


op.add_option_group(group_symmetric)

(options,args) = op.parse_args()

#print options
