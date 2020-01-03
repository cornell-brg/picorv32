#!/usr/bin/env python
#===============================================================================
# gen-matmul-matrices.py
#===============================================================================
# Generate random numbers for matrix multiplication benchmark (require numpy!)
#
#  -h --help     Display this message
#  -n --size N   size = N
#  
# Author : Shunning Jiang
# Date   : November 2, 2017

import argparse
import fileinput
import sys
import re
import math
import random

#-------------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------------

class ArgumentParserWithCustomError(argparse.ArgumentParser):
  def error( self, msg = "" ):
    if ( msg ): print "\n ERROR: %s" % msg 
    print ""
    file = open( sys.argv[0] )
    for ( lineno, line ) in enumerate( file ):
      if ( line[0] != '#' ): sys.exit(msg != "")
      if ( (lineno == 2) or (lineno >= 4) ): print line[1:].rstrip("\n")

def parse_cmdline():
  p = ArgumentParserWithCustomError( add_help=False )
  p.add_argument( "-h", "--help", action="store_true" )
  p.add_argument( "-n", "--size", type=int, dest="size", required=True )

  opts = p.parse_args()
  if opts.help: p.error()
  return opts

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
  opts = parse_cmdline()

  test_out = open( "ubmark-matmul.dat", "w" )

  test_out.write( "// Data set for matrix multiplication\n\n" );

  import numpy as np

  A = [ [ random.randint(0,1000) for _ in xrange(opts.size) ]
          for _ in xrange(opts.size) ]

  try:

    test_out.write( "int N = %d;\n" % opts.size );
    test_out.write( "const int size = %d;\n\n" % opts.size );

    test_out.write( "int A[][size] = {\n" );

    A = []
    for i in xrange( opts.size ):
      a = []
      test_out.write( "{" )
      for j in xrange( opts.size ):
        x = random.randint( 0, 1000 )
        a.append( x )
        test_out.write( " " + str( x ) )
        if j < opts.size-1:
          test_out.write( "," )

      A.append(a)
      if i < opts.size-1:
        test_out.write( "},\n" )
      else:
        test_out.write( "}" )

    test_out.write( "\n};\n\n" );

    test_out.write( "int B[][size] = {\n" );

    B = []

    for i in xrange( opts.size ):
      b = []
      test_out.write( "{" )
      for j in xrange( opts.size ):
        x = random.randint( 0, 1000 )
        b.append( x )
        test_out.write( " " + str( x ) )
        if j < opts.size-1:
          test_out.write( "," )

      B.append(b)
      if i < opts.size-1:
        test_out.write( "},\n" )
      else:
        test_out.write( "}" )

    test_out.write( "\n};\n\n" );

    C = np.dot( np.matrix(A), np.matrix(B) ).tolist()

    test_out.write( "int ref[][size] = {\n" );

    for i in xrange( opts.size ):
      test_out.write( "{" )
      for j in xrange( opts.size ):
        test_out.write( " " + str( C[i][j] ) )
        if j < opts.size-1:
          test_out.write( "," )

      if i < opts.size-1:
        test_out.write( "},\n" )
      else:
        test_out.write( "}" )

    test_out.write( "\n};\n\n" );

  finally:

    test_out.close()

main()

