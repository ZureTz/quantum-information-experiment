from math import sqrt
from typing import Final, Any
import tomllib

import qiskit as qk
from qiskit_aer import AerSimulator
from qiskit.circuit.library import MCMT
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector


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
# Number of oracle qubits in oracle workspace
numOracleQuBits: Final[int] = 1


def initializeCircuit() -> qk.QuantumCircuit:
    """
    Gate that initializes the qubits to the superposition state

    Returns:
        qk.QuantumCircuit: Initialization circuit
    """

    initialize = qk.QuantumCircuit(
        numInputQuBits + numOracleQuBits, name="Initialization"
    )
    # Reverse the last qubit to make it |1> and apply H gate to all qubits
    initialize.x(numInputQuBits + numOracleQuBits - 1)

    initialize.barrier(range(numInputQuBits + numOracleQuBits))
    # Apply H gate to all qubits
    initialize.h(list(range(numInputQuBits)) + [numInputQuBits + numOracleQuBits - 1])
    # initialize.h(range(numInputQuBits + numOracleQuBits))

    initialize.barrier(range(numInputQuBits + numOracleQuBits))

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
    This formula can be minimized to: (q0 & q1) ^ (~q1 & q2)
    Using the minimized form, the oracle circuit can be implemented

    Returns:
        qk.QuantumCircuit: Oracle circuit
    """

    oracle = qk.QuantumCircuit(numInputQuBits + numOracleQuBits, name="Oracle")

    # Formula (q0 | ~q1) & (~q0 | q1 | q2) & (q0 | q2)
    # can be minimized to (q0 & q1) | (~q1 & q2)
    # in XOR form: (q0 & q1) ^ (~q1 & q2) ^ (q0 & q1 & ~q1 & q2)
    # which can be further minimized to: (q0 & q1) ^ (~q1 & q2)
    oracle.ccx(0, 1, numInputQuBits + numOracleQuBits - 1)
    oracle.x(1)
    oracle.ccx(1, 2, numInputQuBits + numOracleQuBits - 1)
    oracle.x(1)

    oracle.barrier(range(numInputQuBits + numOracleQuBits))
    # Output as png
    oracle.draw(output="mpl", filename=fileSavePath + "grover-algorithm-oracle.png")

    return oracle


def diffusionCircuit() -> qk.QuantumCircuit:
    """
    Gate that applies the diffusion operator

    Returns:
        qk.QuantumCircuit: Diffusion circuit
    """

    diffusion = qk.QuantumCircuit(numInputQuBits + numOracleQuBits, name="Diffusion")
    # First apply H gate to all input qubits and oracle workspace qubit
    diffusion.h(range(numInputQuBits))
    diffusion.h(numInputQuBits + numOracleQuBits - 1)
    # Then apply X gate to all input qubits
    diffusion.x(range(numInputQuBits))
    # Apply the multi-controlled Z gate
    cczGate = MCMT("cx", numInputQuBits, 1)
    diffusion.compose(
        cczGate,
        list(range(numInputQuBits)) + [numInputQuBits + numOracleQuBits - 1],
        inplace=True,
    )

    # Apply X gate and H gate to all qubits except the last one which is in the oracle workspace
    diffusion.x(range(numInputQuBits))
    diffusion.h(range(numInputQuBits))

    # Add barrier
    diffusion.barrier(range(numInputQuBits + numOracleQuBits))

    # Output as png
    diffusion.draw(
        output="mpl", filename=fileSavePath + "grover-algorithm-diffusion.png"
    )

    return diffusion


def main():
    # Create a quantum circuit with numInputQuBits + numOracleQuBits qubits
    # and classical register with numInputQuBits bits
    circuit = qk.QuantumCircuit(numInputQuBits + numOracleQuBits, numInputQuBits)

    # Apply the initialization circuit
    circuit.compose(initializeCircuit(), inplace=True)

    # Times to apply Oracle and Diffusion gates = sqrt(2^(numInputQuBits))
    for _ in range(int(sqrt(2 ** (numInputQuBits)))):
        circuit.compose(oracleCircuit(), inplace=True)
        circuit.compose(diffusionCircuit(), inplace=True)
        
    # Get the state vector of the circuit and output as png
    stateVector = Statevector(circuit)
    stateVector.draw(output="city", filename=fileSavePath + "grover-algorithm-state-vector.png")

    # Measure all qubits except the last one which is in the oracle workspace
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
