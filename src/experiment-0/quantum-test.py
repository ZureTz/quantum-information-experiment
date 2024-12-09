from argparse import ArgumentParser
import pyqpanda as pq


def initArgParser() -> ArgumentParser:
    parser = ArgumentParser(prog="quantum-test")
    parser.add_argument(
        "-i",
        "--iterations",
        dest="ITERATIONS",
        help="number of iterations",
        required=True,
    )
    return parser


def main():

    # initialize argument parser, then parse the arguments
    parser = initArgParser()
    args = vars(parser.parse_args())

    qvm = pq.CPUQVM()
    qvm.init_qvm()

    quBits = qvm.qAlloc_many(1)
    cBits = qvm.cAlloc_many(1)

    # Build program
    prog = pq.QProg()
    circuit = pq.QCircuit()

    circuit << pq.H(quBits[0])
    print('Circuit be like: {}'.format(circuit))

    prog << circuit << pq.Measure(quBits[0], cBits[0])
    print('Program be like: {}'.format(prog))
    

    # Run Given Iterations
    iterations = int(args.get("ITERATIONS"))
    print("Iterations: {}".format(iterations))

    results = qvm.run_with_configuration(prog, cBits, iterations)
    
    print('Running result: {}'.format(results))


if __name__ == "__main__":
    main()
