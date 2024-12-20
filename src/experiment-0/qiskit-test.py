from typing import Final, Any
import tomllib

from qiskit.visualization import circuit_drawer, plot_histogram
from qiskit_aer import AerSimulator
import qiskit as qk


def configInformation() -> dict[str, Any]:
    """
    Load configuration information from the config.toml file
    
    Args:
        None
    
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


def main():
    """
    Main function to run the bell state circuit
    """
    
    # Create a quantum circuit with 2 qubits
    circuit = qk.QuantumCircuit(2)

    # Apply Hadamard gate and CX gate to the circuit
    circuit.h(0)
    circuit.cx(0, 1)

    # Measure all qubits
    circuit.measure_all()

    # Transpile the circuit for the AerSimulator
    simulator = AerSimulator()
    circuit = qk.transpile(circuit, simulator)

    # Run the circuit on the AerSimulator
    result = simulator.run(circuit, shots=simulationShots).result()
    count = result.get_counts(circuit)

    # Print results and save the histogram
    print(count)
    plot_histogram(
        count,
        filename=fileSavePath + "bell-state-count.png",
        title="Bell State Circuit",
    )

    # Draw the circuit and save the image
    circuitImg = circuit_drawer(circuit, output="mpl", scale=2)
    circuitImg.savefig(fileSavePath + "bell-state.png")


if __name__ == "__main__":
    main()
