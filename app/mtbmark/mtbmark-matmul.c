//========================================================================
// ubmark-matmul
//========================================================================

#include "common.h"
#include "mtbmark-matmul-small.dat"

typedef struct {
  int   N;
  int (*C)[size];
  int (*A)[size];
  int (*B)[size];
  int   begin;
  int   end;
} arg_t;

//------------------------------------------------------------------------
// matmul-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void matmul_mt( void* arg_vptr )
{
  arg_t* arg_ptr = (arg_t*) arg_vptr;

  int   N = arg_ptr->N;
  int (*C)[size] = arg_ptr->C;
  int (*A)[size] = arg_ptr->A;
  int (*B)[size] = arg_ptr->B;
  int   begin = arg_ptr->begin;
  int   end   = arg_ptr->end;

  int i, j, k;

  for (i=begin; i<end; ++i)
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
  bthread_init();

  int dest[size][size];

  test_stats_on();

  int block_size = N;

  // starting from idx, the core does 1 more iteration
  int ncores = bthread_get_num_cores();
  int idx = ncores;

  if (ncores == 2)
  {
    block_size = N >> 1;
    idx = ncores - ( N - (block_size << 1) );
  }
  else
  if (ncores == 4)
  {
    block_size = N >> 2;
    idx = ncores - ( N - (block_size << 2) );
  }
  else
  if (ncores == 8)
  {
    block_size = N >> 3;
    idx = ncores - ( N - (block_size << 3) );
  }
  else
  if (ncores == 16)
  {
    block_size = N >> 4;
    idx = ncores - ( N - (block_size << 4) );
  }
  else
  if (ncores == 32)
  {
    block_size = N >> 5;
    idx = ncores - ( N - (block_size << 5) );
  }
  else
  if (ncores == 64)
  {
    block_size = N >> 6;
    idx = ncores - ( N - (block_size << 6) );
  }
  arg_t args[ncores];

  int current = 0;
  for (int i=0; i<ncores; ++i)
  {
    int end = current + block_size + (i>=idx);
    args[i].begin = current;
    args[i].end = current = end;

    args[i].N = N;
    args[i].C = dest;
    args[i].A = A;
    args[i].B = B;
  }

  for (int i=1; i<ncores; ++i)
    bthread_spawn( i, &matmul_mt, &args[i] );

  matmul_mt( &args[0] );

  for (int i=1; i<ncores; ++i)
    bthread_join( i );

  // Stop counting stats

  test_stats_off();

  if ( bthread_get_core_id() == 0 )
    verify_results( N, dest, ref );

  return 0;
}
