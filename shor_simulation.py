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
    if n % 2 == 0:
        return 2, n // 2

    for _ in range(200):
        a = random.randint(2, n - 1)

        g = math.gcd(a, n)
        if 1 < g < n:
            return g, n // g

        r = quantum_period_finding(a, n)
        if r is None or r % 2 != 0:
            continue


        cand_p = math.gcd(pow(a, r // 2) - 1, n)
        cand_q = math.gcd(pow(a, r // 2) + 1, n)

        if 1 < cand_p < n:
            return cand_p, n // cand_p
        if 1 < cand_q < n:
            return cand_q, n // cand_q

    return None, None



def demonstrate_shor_attack(vmid: str = "9876543210ab1234", pin: str = "4567"):
    """
    Shows an attacker intercepting RSA-encrypted VMID/PIN and recovering them
    using Shor's Algorithm.

    We use a tiny RSA modulus (p=127, q=131) so the classical simulation runs
    instantly.  The attack logic is identical for 2048-bit keys on a quantum
    computer.
    """
    print("\n" + "=" * 64)
    print("  QUANTUM ATTACK SIMULATION — Shor's Algorithm on RSA")
    print("=" * 64)

    p, q = 127, 131     
    n    = p * q                    
    e    = 17                   

    phi_n = (p - 1) * (q - 1)
    assert math.gcd(e, phi_n) == 1, "e must be coprime to phi(n)"
    d = pow(e, -1, phi_n)

    print(f"\n[Setup] EV system RSA public key (simulated small key for demo):")
    print(f"  Modulus  n = {n}  (= {p} × {q})")
    print(f"  Public   e = {e}")
    print(f"  Private  d = {d}  ← attacker does NOT know this")

    secret_int  = int.from_bytes(pin[:2].encode(), "big")
    ciphertext  = pow(secret_int, e, n)         

    print(f"\n[Intercept] Attacker eavesdrops on the network and captures:")
    print(f"  Ciphertext c = {ciphertext}  (encrypted PIN bytes)")
    print(f"  Public key   (n={n}, e={e})")
    print(f"\n[Shor's Attack] Factoring n={n} with quantum period-finding ...")

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

if __name__ == "__main__":
    demonstrate_shor_attack()
