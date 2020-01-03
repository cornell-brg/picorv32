#include "common.h"
#include "stdio.h"

int main( int argc, char* argv[] )
{
  if (argc < 2)
  {
    puts("ERROR");
    return 0;
  }
  printf("%s\n", argv[1]);
  return 0;
}
