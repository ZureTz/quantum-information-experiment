// Test the oracle function used in grover-algorithm.py

#include <iostream>

// Oracle function used in grover-algorithm.py
int oracleTest(int q0, int q1, int q2) {
  return (q0 || !q1) && (!q0 || q1 || q2) && (q0 || q2);
}

int main(int argc, char const *argv[]) {

  // Print the truth table of the oracle function
  for (int q2 = 0; q2 <= 1; q2++) {
    for (int q1 = 0; q1 <= 1; q1++) {
      for (int q0 = 0; q0 <= 1; q0++) {
        std::cout << q2 << " " << q1 << " " << q0 << " "
                  << oracleTest(q0, q1, q2) << std::endl;
      }
    }
  }

  return 0;
}