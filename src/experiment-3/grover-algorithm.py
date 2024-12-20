from typing import Final, Any
import tomllib

from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import qiskit as qk


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


def main():
    # Create oracle circuit (default 2 qubits) and draw it
    circuit = oracleCircuit()
    circuit.draw(output="mpl", filename=fileSavePath + "oracle.png")


if __name__ == "__main__":
    main()
