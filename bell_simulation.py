from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import os

def run_bell_state_simulation(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Create Bell State
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Step 2: Simulate
    simulator = AerSimulator()
    result = simulator.run(qc).result()
    counts = result.get_counts()

    # Step 3: Circuit
    circuit_path = os.path.join(output_dir, 'circuit.png')
    qc.draw('mpl')
    plt.savefig(circuit_path, bbox_inches='tight')
    plt.close()

    # Step 4: Bloch Sphere
    bloch_path = os.path.join(output_dir, 'bloch.png')
    state = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    plot_bloch_multivector(state)
    plt.savefig(bloch_path, bbox_inches='tight')
    plt.close()

    # Step 5: Histogram
    hist_path = os.path.join(output_dir, 'histogram.png')
    plot_histogram(counts)
    plt.savefig(hist_path, bbox_inches='tight')
    plt.close()
