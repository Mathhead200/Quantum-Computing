from qiskit import *
from qiskit_ibm_runtime import *

if __name__ == "__main__":
	qc = QuantumCircuit(2, 1)
	qc.h([0, 1])
	qc.x(1)
	qc.draw("mpl", filename="out.png")
