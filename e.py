#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
from optparse import OptionParser,OptionGroup
from esymmetric import *
from eexchanger import *

op = OptionParser()

op.add_option("-i","--input",action="store",dest="input",default=False,help="Set the input file to be handled.")
op.add_option("-o","--output",action="store",dest="output",default=False,help="Set output file.")
op.add_option('-n','--new',action='store_true',dest='new',default=False,help='Generate a new SYMKEY when -s/--symmetric provided.')

group_symmetric = OptionGroup(op,'Key Exchange Services','Provides authenticated symmetric-key exchanging service.')
group_symmetric.add_option('-e','--exchange',action='store_true',dest='exchange',default=False,help="Tell me you are going to use this functions")
group_symmetric.add_option('-l','--load-key',action='store_true',dest='loadkey',default=False,help="Load a new key from the file specified with --input.")

group_transfer = OptionGroup(op,'Symmetric Encryption Service','Provides encrypt/decrypt service with previously exchanged keys.')
group_transfer.add_option('-s','--symmetric',action='store_true',dest='symmetric',default=False,help="Tell me you're going to use this function.")

op.add_option_group(group_symmetric)

(options,args) = op.parse_args()

# Read verbose.
if options.exchange == True:
    #print "Will do symmetric jobs."
    if options.new == True:
        if options.output == False:
            print "Please specify a file to store your transfer-key with --output."
            exit()
        def ks_send(keys):
            return keySelect(keys,title='',description='即将签署一个新生成的通讯中继密钥。\n请选择您想要使用的PGP身份认证密钥。\n')
        def ks_recv(keys):
            return keySelect(keys,title='',description='请选择接收者的身份公钥。')
        newkey = send_new_key(ks_send,ks_recv)
        if newkey != False:
            f=open(options.output,'w+')
            f.write(newkey)
            f.close()
            print "New transfer key generated."
    elif options.loadkey == True:
        print 'will load a key'
        if options.input == False:
            print "Please specify a file to load from with --input."
            exit()
        f = open(options.input,'r')
        kf = f.read()
        f.close()
        r = load_new_key(kf)
        if r == True:
            print "New transfer key loaded."
else:
    print "No verbose options received, not knowing what to do.\nYou may ask for help by adding --help option."
