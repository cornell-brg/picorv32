//========================================================================
// ubmark-vvadd
//========================================================================

#include "common.h"
#include "ubmark-vvdivrem.dat"

//------------------------------------------------------------------------
// vvadd-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void vvdiv_scalar( unsigned *dest, unsigned *src0, unsigned *src1, int size )
{
  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = src0[i] / src1[i];
}

__attribute__ ((noinline))
void vvrem_scalar( unsigned *dest, unsigned *src0, unsigned *src1, int size )
{
  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = src0[i] % src1[i];
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( unsigned dest[], unsigned ref[], int size )
{
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( i, dest[i], ref[i] );
    }
  }
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  unsigned dest_divu[size], dest_remu[size];

  int i;
  for ( i = 0; i < size; i++ )
    dest_divu[i] = dest_remu[i] = 0;

  test_stats_on();
  vvdiv_scalar( dest_divu, src0, src1, size );
  vvrem_scalar( dest_remu, src0, src1, size );
  test_stats_off();

  verify_results( dest_divu, ref_divu, size );
  verify_results( dest_remu, ref_remu, size );

  return 0;
}
