import qrcode
import time
from ascon import encrypt, decrypt
import os
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class Kiosk:
    def __init__(self, grid_authority):
        self.grid_authority = grid_authority
        self.fid = None
        self.current_vfid = "abcd"
        self.current_qr_code = None
        self.key = os.urandom(16)

        with open("private.pem", "rb") as f:
            self.private_key = RSA.import_key(f.read())

    def receive_fid(self, fid: str):
        self.fid = fid
        encrypted_packet = self.lwc_encrypt(fid)
        self.current_vfid = self.make_vfid(encrypted_packet)
        self.current_qr_code = self.generate_qr()
        self.current_qr_code.show()

    def generate_qr(self):
        qr = qrcode.make(self.current_vfid)
        return qr

    def handle_user_request(self, request):
        '''
        1. Decrypt FID and the request data
        2. Forward request to Grid
        3. Return response

        vmid and pin are rsa-encrypted
        '''
        received_vfid = request["vfid"]

    def lwc_encrypt(self, fid: str):
        payload = {
                "fid": fid,
                "ts": int(time.time())
        }

        nonce = os.urandom(16)
        plaintext = json.dumps(payload).encode()

        ciphertext = encrypt(key=self.key, nonce=nonce, associateddata=None, plaintext=plaintext, variant="Ascon-128")

        return {
                "nonce": nonce,
                "ciphertext": ciphertext
        }

    def lwc_decrypt(self, vfid: str):
        nonce_b64, ct_b64 = vfid.split(".")
        nonce = base64.urlsafe_b64decode(nonce_b64)
        ciphertext = base64.urlsafe_b64decode(ct_b64)
        plaintext = decrypt(key=self.key, nonce=nonce, associateddata=None, ciphertext=ciphertext, variant="Ascon-128")
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
        cipher.decrypt(ct).decode()


