import qrcode
import time
from ascon import encrypt, decrypt
import os
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class Kiosk:
    def __init__(self, grid_authority, simulate_hardware_failure=False):
        self.grid_authority = grid_authority
        self.fid = None
        self.franchise = None
        self.current_vfid = None
        # self.current_qr_code = None
        self.simulate_hardware_failure = simulate_hardware_failure
        self.key = os.urandom(16)

        with open("private.pem", "rb") as f:
            self.private_key = RSA.import_key(f.read())

    def receive_fid(self, fid: str, franchise=None):
        self.fid = fid
        self.franchise = franchise
        # self.current_qr_code = self.generate_qr()

    def generate_qr(self):
        qr = qrcode.QRCode(border=1)
        qr.add_data(self.current_vfid)
        qr.make(fit=True)

        qr.print_ascii()

    def initiate_transaction(self):
        if self.fid == None: 
            raise ValueError("FID not available")

        enc_packet = self.lwc_encrypt(self.fid)
        self.current_vfid = self.make_vfid(enc_packet)

    def handle_user_request(self, request):
        '''
        1. Validate vFID, decrypt it to recover actual FID (LWC)
        2. Decrypt VMID and PIN (RSA)
        3. Forward auth request to Grid Authority
        4. Relay response: notify franchise to unlock cable; trigger refund on hardware failure
        5. Return response to caller
        '''
        
        received_vfid = request["vfid"]
        if received_vfid != self.current_vfid:
            raise ValueError("vfid value received from user device is not correct")

        fid = self.lwc_decrypt(received_vfid)  # recover real FID from vFID

        grid_request = {
            "fid": fid,
            "vmid": self.rsa_decrypt(request["vmid"]),
            "pin": self.rsa_decrypt(request["pin"]),
            "amount": request["amount"]
        }

        response = self.grid_authority.process_transaction(grid_request)

        if response["status"] == "success":
            if self.franchise:
                self.franchise.receive_confirmation(True)
            
            if self.simulate_hardware_failure:
                print("[Kiosk] Hardware failure after payment. Initiating refund...")
                refund = self.grid_authority.process_refund(
                    response["uid"], fid, request["amount"]
                )
                response = {
                    "status": "refunded",
                    "message": "Payment refunded due to hardware failure",
                    "txn_id": refund["txn_id"]
                }
        else:
            if self.franchise:
                self.franchise.receive_confirmation(False)

        return response


    def lwc_encrypt(self, fid: str):
        payload = {
                "fid": fid,
                "ts": int(time.time())
        }

        nonce = os.urandom(16)
        plaintext = json.dumps(payload).encode()

        ciphertext = encrypt(key=self.key, nonce=nonce, associateddata=b"", plaintext=plaintext, variant="Ascon-128")

        return {
                "nonce": nonce,
                "ciphertext": ciphertext
        }

    def lwc_decrypt(self, vfid: str):
        nonce_b64, ct_b64 = vfid.split(".")
        nonce = base64.urlsafe_b64decode(nonce_b64)
        ciphertext = base64.urlsafe_b64decode(ct_b64)
        plaintext = decrypt(key=self.key, nonce=nonce, associateddata=b"", ciphertext=ciphertext, variant="Ascon-128")
        if plaintext is None:
            raise ValueError("Decryption of vfid failed on kiosk end")

        payload = json.loads(plaintext.decode())
        return payload['fid']

    def make_vfid(self, packet):
        nonce_b64 = base64.urlsafe_b64encode(packet['nonce']).decode()
        ct_b64 = base64.urlsafe_b64encode(packet['ciphertext']).decode()

        return f"{nonce_b64}.{ct_b64}"

    def rsa_decrypt(self, ct):
        cipher = PKCS1_OAEP.new(self.private_key)
        return cipher.decrypt(ct).decode()
