from typing import Any, Final
import tomllib
import pyqpanda as pq


def configInformation() -> dict[str, Any]:
    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


# Load configuration
config: Final[dict[str, Any]] = configInformation()


class AdderProgram:
    def __init__(self, workingDigits: int):
        self.qvm = pq.CPUQVM()  # Initialize QVM
        self.qvm.init_qvm()

        self.workingDigits = workingDigits
        # 2 * nDigits : input for a and b
        numInputDigits = 2 * workingDigits
        # 1 for cIn and cOut circuit
        numCinAndCOutDigit = 1
        # nDigits : for sum
        numSumDigits = workingDigits

        # Allocate qubits and cbits
        self.qubits = self.qvm.qAlloc_many(
            numInputDigits + numCinAndCOutDigit + numSumDigits
        )
        self.cBits = self.qvm.cAlloc_many(numSumDigits)

        # [0 to n - 1]: a_{n-1} to a_0
        # [n to 2n - 1]: b_{n-1} to b_0
        # [2n]: cin/cout
        # [2n + 1 to 3n]: sum_{n-1} to sum_0
        self.aBeginIndex = 0
        self.bBeginIndex = self.workingDigits
        self.cInCoutIndex = 2 * self.workingDigits
        self.sumBeginIndex = 2 * self.workingDigits + 1

    def prepareInputCircuit(self, a: int, b: int) -> pq.QCircuit:
        circuit = pq.QCircuit()

        # convert a and b to binary form list
        aInBinary: list[int] = [
            1 if (a % 2**i // 2 ** (i - 1)) == 1 else 0
            for i in range(self.workingDigits, 0, -1)
        ]

        bInBinary: list[int] = [
            1 if (b % 2**i // 2 ** (i - 1)) == 1 else 0
            for i in range(self.workingDigits, 0, -1)
        ]

        print("a: {}, b: {}".format(aInBinary, bInBinary))

        # based on the two lists, set appropriate input, using the X gate
        for i in range(self.workingDigits - 1, -1, -1):
            if aInBinary[i] == 1:
                circuit << pq.X(self.qubits[self.aBeginIndex + i])
            if bInBinary[i] == 1:
                circuit << pq.X(self.qubits[self.bBeginIndex + i])

        circuit << pq.BARRIER(self.qubits)

        return circuit

    # this is for each bit
    # bit index is invoked for the same digits qubits
    #   e.g. qubits[0]
    def singleAdderCircuit(self, bitIndex: int) -> pq.QCircuit:
        circuit = pq.QCircuit()
        (
            circuit
            << pq.CNOT(
                self.qubits[self.cInCoutIndex],
                self.qubits[self.sumBeginIndex + bitIndex],
            )
            << pq.CNOT(
                self.qubits[self.sumBeginIndex + bitIndex],
                self.qubits[self.cInCoutIndex],
            )
            # operation with b
            << pq.Toffoli(
                self.qubits[self.bBeginIndex + bitIndex],
                self.qubits[self.sumBeginIndex + bitIndex],
                self.qubits[self.cInCoutIndex],
            )
            << pq.CNOT(
                self.qubits[self.bBeginIndex + bitIndex],
                self.qubits[self.sumBeginIndex + bitIndex],
            )
            # operation with a
            << pq.Toffoli(
                self.qubits[self.aBeginIndex + bitIndex],
                self.qubits[self.sumBeginIndex + bitIndex],
                self.qubits[self.cInCoutIndex],
            )
            << pq.CNOT(
                self.qubits[self.aBeginIndex + bitIndex],
                self.qubits[self.sumBeginIndex + bitIndex],
            )
        )
        circuit << pq.BARRIER(self.qubits)

        return circuit

    # A and B are for digits binary number
    def combinationCircuit(self, a: int, b: int) -> pq.QCircuit:
        circuit = pq.QCircuit()

        circuit << self.prepareInputCircuit(a, b)

        for i in range(self.workingDigits - 1, -1, -1):
            circuit << self.singleAdderCircuit(i)

        return circuit

    def run(self, a: int, b: int, iterations: int):
        circuit = self.combinationCircuit(a, b)

        prog = pq.QProg()
        prog << circuit

        # Add measurement
        for i in range(self.workingDigits):
            prog << pq.Measure(
                self.qubits[self.sumBeginIndex + self.workingDigits - 1 - i],
                self.cBits[i],
            )

        pq.draw_qprog(
            prog, "pic", filename=config["exportFiles"]["destination"] + "adder"
        )

        result = self.qvm.run_with_configuration(prog, self.cBits, iterations)
        print("Result: {}".format(result))

    # Destructor using 'with'
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.qvm.finalize()


def main():
    nDigits: int = config["adderDigits"]["count"]
    runIterations: int = config["adderDigits"]["iterations"]

    print("nDigits = {}, runIterations = {}".format(nDigits, runIterations))

    with AdderProgram(nDigits) as program:
        program.run(0b1000, 0b0111, runIterations)


if __name__ == "__main__":
    main()
