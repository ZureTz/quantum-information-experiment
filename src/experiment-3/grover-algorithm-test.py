# Relative path: src/experiment-3/grover-algorithm-test.py

from math import sqrt
from typing import Final, Any
import tomllib

import qiskit as qk
from qiskit_aer import AerSimulator
from qiskit.circuit.library import MCMT
from qiskit.visualization import plot_histogram


def configInformation() -> dict[str, Any]:
    """
    Load configuration information from the config.toml file

    Returns:
        dict[str, Any]: Configuration information in a dictionary format
    """

    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


# Load configuration
config: Final[dict[str, Any]] = configInformation()

# File save path
fileSavePath: Final[str] = config["exportFiles"]["destination"]
# Number of shots for the simulation
simulationShots: Final[int] = config["simulation"]["shots"]

# Number of input qubits
numInputQuBits: Final[int] = 3
# Number of additional qubits used in the oracle workspace
# This number is 3 because the expression has sub-expressions with 3 qubits
numAdditionalQuBits: Final[int] = numInputQuBits
# Number of oracle qubits in oracle workspace
numOracleQuBits: Final[int] = 1


def initializeCircuit() -> qk.QuantumCircuit:
    """
    Gate that initializes the qubits to the superposition state

    Returns:
        qk.QuantumCircuit: Initialization circuit
    """

    initialize = qk.QuantumCircuit(
        numInputQuBits + numAdditionalQuBits + numOracleQuBits, name="Initialization"
    )
    # Reverse the last qubit to make it |1> and apply H gate to all qubits
    initialize.x(numInputQuBits + numAdditionalQuBits + numOracleQuBits - 1)

    initialize.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))
    # Apply H gate to all qubits
    initialize.h(
        list(range(numInputQuBits))
        + [numInputQuBits + numAdditionalQuBits + numOracleQuBits - 1]
    )
    # initialize.h(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    initialize.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    # Output as png
    initialize.draw(
        output="mpl", filename=fileSavePath + "grover-algorithm-initialize.png"
    )

    return initialize


def oracleCircuit() -> qk.QuantumCircuit:
    """
    Gate that works exactly as the the logic expression below:
        (q0 | ~q1) & (~q0 | q1 | q2) & (q0 | q2)
    It inputs 3 qubits and outputs 1 qubit to the oracle workspace

    Returns:
        qk.QuantumCircuit: Oracle circuit
    """

    oracle = qk.QuantumCircuit(
        numInputQuBits + numAdditionalQuBits + numOracleQuBits, name="Oracle"
    )

    # Sub-expression 1: (q0 | ~q1) == ~(~q0 & q1)
    oracle.x(0)
    oracle.ccx(0, 1, numInputQuBits)
    oracle.x(0)
    oracle.x(numInputQuBits)
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    # Sub-expression 2: (~q0 | q1 | q2) == ~(q0 & ~q1 & ~q2)
    oracle.x([1, 2])
    oracle.compose(
        MCMT("cx", numInputQuBits, 1),
        list(range(numInputQuBits)) + [numInputQuBits + 1],
        inplace=True,
    )
    oracle.x([1, 2])
    oracle.x(numInputQuBits + 1)
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    # Sub-expression 3: (q0 | q2) == ~(~q0 & ~q2)
    oracle.x([0, 2])
    oracle.ccx(0, 2, numInputQuBits + 2)
    oracle.x([0, 2])
    oracle.x(numInputQuBits + 2)
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    # Combine all sub-expressions
    oracle.compose(
        MCMT("cx", numAdditionalQuBits, 1),
        list(range(numInputQuBits, numInputQuBits + numAdditionalQuBits))
        + [numInputQuBits + numAdditionalQuBits + numOracleQuBits - 1],
        inplace=True,
    )

    # Reverse the additional qubits and the input qubits to the original state

    # Reverse for Sub-expression 3
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))
    oracle.x(numInputQuBits + 2)
    oracle.x([0, 2])
    oracle.ccx(0, 2, numInputQuBits + 2)
    oracle.x([0, 2])

    # Reverse for Sub-expression 2
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))
    oracle.x(numInputQuBits + 1)
    oracle.x([1, 2])
    oracle.compose(
        MCMT("cx", numInputQuBits, 1),
        list(range(numInputQuBits)) + [numInputQuBits + 1],
        inplace=True,
    )
    oracle.x([1, 2])

    # Reverse for Sub-expression 1
    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))
    oracle.x(numInputQuBits)
    oracle.x(0)
    oracle.ccx(0, 1, numInputQuBits)
    oracle.x(0)

    oracle.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))
    # Output as png
    oracle.draw(output="mpl", filename=fileSavePath + "grover-algorithm-oracle.png")

    return oracle


def diffusionCircuit() -> qk.QuantumCircuit:
    """
    Gate that applies the diffusion operator

    Returns:
        qk.QuantumCircuit: Diffusion circuit
    """

    diffusion = qk.QuantumCircuit(
        numInputQuBits + numAdditionalQuBits + numOracleQuBits, name="Diffusion"
    )
    # First apply H gate to all input qubits and oracle workspace qubit
    diffusion.h(range(numInputQuBits))
    diffusion.h(numInputQuBits + numAdditionalQuBits + numOracleQuBits - 1)
    # Then apply X gate to all input qubits
    diffusion.x(range(numInputQuBits))
    # Apply the multi-controlled Z gate
    cccxGate = MCMT("cx", numInputQuBits, 1)
    diffusion.compose(
        cccxGate,
        list(range(numInputQuBits))
        + [numInputQuBits + numAdditionalQuBits + numOracleQuBits - 1],
        inplace=True,
    )

    # Apply X gate and H gate to all qubits except the last one which is in the oracle workspace
    diffusion.x(range(numInputQuBits))
    diffusion.h(range(numInputQuBits))

    # Add barrier
    diffusion.barrier(range(numInputQuBits + numAdditionalQuBits + numOracleQuBits))

    # Output as png
    diffusion.draw(
        output="mpl", filename=fileSavePath + "grover-algorithm-diffusion.png"
    )

    return diffusion


def main():
    # Create a quantum circuit with numInputQuBits + numOracleQuBits qubits
    # and classical register with numInputQuBits bits
    circuit = qk.QuantumCircuit(
        numInputQuBits + numAdditionalQuBits + numOracleQuBits, numInputQuBits
    )

    # Apply the initialization circuit
    circuit.compose(initializeCircuit(), inplace=True)

    # Times to apply Oracle and Diffusion gates = sqrt(2^(numInputQuBits))
    for _ in range(int(sqrt(2 ** (numInputQuBits)))):
        # Apply the oracle gate
        circuit.compose(oracleCircuit(), inplace=True)
        # Apply the diffusion gate
        circuit.compose(diffusionCircuit(), inplace=True)

    # stateVector = Statevector(circuit)
    # stateVector.draw(output="city", filename=fileSavePath + "grover-algorithm-state-vector.png")

    # Measure all qubits except the last one which is in the oracle workspace
    # circuit.measure(range(numInputQuBits), range(numInputQuBits))
    circuit.measure(range(numInputQuBits), range(numInputQuBits))

    # Output circuit as png
    circuit.draw(output="mpl", filename=fileSavePath + "grover-algorithm-circuit.png")

    # Run simulation using AerSimulator and output the result as histogram
    simulator = AerSimulator()
    circuit = qk.transpile(circuit, simulator)
    result = simulator.run(circuit, shots=simulationShots).result()
    count = result.get_counts(circuit)
    plot_histogram(
        count,
        filename=fileSavePath + "grover-algorithm-count.png",
        title="Grover's Algorithm",
    )


if __name__ == "__main__":
    main()
