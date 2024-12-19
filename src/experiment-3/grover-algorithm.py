from typing import Any, Final
import tomllib
import qiskit as qk


def configInformation() -> dict[str, Any]:
    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


# Load configuration
config: Final[dict[str, Any]] = configInformation()


def main():
    # Create a quantum circuit with 2 qubits
    circuit = qk.QuantumCircuit(2)

    # Add H-gate to the first qubit
    circuit.h(0)

    # Perform a controlled-X gate on qubit 1, controlled by qubit 0
    circuit.cx(0, 1)

    # print(circuit)
    circuit.draw(output="mpl", filename="grover-algorithm.png")


if __name__ == "__main__":
    main()
