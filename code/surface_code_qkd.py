"""
Topological Surface Code Error Correction for Free-Space Satellite QKD
Stabiliser Code Simulation for Quantum Key Distribution
"""
import numpy as np

def pauli_x(state, qubit, n):
    """Apply Pauli X to qubit in an n-qubit state vector."""
    for i in range(len(state)):
        if not (i >> qubit & 1):
            j = i | (1 << qubit)
            if j > i:
                state[i], state[j] = state[j], state[i]
    return state

def depolarising_channel(n_qubits, p_error=0.01, seed=42):
    """Simulate depolarising errors on n qubits."""
    np.random.seed(seed)
    errors = np.zeros((n_qubits, 2), dtype=int)  # col0=X, col1=Z
    for q in range(n_qubits):
        r = np.random.rand()
        if r < p_error / 3:
            errors[q, 0] = 1  # X error
        elif r < 2 * p_error / 3:
            errors[q, 1] = 1  # Z error
        elif r < p_error:
            errors[q, 0] = errors[q, 1] = 1  # Y error
    return errors

def distance_3_surface_code_syndrome(errors):
    """
    Distance-3 surface code (9 data qubits, 4 X-stabilisers, 4 Z-stabilisers).
    Returns syndrome bits for error detection.
    """
    # Simplified planar code stabiliser map
    x_stab = [[0,1,3,4], [1,2,4,5], [3,4,6,7], [4,5,7,8]]
    z_stab = [[0,1,3,4], [1,2,4,5], [3,4,6,7], [4,5,7,8]]
    x_syndrome = [sum(errors[q, 1] for q in s) % 2 for s in x_stab]
    z_syndrome = [sum(errors[q, 0] for q in s) % 2 for s in z_stab]
    return np.array(x_syndrome), np.array(z_syndrome)

def minimum_weight_matching(syndrome):
    """Simple greedy error correction from syndrome."""
    error_estimate = np.zeros(9, dtype=int)
    for i, s in enumerate(syndrome):
        if s:
            error_estimate[i * 2 % 9] = 1  # simplified
    return error_estimate

def simulate_qkd_bb84(n_bits=1000, p_channel=0.05, p_eva=0.0, seed=42):
    np.random.seed(seed)
    alice_bits  = np.random.randint(0, 2, n_bits)
    alice_bases = np.random.randint(0, 2, n_bits)
    bob_bases   = np.random.randint(0, 2, n_bits)
    # Channel errors
    received = alice_bits.copy()
    flip = np.random.rand(n_bits) < p_channel
    received[flip] ^= 1
    # Sifting
    sifted = alice_bases == bob_bases
    sifted_key = alice_bits[sifted]
    received_key = received[sifted]
    qber = (sifted_key != received_key).mean()
    return sifted_key, received_key, float(qber)

if __name__ == "__main__":
    print("Simulating satellite QKD with surface code error correction...")
    errors = depolarising_channel(9, p_error=0.05)
    x_syn, z_syn = distance_3_surface_code_syndrome(errors)
    print(f"  Error pattern  : {errors.tolist()}")
    print(f"  X-syndrome     : {x_syn.tolist()}")
    print(f"  Z-syndrome     : {z_syn.tolist()}")
    key_a, key_b, qber = simulate_qkd_bb84(n_bits=10000, p_channel=0.03)
    print(f"  Sifted key len : {len(key_a)}")
    print(f"  QBER           : {qber:.4f} ({qber*100:.2f}%)")
    print(f"  Key agreement  : {'SECURE' if qber < 0.11 else 'ABORT'}")
    print("QKD surface code simulation complete.")
