from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class UserDevice:
    def __init__(self):
        with open("public.pem", "rb") as f:
            self.public_key = RSA.import_key(f.read())

    def make_transaction(self, kiosk):
        '''
        1. Scan QR → get encrypted FID
        2. Enter: VMID, PIN, Amount
        3. Hash PIN
        4. Encrypt the data
        5. Send to kiosk

        The details should be RSA encrypted
        '''
        # decrpyt QR for fid
        vfid = int(input())
        vmid = str(input())
        pin = str(input())
        amount = int(input())

        kiosk.handle_user_request(
            {
                "vfid": vfid,
                "vmid": self.rsa_encrypt(vmid),
                "pin": self.rsa_encrypt(pin),
                "amount": amount
            }
        )
        

    def rsa_encrypt(self, pt: str):
        cipher = PKCS1_OAEP.new(self.public_key)
        return cipher.encrypt(pt.encode())

