//========================================================================
// mtbmark-vvadd
//========================================================================
// Each core will process one fourth of the src and dest arrays. So for
// example, if the arrays have 100 elements, core 0 will process elements
// 0 through 24, core 1 will process elements 25 through 49, and so on.

#include "common.h"
#include "mtbmark-vvadd.dat"

//------------------------------------------------------------------------
// Argument struct
//------------------------------------------------------------------------
// This is used to pass arguments when we spawn work onto the cores.

typedef struct {
  int* dest;  // pointer to dest array
  int* src0;  // pointer to src0 array
  int* src1;  // pointer to src1 array
  int  begin; // first element this core should process
  int  end;   // (one past) last element this core should process
} arg_t;

//------------------------------------------------------------------------
// vvadd-mt
//------------------------------------------------------------------------
// Each thread uses the argument structure to figure out what part of the
// array it should work on.

__attribute__ ((noinline))
void vvadd_mt( void* arg_vptr )
{
  // Cast void* to argument pointer.

  arg_t* arg_ptr = (arg_t*) arg_vptr;

  // Create local variables for each field of the argument structure.

  int* dest  = arg_ptr->dest;
  int* src0  = arg_ptr->src0;
  int* src1  = arg_ptr->src1;
  int  begin = arg_ptr->begin;
  int  end   = arg_ptr->end;

  // Do the actual work.

  for ( int i = begin; i < end; i++ )
    dest[i] = src0[i] + src1[i];
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  for ( int i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( i, dest[i], ref[i] );
    }
  }
  test_pass();
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  // Initialize bare threads (bthread). This must happen as the first
  // thing in main()!

  bthread_init();

  // This array will be where the results are stored.

  int dest[size];

  // Start counting stats.

  test_stats_on();

  int block_size = size;
  int ncores = bthread_get_num_cores();

  if (ncores == 2)  block_size = size >> 1;
  else
  if (ncores == 4)  block_size = size >> 2;
  else
  if (ncores == 8)  block_size = size >> 3;
  else
  if (ncores == 16) block_size = size >> 4;

  // Create four argument structures that include the array pointers and
  // what elements each core should process.

  arg_t args[ncores];

  for (int i=0; i<ncores; ++i)
  {
    int begin = i*block_size;
    int end   = begin+block_size;
    if (i == ncores-1) end = size;
    args[i].dest = dest;
    args[i].src0 = src0;
    args[i].src1 = src1;
    args[i].begin = begin;
    args[i].end = end;
  }

  // Spawn work onto cores 1, 2, and 3.

  for (int i=1; i<ncores; ++i)
    bthread_spawn( i, &vvadd_mt, &args[i] );

  // Have core 0 also do some work.

  vvadd_mt( &args[0] );

  // Wait for core 1, 2, and 3 to finish.

  for (int i=1; i<ncores; ++i)
    bthread_join( i );

  // Stop counting stats

  test_stats_off();

  // Core 0 will verify the results.

  if ( bthread_get_core_id() == 0 )
    verify_results( dest, ref, size );

  return 0;
}

