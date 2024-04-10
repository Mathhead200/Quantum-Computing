from qiskit import QuantumCircuit, transpile
# from qiskit_ibm_runtime import *
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import UnitaryGate
from matplotlib import pyplot
from math import sqrt, ceil

# number of bits
n = 8

# number of states: function of little n
N = 2**n

def f(x: int) -> bool:
    """ Our search function """
    return x == 200

# iterations
COUNT = ceil(sqrt(N))

if __name__ == "__main__":
    Uf = [[(-1)**f(i) if i == j else 0 for j in range(N)] for i in range(N)]
    Uf = UnitaryGate(Uf, label="Uf")

    D = [[2/N - (1 if i == j else 0) for j in range(N)] for i in range(N)]
    D = UnitaryGate(D, label="D")

    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(COUNT):
        qc.append(Uf, range(n))
        qc.append(D, range(n))
    qc.measure(range(n), range(n))

    qc.draw("mpl", style="iqp", filename="grover")

    backend = Aer.get_backend("qasm_simulator")
    qc = transpile(qc, backend=backend)
    result = backend.run(qc).result()
    plot_histogram(result.get_counts(), filename="histogram-grover.png")
