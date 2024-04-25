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
    # return x % 2**(n-1)
    return [5, 2, 0, 6, 0, 6, 5, 2][x]  # s = 6

# ----- DON'T EDIT BELOW! -----
N = 2**n
I = [[1 if i == j else 0 for j in range(N)] for i in range(N)]  # N-bit identity matrix.

def tensor(v: list, w: list, op = lambda v0, w0: v0 * w0):
    return [op(v[i],  w[j]) for i in range(len(v)) for j in range(len(w))]

def _Bf_column(y: int, x: int) -> list[int]:
    """ y and x must be n*-bit classical states; i.e., unsigned ints (*see global, n) """
    return tensor(I[y ^ f(x)], I[x])
    
def transpose(M: list[list]) -> list[list]:
    """ M must be a rectangular matrix; i.e., non-raggid """
    ROWS = len(M)
    COLS = len(M[0])
    return [[M[j][i] for j in range(ROWS)] for i in range(COLS)]

# build Simon's black box
Bf = transpose([_Bf_column(y, x) for y in range(N) for x in range(N)])

def print_mat(M: list[list], augmented=False) -> None:
    for i in range(len(M)):
        COLS = len(M[i])
        for j in range(COLS):
            if augmented and j ==  COLS - 1:
                print("|", end="")
            print(M[i][j], end="")
        print()

def rref_mod2(M: list[list]) -> None:
    """ RREF (mod 2). M must be a rectangular matrix with entires in Z/{2}. """
    ROWS = len(M)
    COLS = len(M[0])

    curr_row = 0  # track how many 1's have been found so far
    for curr_col in range(COLS):
        # search for the next 1 in the j-th column
        i = curr_row
        while i < ROWS and M[i][curr_col] != 1:
            i += 1
        if i == ROWS: continue  # failed to find. Move to next column without advancing curr_row

        # otherwise, row swap 1 into place
        (M[curr_row], M[i]) = (M[i], M[curr_row])

        # 0 out all entries above and below this 1
        for i in range(ROWS):
            if i == curr_row or M[i][curr_col] == 0: continue
            # otherwise, row-add curr_row + i
            for j in range(COLS):
                M[i][j] = (M[i][j] + M[curr_row][j]) % 2

        # advance curr_row and move to the next column
        curr_row += 1

def pivots(M: list[list]):
    """
    M must be in echelon form.
    Returns the pivots as column indicies for each row that contains a pivot. E.g.,
    ```
    pivots([
        [1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]) = [0, 2]  # because rows 0 and 1 contain pivots in columns 0 and 2 (respectively)
    ```
    """
    ROWS = len(M)

    pivots = []
    i = 0
    j = 0
    while i < ROWS and j < len(M[i]):
        if M[i][j] == 1:
            yield j
            i += 1
        j += 1

def rank(M: list[list]) -> int:
    return len(list(pivots(M)))


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
    result = backend.run(qc, shots=N/2*128).result()
    plot_histogram(result.get_counts(), filename="histogram-simon.png")

    # post-processing:
    count = 0  # iteration count
    solutions = set()  # store solution set {y | y*s = 0}
    Y = []  # augmented solution matrix [solutions|0] in RREF
    while rank(Y) < n - 1:
        # run until we get a new solution, y
        y = next(iter(backend.run(qc, shots=1).result().get_counts()))
        count += 1
        if (y in solutions): continue
        print("y[" + str(len(solutions)) + "] = " + y)
        solutions.add(y)
        Y.append([int(digit) for digit in y] + [0])

        # solve for s with what we have so far
        rref_mod2(Y)
        Y = [row for row in Y if not all([ele == 0 for ele in row])]  # remove all 0 rows
    print()

    # print solution
    print("Augmented solution matirx (RREF):")
    print_mat(Y, augmented=True)
    print()
    print("Iterations: ", count)
