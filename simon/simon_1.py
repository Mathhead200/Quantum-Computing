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
    return [5, 2, 0, 6, 0, 6, 5, 2][x]  # s = 6

# ----- DON'T EDIT BELOW! -----
N = 2**n
I = [[1 if i == j else 0 for j in range(N)] for i in range(N)]  # N-bit identity matrix.

def tensor(v: list, w: list, op = lambda v0, w0: v0 * w0):
    return [v[i] * w[j] for i in range(len(v)) for j in range(len(w))]

def _Bf_column(y: int, x: int) -> list[int]:
    """ y and x must be n*-bit classical states; i.e., unsigned ints (*see global, n) """
    print("|yx> = |" + str(y) + str(x) + ">")
    return tensor(I[y ^ f(x)], I[x])
    
def transpose(M: list[list]) -> list[list]:
    """ M must be a rectangular matrix; i.e., non-raggid """
    ROWS = len(M)
    COLS = len(M[0])
    return [[M[j][i] for j in range(ROWS)] for i in range(COLS)]

# build Simon's black box
Bf = transpose([_Bf_column(y, x) for y in range(N) for x in range(N)])

def print_mat(M: list[list]) -> None:
    for i in range(len(M)):
        for j in range(len(M[i])):
            print(M[i][j], end="")
        print()

if __name__ == "__main__":
    print("Bf:")
    print_mat(Bf)
    print()

    print("x -> f(x)")
    for x in range(N):
        print(x, "->", f(x))
    print()

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
    result = backend.run(qc, shots=1024*n).result()
    plot_histogram(result.get_counts(), filename="histogram-simon.png")