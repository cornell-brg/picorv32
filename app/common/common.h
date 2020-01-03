//========================================================================
// common
//========================================================================
// Helper routines for writing TinyRV2 microbenchmarks.

#ifndef COMMON_H
#define COMMON_H

#define PICO_CTRL(val) asm("sw %0, 0(%1)" :: "r"(val), "r"(0x10000000))

#include "common-misc.h"
#include "common-wprint.h"
#include "common-bthread.h"

#endif /* COMMON_H */

