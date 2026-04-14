

import math
import random


def quantum_period_finding(a: int, n: int) -> int | None:

    x = a % n
    for r in range(1, n + 1):
        if x == 1:
            return r
        x = (x * a) % n
    return None


def shors_factor(n: int) -> tuple[int | None, int | None]:
    """
    Returns (p, q) on success, (None, None) on failure.
    """
    if n % 2 == 0:
        return 2, n // 2

    for _ in range(200):
        a = random.randint(2, n - 1)

        # Lucky shortcut: GCD already reveals a factor
        g = math.gcd(a, n)
        if 1 < g < n:
            return g, n // g

        # Quantum step: find period r of f(x) = a^x mod n
        r = quantum_period_finding(a, n)
        if r is None or r % 2 != 0:
            continue

        # Extract factor candidates
        cand_p = math.gcd(pow(a, r // 2) - 1, n)
        cand_q = math.gcd(pow(a, r // 2) + 1, n)

        if 1 < cand_p < n:
            return cand_p, n // cand_p
        if 1 < cand_q < n:
            return cand_q, n // cand_q

    return None, None

def demonstrate_shor_attack(vmid: str = "9876543210ab1234", pin: str = "4567"):

    print("\n" + "=" * 64)
    print("  QUANTUM ATTACK SIMULATION — Shor's Algorithm on RSA")
    print("=" * 64)

    # RSA Setup
    p, q = 127, 131                 # small primes for classical demo
    n    = p * q                    # modulus = 16637
    e    = 17                       # public exponent 

    phi_n = (p - 1) * (q - 1)
    assert math.gcd(e, phi_n) == 1, "e must be coprime to phi(n)"
    d = pow(e, -1, phi_n)           # private exponent (secret)

    print(f"\n[Setup] EV system RSA public key (simulated small key for demo):")
    print(f"  Modulus  n = {n}  (= {p} × {q})")
    print(f"  Public   e = {e}")
    print(f"  Private  d = {d}  ← attacker does NOT know this")

    #  Encrypt a 2-byte slice of the PIN 
    secret_int  = int.from_bytes(pin[:2].encode(), "big")
    ciphertext  = pow(secret_int, e, n)          # textbook RSA encrypt

    print(f"\n[Intercept] Attacker eavesdrops on the network and captures:")
    print(f"  Ciphertext c = {ciphertext}  (encrypted PIN bytes)")
    print(f"  Public key   (n={n}, e={e})")
    print(f"\n[Shor's Attack] Factoring n={n} with quantum period-finding ...")

    # Run Shor's algorithm
    found_p, found_q = shors_factor(n)

    if found_p is None:
        print("[Shor's Attack] Factoring failed (increase attempts).")
        return

    print(f"[Shor's Attack] Factored!  p = {found_p},  q = {found_q}")

    recovered_phi = (found_p - 1) * (found_q - 1)
    recovered_d   = pow(e, -1, recovered_phi)
    print(f"[Shor's Attack] Recovered private key  d = {recovered_d}")

    recovered_int = pow(ciphertext, recovered_d, n)
    recovered_pin = recovered_int.to_bytes(2, "big").decode(errors="replace")
    print(f"[Shor's Attack] Decrypted PIN bytes:  '{recovered_pin}'")
    print(f"[Result]        Original PIN was:     '{pin[:2]}'")
    print(f"                Match: {recovered_pin == pin[:2]}")

    # Implication 
    print(f"""
[Implication]
  The EV system transmits VMID and PIN encrypted with 2048-bit RSA.
  On a sufficiently large quantum computer, Shor's Algorithm factors
  a 2048-bit modulus in O(log³ n) ≈ 10⁹ quantum gate operations —
  feasible with ~4000 logical qubits (Beauregard 2003).

  Once n is factored, every intercepted VMID/PIN ciphertext can be
  decrypted offline, enabling:
    • Identity theft (spoofed VMID)
    • Fraudulent charging sessions
    • Replay attacks

  Post-quantum mitigation: replace RSA with CRYSTALS-Kyber (NIST
  PQC standard, lattice-based, quantum-resistant).
""")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    demonstrate_shor_attack()
