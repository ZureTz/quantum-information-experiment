from typing import Any, Final
import tomllib
import pyqpanda as pq


def configInformation() -> dict[str, Any]:
    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


# Load configuration
config: Final[dict[str, Any]] = configInformation()


class ControlledSubtractorProgram:
    def __init__(self, workingDigits: int):
        """
        Initialize the ControlledSubtractorProgram with the number of working digits.

        Args:
            workingDigits (int): The number of digits to be used in the quantum operations.
        """
        self.qvm = pq.CPUQVM()  # Initialize QVM
        self.qvm.init_qvm()

        self.workingDigits = workingDigits
        # 2 * nDigits : input for a and b
        numInputDigits = 2 * workingDigits
        # 1 for cIn and cOut circuit
        numCinAndCOutDigit = 1
        # nDigits : for sum
        numSumDigits = workingDigits
        # control add or sub
        numControlDigits = 1

        # Allocate qubits and cbits
        self.qubits = self.qvm.qAlloc_many(
            numInputDigits + numCinAndCOutDigit + numSumDigits + numControlDigits
        )
        self.cBits = self.qvm.cAlloc_many(numSumDigits)

        # [0 to n - 1]: a_{n-1} to a_0
        # [n to 2n - 1]: b_{n-1} to b_0
        # [2n]: cin/cout
        # [2n + 1 to 3n]: sum_{n-1} to sum_0
        # [3n + 1]: control digit
        self.aBeginIndex = 0
        self.bBeginIndex = self.workingDigits
        self.cInCoutIndex = 2 * self.workingDigits
        self.sumBeginIndex = 2 * self.workingDigits + 1
        self.controlIndex = 3 * self.workingDigits + 1

    def prepareInputCircuit(
        self, a: int, b: int, isDoingSubtraction: int
    ) -> pq.QCircuit:
        """
        Prepare the input circuit by setting the initial values of qubits based on the binary representation of a and b.

        Args:
            a (int): The integer value for the first operand.
            b (int): The integer value for the second operand.
            isDoingSubtraction (int): Flag to indicate if the operation is subtraction (1) or addition (0).

        Returns:
            pq.QCircuit: The quantum circuit with the prepared input.
        """
        
        circuit = pq.QCircuit()

        # Convert a and b to binary from right to left
        aInBinary: list[int] = [
            1 if (a % 2**i // 2 ** (i - 1)) == 1 else 0
            for i in range(self.workingDigits, 0, -1)
        ]

        bInBinary: list[int] = [
            1 if (b % 2**i // 2 ** (i - 1)) == 1 else 0
            for i in range(self.workingDigits, 0, -1)
        ]

        print(
            "a: {}, b: {}, isDoingSubtraction: {}".format(
                aInBinary, bInBinary, isDoingSubtraction
            )
        )

        # Set the values of qubits based on the binary representation of a and b
        for i in range(self.workingDigits - 1, -1, -1):
            if aInBinary[i] == 1:
                circuit << pq.X(self.qubits[self.aBeginIndex + i])
            if bInBinary[i] == 1:
                circuit << pq.X(self.qubits[self.bBeginIndex + i])

        if isDoingSubtraction:
            circuit << pq.X(self.qubits[self.controlIndex])

        circuit << pq.BARRIER(self.qubits)

        return circuit

    def preControlledInverseCircuit(self) -> pq.QCircuit:
        """
        Prepare the pre-controlled inverse circuit.

        This circuit applies a CNOT gate controlled by the control qubit to each qubit in the range of a.

        Returns:
            pq.QCircuit: The quantum circuit with the pre-controlled inverse operations.
        """
        
        circuit = pq.QCircuit()
        for i in range(self.aBeginIndex + self.workingDigits):
            circuit << pq.CNOT(self.qubits[self.controlIndex], self.qubits[i])
        circuit << pq.BARRIER(self.qubits)
        return circuit

    # this is for each bit
    # bit index is invoked for the same digits qubits
    #   e.g. qubits[0 + bitIndex], qubits[4 + bitIndex] ...
    def singleAdderCircuit(self, bitIndex: int) -> pq.QCircuit:
        """
        Creates a single-bit adder quantum circuit.

        Args:
            bitIndex (int): The index of the bit to perform the addition on.
        
        Returns:
            pq.QCircuit: A quantum circuit implementing the single-bit adder.
        """
        
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

    def postControlledInverseCircuit(self) -> pq.QCircuit:
        """
        Prepare the post-controlled inverse circuit.
        
        Args:
            None
            
        Returns:
            pq.QCircuit: The quantum circuit with the post-controlled inverse operations.
        """
        
        circuit = pq.QCircuit()

        for i in range(self.sumBeginIndex, self.sumBeginIndex + self.workingDigits):
            circuit << pq.CNOT(self.qubits[self.controlIndex], self.qubits[i])

        circuit << pq.BARRIER(self.qubits)
        return circuit


    def combinationCircuit(
        self, a: int, b: int, isDoingSubtraction: int
    ) -> pq.QCircuit:
        """
        Combine the quantum circuits for the pre-controlled inverse, single adder, and post-controlled inverse operations.

        Args:
            a (int): The integer value for the first operand.
            b (int): The integer value for the second operand.
            isDoingSubtraction (int): Flag to indicate if the operation is subtraction (1) or addition (0).

        Returns:
            pq.QCircuit: The quantum circuit with the combined operations.
        """
        
        circuit = pq.QCircuit()

        # Prepare input
        circuit << self.prepareInputCircuit(a, b, isDoingSubtraction)

        # Controlled Inverse A
        circuit << self.preControlledInverseCircuit()

        for i in range(self.workingDigits - 1, -1, -1):
            circuit << self.singleAdderCircuit(i)

        # Inverse all outputs
        circuit << self.postControlledInverseCircuit()

        return circuit

    def run(self, a: int, b: int, isDoingSubtraction: int, iterations: int):
        """
        Run the quantum program with the given inputs.
        
        Args:
            a (int): The integer value for the first operand.
            b (int): The integer value for the second operand.
            isDoingSubtraction (int): Flag to indicate if the operation is subtraction (1) or addition (0).
            iterations (int): The number of iterations to run the program.
        
        Returns:   
            None
        """
        
        circuit = self.combinationCircuit(a, b, isDoingSubtraction)

        prog = pq.QProg()
        prog << circuit

        # Add measurement
        for i in range(self.workingDigits):
            prog << pq.Measure(
                self.qubits[self.sumBeginIndex + self.workingDigits - 1 - i],
                self.cBits[i],
            )

        pq.draw_qprog(
            prog,
            "pic",
            filename=(
                config["exportFiles"]["destination"]
                + "controlled-adder-or-subtractor-"
                + ("subtracting" if isDoingSubtraction else "adding")
            ),
        )

        result = self.qvm.run_with_configuration(prog, self.cBits, iterations)
        print("Result: {}".format(result))

    # Destructor using 'with'
    def __enter__(self):
        """
        Enter the context manager.

        Returns:
            self
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager.
        
        Returns:
            None
        """
        
        self.qvm.finalize()


def main():
    # Load configuration
    
    # Number of digits to be used in the quantum operations
    nDigits: int = config["adderDigits"]["count"]
    # Number of iterations to run the program
    runIterations: int = config["adderDigits"]["iterations"]

    print("nDigits = {}, runIterations = {}".format(nDigits, runIterations))

    # Run the program for addition and subtraction respectively
    # Using different values for a and b to ensure the correctness of the program
    with ControlledSubtractorProgram(nDigits) as program:
        program.run(0b0001, 0b1011, 0, runIterations)
        program.run(0b0001, 0b1011, 1, runIterations)


if __name__ == "__main__":
    main()
