//========================================================================
// ubmark-matmul
//========================================================================

#include "common.h"
#include "ubmark-matmul.dat"

//------------------------------------------------------------------------
// matmul-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void matmul_scalar( int N, int C[][size], int A[][size], int B[][size] )
{
  int i, j, k;
  for (i=0; i<N; ++i)
  for (j=0; j<N; ++j)
  {
    C[i][j] = 0;
    for (k=0; k<N; ++k)
      C[i][j] += A[i][k] * B[k][j];
  }
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int N, int dest[][size], int ref[][size] )
{
  int i, j;
  for (i=0; i<N; ++i)
  for (j=0; j<N; ++j)
    if ( !( dest[i][j] == ref[i][j] ) ) {
      test_fail( i*N+j, dest[i][j], ref[i][j] );
    }
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  int dest[size][size];

  int i, j;
  for (i=0; i<N; ++i)
  for (j=0; j<N; ++j)
    dest[i][j] = 0;

  test_stats_on();
  matmul_scalar( N, dest, A, B );
  test_stats_off();

  verify_results( N, dest, ref );

  return 0;
}
