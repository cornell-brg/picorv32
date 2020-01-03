//========================================================================
// cgra_ubmark-fir.c
//========================================================================

#include "common.h"
#include "cgra_ubmark-fir.dat"

//------------------------------------------------------------------------
// fir
//------------------------------------------------------------------------

__attribute__ ((noinline))
int fir( int n, int data[], int coeff[] )
{
  int i, sum = 0;

  for ( i = 0; i < n; i++ )
    sum += data[i] * coeff[i];

  return sum;
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int sum, int ref_sum )
{
  if ( sum != ref_sum )
    test_fail( 0, sum, ref_sum );
  test_pass();
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  int sum;

  test_stats_on();
  sum = fir( n, data, coeff );
  test_stats_off();

  verify_results( sum, ref_sum );

  return 0;
}
