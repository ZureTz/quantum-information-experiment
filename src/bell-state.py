from typing import Any, Final
import tomllib
import pyqpanda as pq


def configInformation() -> dict[str, Any]:
    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


def setAppropriateInput(quBits: list[pq.Qubit], round: int) -> pq.QCircuit:
    # Control input qubits (Default All 0)
    initCircuit = pq.QCircuit()
    match round:
        # qubits |00>
        case 0:
            pass
        # qubits |01>
        case 1:
            initCircuit << pq.X(quBits[1])
        # qubits |10>
        case 2:
            initCircuit << pq.X(quBits[0])
        # qubits |11>
        case 3:
            initCircuit << pq.X(quBits[0:2])
        case _:
            pass
    return initCircuit


def main():
    # Load configuration
    config: Final[dict[str, Any]] = configInformation()

    # Initialize QVM
    qvm = pq.CPUQVM()
    qvm.init_qvm()

    quBits = qvm.qAlloc_many(2)
    cBits = qvm.cAlloc_many(2)

    for round in range(4):
        print("\nSet input as |{:02b}>".format(round))

        initCircuit = setAppropriateInput(quBits, round)

        # Core circuit
        coreCircuit = pq.QCircuit()
        coreCircuit << pq.H(quBits[0]) << pq.CNOT(quBits[0], quBits[1])

        # Add measurements
        # Then combine with program
        prog = pq.QProg()
        (
            prog
            << initCircuit
            << coreCircuit
            << pq.Measure(quBits[0], cBits[0])
            << pq.Measure(quBits[1], cBits[1])
        )

        print("Program be like: {}".format(prog))
        pq.draw_qprog(
            prog,
            "pic",
            filename=config["exportFiles"]["destination"]
            + "program-bell-state-input-"
            + str(round),
        )

        result = qvm.run_with_configuration(prog, cBits, config["simulation"]["shots"])
        print("Output: {}".format(result))

    qvm.finalize()


if __name__ == "__main__":
    main()
