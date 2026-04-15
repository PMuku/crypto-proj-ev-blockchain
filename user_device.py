from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class UserDevice:
    def __init__(self):
        with open("public.pem", "rb") as f:
            self.public_key = RSA.import_key(f.read())

    def make_transaction(self, kiosk, vfid=None, vmid=None, pin=None, amount=None):
        '''
        1. Scan QR → read vFID (base64 string from QR code)
        2. Enter: VMID, PIN, Amount
        3. RSA-encrypt VMID and PIN
        4. Send encrypted payload to kiosk
        '''
        if vfid is None:
            vfid = input("Scan QR (enter vFID): ").strip()
        if vmid is None:
            vmid = input("Enter VMID: ").strip()
        if pin is None:
            pin = input("Enter PIN: ").strip()
        if amount is None:
            amount = float(input("Enter amount: ").strip())

        response = kiosk.handle_user_request(
            {
                "vfid":   vfid,
                "vmid":   self.rsa_encrypt(vmid),
                "pin":    self.rsa_encrypt(pin),
                "amount": amount
            }
        )

        if response["status"] == "success":
            print(f"[User Device] Payment successful! TxnID: {response['txn_id']}")
        elif response["status"] == "refunded":
            print(f"[User Device] Payment refunded (hardware failure). TxnID: {response['txn_id']}")
        else:
            print(f"[User Device] Payment failed: {response['message']}")

        return response

    def rsa_encrypt(self, pt: str):
        cipher = PKCS1_OAEP.new(self.public_key)
        return cipher.encrypt(pt.encode())
