//========================================================================
// ubmark-vvadd
//========================================================================

#include "common.h"
#include "stdio.h"

//------------------------------------------------------------------------
// vvadd-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void vvadd_scalar( int *dest, int *src0, int *src1, int size )
{
  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = src0[i] + src1[i];
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
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

int src0[105], src1[105], ref[105];
int main( int argc, char* argv[] )
{
  int dest[105], size;
  FILE *f = fopen("/home/sj634/workspace/pymtl-v3-designs/app/ubmark/ubmark-vvadd-fileio.dat", "r");

  fscanf(f, "%d", &size);
  int i;
  for (i=0; i<size; ++i) 
    dest[i] = 0;

  for (i=0; i<size; ++i) 
    fscanf(f, "%d", &src0[i]);

  for (i=0; i<size; ++i) 
    fscanf(f, "%d", &src1[i]);

  for (i=0; i<size; ++i) 
    fscanf(f, "%d", &ref[i]);

  test_stats_on();
  vvadd_scalar( dest, src0, src1, size );
  test_stats_off();

  verify_results( dest, ref, size );

  return 0;
}
