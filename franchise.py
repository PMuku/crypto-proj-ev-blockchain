class Franchise:
    def __init__(self, name, zone_code, fid, account_number, balance):
        self.name = name
        self.zone_code = zone_code
        self.fid = fid
        self.account_number = account_number
        self.balance = balance

    def enter_fid_to_kiosk(self, kiosk):
        kiosk.receive_fid(self.fid, franchise=self)

    def receive_confirmation(self, success):
        if success:
            print(f"[Franchise: {self.name}] Payment confirmed. Unlocking charging cable.")
            return True
        else:
            print(f"[Franchise: {self.name}] Payment failed. Charging cable remains locked.")
            return False
