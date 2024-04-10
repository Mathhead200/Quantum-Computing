from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import UnitaryGate
from matplotlib import pyplot

backend = Aer.get_backend('qasm_simulator')

def not_deutsch2(gate: UnitaryGate, show=True, style="iqp"):
	qc = QuantumCircuit(3, 1)  # add a third ancilla qubit, q[2]
	qc.h([0])  # DIFFERENT: only place Hadamard gate on wire 0
	qc.append(gate, [1])  # input function
	qc.cx(0, 1)

	# my changes here:
	qc.h(2)  # add a Hadamard gate to the ancilla qubit
	qc.cswap(2, 0, 1)  # swap qubits 0 <-> 1 controlled by ancilla
	qc.h(2)  # undo Hadamard
	qc.measure(2, 0)  # measure ancilla, q[2], (to c[0])

	qc.draw("mpl", style=style, filename=f"circuit-{gate.label}.png")
	
	qc = transpile(qc, backend=Aer.get_backend('qasm_simulator'))
	result = backend.run(qc).result()
	plot_histogram(result.get_counts(), filename=f"histogram-{gate.label}.png")
	if (show): pyplot.show()
	return result

def mode(d: dict):
	return max(d, key=d.get)

if __name__ == "__main__":
	f0 = UnitaryGate([[1, 0], [0, 1]], label="f0")
	f1 = UnitaryGate([[1, 0], [0, -1]], label="f1")
	f2 = UnitaryGate([[-1, 0], [0, 1]], label="f2")
	f3 = UnitaryGate([[-1, 0], [0, -1]], label="f3")
	
	histograms = {f.label: not_deutsch2(f, show=False).get_counts() for f in [f0, f1, f2, f3]}
	interpret = { "0": "constant", "1": "balanced" }
	print({k: interpret[mode(h)] for k, h in histograms.items()})
