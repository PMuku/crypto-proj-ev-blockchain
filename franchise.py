class Franchise:
    def __init__(self, name, zone_code, fid, account_number, balance,
                 simulate_hardware_failure=False):
        self.name = name
        self.zone_code = zone_code
        self.fid = fid
        self.account_number = account_number
        self.balance = balance
        self.simulate_hardware_failure = simulate_hardware_failure

    def enter_fid_to_kiosk(self, kiosk):
        kiosk.receive_fid(self.fid, franchise=self)

    def receive_confirmation(self, success):
        if success:
            if self.simulate_hardware_failure:
                print(f"[Franchise: {self.name}] Payment confirmed but hardware FAILURE — cable did not unlock.")
                return False  # triggers refund in kiosk
            print(f"[Franchise: {self.name}] Payment confirmed. Unlocking charging cable.")
            return True
        else:
            print(f"[Franchise: {self.name}] Payment failed. Charging cable remains locked.")
            return False

