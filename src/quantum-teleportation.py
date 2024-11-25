from math import acos, sqrt
from typing import Any, Final

import tomllib
import pyqpanda as pq


def configInformation() -> dict[str, Any]:
    with open("config/config.toml", "rb") as file:
        return tomllib.load(file)


# in this circuit, alpha and beta are both real numbers
def prepareStateGate(qubit: pq.Qubit, alpha: float, beta: float) -> pq.QGate | None:
    # Guard, check if args are legal
    modulus = alpha**2 + beta**2
    if abs(modulus - 1.0) > 0.00001:
        print("Illegal alpha and beta, mod = {}".format(modulus))
        return

    # Make a quantum gate that transforms |0> to \alpha |0> + \beta |1>
    # Note that alpha and beta are Real Numbers
    # So just use R_y Gate is ok.

    # \alpha = cos(theta/2) so that theta = acos(\alpha) * 2
    angle: float = 2 * acos(alpha)

    # To rotate to the angle
    return pq.RY(qubit, angle)


def main():
    # Load configuration
    config: Final[dict[str, Any]] = configInformation()

    # Initialize QVM
    qvm = pq.CPUQVM()
    qvm.init_qvm()

    # quBits[0] : \phi
    # quBits[1 and 2] : EPR Pair
    # cBits correspond to qubits respectively
    quBits = qvm.qAlloc_many(3)
    cBits = qvm.cAlloc_many(3)

    # 0: Init Phi state
    initCircuit = pq.QCircuit()
    initCircuit << prepareStateGate(quBits[0], sqrt(2) / 2, sqrt(2) / 2)

    # 1: Bell State
    bellStateCircuit = pq.QCircuit()
    bellStateCircuit << pq.H(quBits[1]) << pq.CNOT(quBits[1], quBits[2])

    # 2: Build Core circuit
    coreCircuit = pq.QCircuit()
    coreCircuit << pq.CNOT(quBits[0], quBits[1]) << pq.H(quBits[0])

    # 3: Add measurement
    prog = pq.QProg()
    prog << initCircuit << bellStateCircuit << coreCircuit << pq.BARRIER(quBits)

    prog << pq.Measure(quBits[0], cBits[0]) << pq.Measure(quBits[1], cBits[1])
    prog << pq.BARRIER(quBits)

    # Then add CNOT and CZ
    prog << pq.CNOT(quBits[1], quBits[2]) << pq.CZ(quBits[0], quBits[2])
    prog << pq.Measure(quBits[2], cBits[2])

    print("Program be like: {}".format(prog))
    pq.draw_qprog(
        prog,
        "pic",
        filename=config["exportFiles"]["destination"] + "quantum-teleportation-prog",
    )

    result = qvm.run_with_configuration(prog, cBits, config["simulation"]["shots"])
    print("Result for all qubits: {}".format(result))

    # get all result with key ended with '0' or '1'
    zeroObeservedTimes: int = 0
    oneObeservedTimes: int = 0
    for key, value in result.items():
        if key[0] == "0":
            zeroObeservedTimes += value
            continue
        # otherwise begin with 1
        oneObeservedTimes += value

    print(
        "Result for qubit_2: {}".format(
            {"0": zeroObeservedTimes, "1": oneObeservedTimes}
        )
    )

    qvm.finalize()


if __name__ == "__main__":
    main()
