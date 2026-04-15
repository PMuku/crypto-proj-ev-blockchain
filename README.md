## Project Overview

A simulation of a secure EV charging payment gateway that demonstrates real-world cryptographic techniques applied to an IoT billing scenario.

The system models three central energy providers (TATA, ADANI, ChargePoint), each with regional zones. Within each zone, franchises (charging station operators) register with the Grid Authority and set up kiosks. EV owners register as users, then pay for charging sessions through those kiosks.

**Key components:**

| Component | Role |
|---|---|
| Grid Authority | Central authority which registers users and franchises, processes and records transactions on the blockchain |
| Franchise | Charging station operator which provides charging services through the kiosk |
| Charging Kiosk | Edge device : reads the VFID from its QR code, validates the user's credentials, and forwards payment requests to the Grid |
| User Device | Simulates an EV owner scanning a kiosk QR code and initiating a payment |
| Blockchain | Immutable ledger of all transactions, including refunds flagged from hardware failures |

**Cryptographic techniques used:**

- **SHA-3 (Keccak-256)** — hashing for FID generation and PIN storage
- **RSA (2048-bit)** — encrypting VMID and PIN during transmission from user device to kiosk
- **ASCON** — lightweight authenticated encryption for generating and protecting the VFID in the kiosk QR code
- **Shor's Algorithm (simulated)** — demonstration of a quantum factoring attack on RSA

---

## How to Run

### Prerequisites
- Python 3.10+

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd crypto-proj-ev-blockchain
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install pycryptodome Pillow ascon qrcode
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   RSA keys (`private.pem` / `public.pem`) are generated automatically on first run if not already present.

---

## Assumptions

### Franchise ID (FID) Generation

> The Grid generates a 16-digit Franchise ID (FID). FID is formed using their name, time of account creation, and password hashed using the SHA-3 (Keccak-256) algorithm.

The FID is computed as the Keccak-256 hash of the three strings (name, time of account creation, and password) concatenated together, rather than hashing the password separately before combining.

---

### Payment Process & Transaction Processing

> Payment Process: The EV Owner scans the QR code, providing their VMID, required charging amount (in currency), and PIN to initiate the session. This data is hashed and sent to the Charging Kiosk.
>
> Transaction Processing: The Charging Kiosk decrypts the Franchise ID from the QR code, forwards the authorization request to the Grid Authority, and waits for approval to begin dispensing power.
>
> Grid Processing: The Grid decrypts the user credentials and validates the funds, VMID, and PIN. If successful, the transaction is recorded in the blockchain, and funds are transferred to the Franchise.

Rather than hashing the VMID and PIN, they are encrypted using RSA. Validation of credentials (VMID and PIN) is performed at the Charging Kiosk rather than at the Grid; the Kiosk then forwards the authorization request to the Grid to approve and record the payment on the blockchain.

---

### Role of Lightweight Cryptography (LWC)

> LWC is critical because EV charging stations and vehicle communication modules often operate on constrained embedded systems. LWC is used for:
> - Generating a Virtual Franchise ID (VFID) from the original FID and a timestamp.
> - Ensuring low computational overhead to reduce authorization delays at the plug.
> - Encrypting Franchise ID in the QR code.
> - Use the ASCON algorithm for lightweight cryptography, designed for secure, high-speed encryption in resource-constrained IoT environments.

The VFID is used for QR code generation.

---

## Team Members
- Vignesh Karri &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2023A7PS0142H
- Pranav Mukundan &nbsp;&nbsp; 2023A7PS1101H
- Aarav Sinha &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2023A7PS2001H
- Shreyas Pathak &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2023A7PS0136H
- Jeremy Karra &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2022A7PS2008H