//========================================================================
// ubmark-bubblesort
//========================================================================

#include "common.h"
#include "ubmark-quicksort.dat"

int gap[] = {40, 13, 4, 1, 0};

__attribute__ ((noinline))
void shellsort(int* dest, int* src, int size)
{
  int i,j,jj,k=0,g,l,swap;

  for ( i = 0; i < size; i++ )
    dest[i] = src[i];

  while (gap[k] >= size) ++k;

  while (g = gap[k++])
    for (i=g; i<size; ++i)
    {
      swap = dest[i];
      jj = i;
      j  = i-g;
      while (j >= 0)
      {
        l = dest[j];
        if (l <= swap) break;
        dest[jj] = l;
        jj = j;
        j -= g;
      }
      dest[jj] = swap;
    }
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

int main( int argc, char* argv[] )
{
  int dest[size];

  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = 0;

  test_stats_on();
  shellsort( dest, src, size );
  test_stats_off();

  verify_results( dest, ref, size );

  return 0;
}

