// Test the oracle function used in grover-algorithm.py
// Relative path: src/experiment-3/oracle-test.cc

#include <iostream>
#include <iomanip>

// Minimized oracle function
int oracleTestMinimized(int q0, int q1, int q2) {
  return (q0 && q1) || (!q1 && q2);
}

// Original oracle function
int oracleTestOriginal(int q0, int q1, int q2) {
  return (q0 || !q1) && (!q0 || q1 || q2) && (q0 || q2);
}

int main(int argc, char const *argv[]) {
  // Test the oracle function
  bool allMatch = true;
  // Print the header with aligned format
  std::cout << std::left
            << std::setw(3) << "q2"
            << std::setw(3) << "q1"
            << std::setw(3) << "q0"
            << std::setw(7) << "result"
            << std::endl;
  
  for (int q2 = 0; q2 <= 1; q2++) {
    for (int q1 = 0; q1 <= 1; q1++) {
      for (int q0 = 0; q0 <= 1; q0++) {
        const int originalResult = oracleTestOriginal(q0, q1, q2);
        const int minimizedResult = oracleTestMinimized(q0, q1, q2);

        if (originalResult != minimizedResult) {
          allMatch = false;
        }
        // Print results with aligned format
        std::cout << std::left
                  << std::setw(3) << q2
                  << std::setw(3) << q1
                  << std::setw(3) << q0
                  << std::setw(7) << originalResult
                  << std::endl;
        std::cout << std::left
                  << std::setw(3) << q2
                  << std::setw(3) << q1
                  << std::setw(3) << q0
                  << std::setw(7) << minimizedResult
                  << std::endl;
        std::cout << std::endl;
      }
    }
  }

  std::cout << (allMatch ? "All matched." : "Mismatch found!") << std::endl;

  return 0;
}