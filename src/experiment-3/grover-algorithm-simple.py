from typing import Final, Any
import tomllib

import qiskit as qk
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
fileSavePath = config["exportFiles"]["destination"]
# Number of shots for the simulation
simulationShots = config["simulation"]["shots"]


def oracleCircuit(n: int = 2) -> qk.QuantumCircuit:
    """
    Function that returns an oracle for the Grover's algorithm

    Args:
        n (int): Number of input qubits (default 2) in the oracle

    Returns:
        qk.QuantumCircuit: Oracle circuit
    """

    oracle = qk.QuantumCircuit(n, name="Oracle")
    oracle.cz(0, 1)

    return oracle


def groverCircuit(n: int = 2) -> qk.QuantumCircuit:
    """
    Function that returns a Grover's algorithm circuit

    Args:
        n (int): Number of input qubits (default 2) in the Grover's algorithm

    Returns:
        qk.QuantumCircuit: Grover's algorithm circuit
    """

    # Create a quantum circuit with n qubits
    grover = qk.QuantumCircuit(n, n, name="Grover")
    grover.h(range(n))
    grover.append(oracleCircuit(n), range(n))

    return grover


def main():
    # Prepare and run the Grover's algorithm
    grover = groverCircuit()
    grover.draw(output="mpl", filename=fileSavePath + "grover-simple.png")

    grover.remove_final_measurements()
    stateVector = Statevector(grover)

    print(stateVector)


if __name__ == "__main__":
    main()
