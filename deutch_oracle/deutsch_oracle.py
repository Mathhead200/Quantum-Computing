from qiskit import QuantumCircuit, transpile
# from qiskit_ibm_runtime import *
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import UnitaryGate
from matplotlib import pyplot

backend = Aer.get_backend('qasm_simulator')

# style = "iqp"|"clifford"
def deutsch(gate: UnitaryGate, show=True, style="iqp"):
	qc = QuantumCircuit(2, 1)
	qc.x([1])
	qc.barrier()
	qc.h([0, 1])
	qc.append(gate, range(2))  # input function
	qc.h([0, 1])
	qc.measure(0, 0)
	qc.draw("mpl", style=style, filename=f"circuit-{gate.label}.png")
	
	qc = transpile(qc, backend=Aer.get_backend('qasm_simulator'))
	result = backend.run(qc).result()
	plot_histogram(result.get_counts(), filename=f"histogram-{gate.label}.png")
	if (show): pyplot.show()
	return result

def mode(d: dict):
	return max(d, key=d.get)

if __name__ == "__main__":
	f0 = UnitaryGate([
		[1, 0, 0, 0],
		[0, 1, 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]], label="f0")    # f(x) = 0
	f1 = UnitaryGate([
		[0, 0, 1, 0],
		[0, 0, 0, 1],
		[1, 0, 0, 0],
		[0, 1, 0, 0]], label="f1")   # f(x) = 1
	f2 = UnitaryGate([
		[1, 0, 0, 0],
		[0, 0, 0, 1],
		[0, 0, 1, 0],
		[0, 1, 0, 0]], label="f2")   # f(x) = x
	f3 = UnitaryGate([
		[0, 0, 1, 0],
		[0, 1, 0, 0],
		[1, 0, 0, 0],
		[0, 0, 0, 1]], label="f3")  # f(x) = 1-x
	
	histograms = {f.label: deutsch(f, show=False).get_counts() for f in [f0, f1, f2, f3]}
	interpret = { "0": "constant", "1": "balanced" }
	print({k: interpret[mode(h)] for k, h in histograms.items()})
