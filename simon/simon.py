from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
# from qiskit_ibm_runtime import *
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import UnitaryGate
from matplotlib import pyplot

# number of qubits
n = 3

def f(x):
    """ Our 2-1 function with iff f(x) = f(y) then x + y = 0,s """
    return x % 4

if __name__ == "__main__":
    # TODO: build Simon's black box
    Uf = [[1 if i == j else 0 for j in range(2**(2*n))] for i in range(2**(2*n))]
    Uf = UnitaryGate(Uf, label="Uf")

    x = QuantumRegister(n, "x")
    y = QuantumRegister(n, "y")
    c = ClassicalRegister(n, "c")
    qc = QuantumCircuit(x, y, c)
    qc.h(range(n))
    qc.append(Uf, range(2*n))
    qc.h(range(n))
    qc.measure(range(n), range(n))

    qc.draw("mpl", style="iqp", filename="simon")

    backend = Aer.get_backend("qasm_simulator")
    qc = transpile(qc, backend=backend)
    result = backend.run(qc, shots=1024).result()
    plot_histogram(result.get_counts(), filename="histogram-simon.png")