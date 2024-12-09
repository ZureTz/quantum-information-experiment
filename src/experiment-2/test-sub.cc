#include <cassert>
#include <climits>
#include <cstdio>

int subtract(int a, int b) { return ~(~a + b); }

int main(int argc, char const *argv[]) {
  for (int i = 0; i < 50; i++) {
    for (int j = 0; j < 50; j++) {
      printf("%d - %d = %d\n", i, j, subtract(i, j));
      assert(i - j == subtract(i, j));
    }
  }

  printf("%d - %d = %d\n", INT_MAX, INT_MIN, subtract(INT_MAX, INT_MIN));
  assert(INT_MAX - INT_MIN == subtract(INT_MAX, INT_MIN));

  printf("%d - %d = %d\n", INT_MIN, INT_MAX, subtract(INT_MIN, INT_MAX));
  assert(INT_MIN - INT_MAX == subtract(INT_MIN, INT_MAX));

  return 0;
}
