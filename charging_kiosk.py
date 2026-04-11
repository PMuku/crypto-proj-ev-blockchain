
import qrcode
import time
from ascon import encrypt, decrypt
import os
import json
import base64

class Kiosk:
    def __init__(self, grid_authority):
        self.grid_authority = grid_authority
        self.fid = None
        self.current_vfid = "abcd"
        self.current_qr_code = None

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

    def lwc_encrypt(self, fid: str):
        payload = {
                "fid": fid,
                "ts": int(time.time())
        }

        key = os.urandom(16)
        nonce = os.urandom(16)
        plaintext = json.dumps(payload).encode()

        ciphertext = encrypt(key=key, nonce=nonce, associateddata=None, plaintext=plaintext, variant="Ascon-128")

        return {
                "nonce": nonce,
                "ciphertext": ciphertext
        }

    def lwc_decrypt(self, packet):
        pass

    def make_vfid(self, packet):
        nonce_b64 = base64.urlsafe_b64encode(packet['nonce']).decode()
        ct_b64 = base64.urlsafe_b64encode(packet['cipertext']).decode()

        return f"{nonce_b64}.{ct_b64}"

