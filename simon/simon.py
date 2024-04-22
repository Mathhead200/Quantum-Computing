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
    return x % 2**(n-1)

# ----- DON'T EDIT BELOW! -----
N = 2**n
I = [[i == j for j in range(N)] for i in range(N)]  # N-bit identity matrix.

def tensor(v: list, w: list, op = lambda v0, w0: v0 * w0):
    return [v[i] * w[j] for j in range(len(w)) for i in range(len(v))]

def _Bf_column(x: int, y: int) -> list[int]:
    """ y and x must be n*-bit classical states; i.e., unsigned ints (*see global, n) """
    return tensor(I[x], I[f(x) ^ y])
    
def transpose(M: list[list]) -> list[list]:
    """ M must be a rectangular matrix; i.e., non-raggid """
    ROWS = len(M)
    COLS = len(M[0])
    return [[M[j][i] for j in range(ROWS)] for i in range(COLS)]

# build Simon's black box
Bf = transpose([_Bf_column(x, y) for y in range(N) for x in range(N)])

def print_mat(M: list[list]) -> None:
    for i in range(len(M)):
        for j in range(len(M[i])):
            print(M[i][j], end="")
        print()

if __name__ == "__main__":
    print_mat(Bf)
    Uf = UnitaryGate(Bf, label="Bf")

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