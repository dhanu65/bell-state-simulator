from flask import Flask, render_template, request, jsonify
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
import matplotlib.pyplot as plt
import io, base64

app = Flask(__name__)

def fig_to_base64(fig):
    """Convert Matplotlib figure to base64 image (no saving)."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def create_bell_state(state_type: str):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if state_type == "phi_minus":
        qc.z(1)
    elif state_type == "psi_plus":
        qc.x(1)
    elif state_type == "psi_minus":
        qc.x(1)
        qc.z(1)
    return qc

BELL_STATE_INFO = {
    "phi_plus": {
        "label": "|Φ⁺⟩ = (|00⟩ + |11⟩)/√2",
        "description": "Perfect correlation between both qubits in-phase.",
        "phase_info": "In-phase superposition across |00⟩ and |11⟩."
    },
    "phi_minus": {
        "label": "|Φ⁻⟩ = (|00⟩ − |11⟩)/√2",
        "description": "Phase-shifted correlation between qubits.",
        "phase_info": "Relative phase of π between |00⟩ and |11⟩."
    },
    "psi_plus": {
        "label": "|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2",
        "description": "Qubits are opposite but with equal phase.",
        "phase_info": "Anti-correlated but in-phase superposition."
    },
    "psi_minus": {
        "label": "|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2",
        "description": "Opposite qubits with π phase difference.",
        "phase_info": "Used in teleportation and superdense coding."
    },
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run_simulation", methods=["POST"])
def run_simulation():
    try:
        data = request.get_json()
        bell_state = data.get("bell_state")
        shots = int(data.get("shots", 1024))

        if not bell_state:
            return jsonify({"status": "error", "message": "No Bell state selected."})

        qc = create_bell_state(bell_state)
        state = Statevector.from_instruction(qc)
        state_vector_values = [f"{amp.real:+.3f}{amp.imag:+.3f}j" for amp in state.data]

        # Measure for histogram
        qc.measure_all()
        simulator = AerSimulator()
        compiled = transpile(qc, simulator)
        result = simulator.run(compiled, shots=shots).result()
        counts = result.get_counts()

        # --- In-memory figures ---
        circuit_fig = qc.draw(output="mpl")
        bloch_fig = plot_bloch_multivector(state)
        hist_fig = plot_histogram(counts)

        # Convert to base64 (no file saving)
        circuit_img = fig_to_base64(circuit_fig)
        bloch_img = fig_to_base64(bloch_fig)
        hist_img = fig_to_base64(hist_fig)

        info = BELL_STATE_INFO[bell_state]

        return jsonify({
            "status": "success",
            "bell_label": info["label"],
            "description": info["description"],
            "phase_info": info["phase_info"],
            "statevector": state_vector_values,
            "circuit_img": circuit_img,
            "bloch_img": bloch_img,
            "hist_img": hist_img
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
