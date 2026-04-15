import os
import sys
import hmac
import hashlib

if not (os.path.exists("private.pem") and os.path.exists("public.pem")):
    print("[Setup] Generating 2048-bit RSA key pair...")
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    with open("private.pem", "wb") as f:
        f.write(key.export_key())
    with open("public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print("[Setup] Keys written to private.pem and public.pem\n")
else:
    print("[Setup] RSA keys already present.\n")

import grid_authority as ga
from charging_kiosk import Kiosk
from franchise import Franchise
from user_device import UserDevice
from blockchain.blockchain import Blockchain
from shor_simulation import demonstrate_shor_attack

SEP = "\n" + "-" * 64 + "\n"

def display_zones():
    print("\n[Grid] Registered energy providers and zones:")
    for provider, zones in ga.PROVIDERS.items():
        print(f"  {provider:12s} -> {', '.join(zones)}")

def main_menu():
    my_franchises = {}
    my_kiosks = {}
    my_users = {} # Store basic info for easy access in menu

    while True:
        print(SEP)
        print("  SECURE EV CHARGING PAYMENT GATEWAY - MENU")
        print("-" * 64)
        print("1. View Available Grid Zones")
        print("2. Register Franchise")
        print("3. Register User")
        print("4. Setup Kiosk (Assign Franchise FID)")
        print("5. Initiate Transaction (Make Payment)")
        print("6. View Blockchain Ledger")
        print("7. Quantum Attack Simulation (Shor's)")
        print("8. Check Balances")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == '1':
            display_zones()
            
        elif choice == '2':
            name = input("Enter Franchise Name: ").strip()
            display_zones()
            zone = input("Enter Zone Code (e.g. TATA-SOUTH): ").strip()
            pwd = input("Enter Password: ").strip()
            bal = float(input("Enter Initial Balance: ").strip())

            try:
                fid = ga.register_franchise(name=name, zone_code=zone, pwd=pwd, bal=bal)
                franchise_obj = Franchise(name=name, zone_code=zone, fid=fid, account_number=f"ACC-{len(my_franchises)}", balance=bal)
                my_franchises[fid] = franchise_obj
                print(f"[Success] Franchise generated FID: {fid}")
            except Exception as e:
                print(f"[Error] {e}")

        elif choice == '3':
            name = input("Enter User Name: ").strip()
            pin = input("Enter 4-digit PIN: ").strip()
            bal = float(input("Enter Initial Balance: ").strip())
            mobile = input("Enter Mobile Number: ").strip()
            display_zones()
            zone = input("Enter Zone Code: ").strip()
            
            try:
                uid, vmid = ga.register_user(name=name, pin=pin, bal=bal, mobile=mobile, zone_code=zone)
                my_users[vmid] = {"uid": uid, "name": name}
                print(f"[Success] User {name} registered with VMID: {vmid}")
            except Exception as e:
                print(f"[Error] {e}")

        elif choice == '4':
            if not my_franchises:
                print("[!] Register a franchise first.")
                continue
            print("Select Franchise:")
            fids = list(my_franchises.keys())
            for i, f_id in enumerate(fids):
                print(f" {i+1}. {my_franchises[f_id].name} (FID: {f_id})")
            try:
                f_idx = int(input("Choice: ")) - 1
                sel_fid = fids[f_idx]
                franchise_obj = my_franchises[sel_fid]
                pwd = input("Enter franchise password: ")                    
                if ga.stored_franchises[sel_fid]["hashed_pwd"] == ga.sha3_hash(pwd):
                    try: 
                        fail_sim = input("Simulate Hardware Failure for refunds at this Kiosk? (y/N): ").strip().lower() == 'y'

                        kiosk = Kiosk(grid_authority=ga, simulate_hardware_failure=fail_sim)
                        franchise_obj.enter_fid_to_kiosk(kiosk)
                        kiosk_id = f"Kiosk-{len(my_kiosks)+1}"
                        my_kiosks[kiosk_id] = kiosk
                        
                        print(f"[Kiosk] vFID generated: {kiosk.current_vfid}")
                        print(f"[Kiosk] ID assigned to {kiosk_id}")

                    except Exception as e:
                       print(f"[Error setup] {e}")

                else:
                    print("[Error] Invalid Password. Access Denied.")
 
            except Exception as e:
                print(f"[Error setup] {e}")

        elif choice == '5':
            if not my_kiosks:
                print("[!] Setup a kiosk first.")
                continue
            
            print("Select Kiosk to Transact with:")
            k_ids = list(my_kiosks.keys())
            for i, k_id in enumerate(k_ids):
                print(f" {i+1}. {k_id} (Assigned to: {my_kiosks[k_id].franchise.name})")
            
            try:
                k_idx = int(input("Choice: ")) - 1
                kiosk_obj = my_kiosks[k_ids[k_idx]]
                kiosk_obj.initiate_transaction()

                kiosk_obj.generate_qr()

                vfid = input("Enter VFID(Scan QR)").strip()
                vmid = input("Enter your VMID: ").strip()
                pin = input("Enter your PIN: ").strip()
                amount = float(input("Enter amount: ").strip())
                
                user_device = UserDevice()
                user_device.make_transaction(kiosk=kiosk_obj, vfid=vfid, vmid=vmid, pin=pin, amount=amount)
            except Exception as e:
                print(f"[Error processing transaction]: {e}")
                
        elif choice == '6':
            ga.blockchain.print_chain()
            print(f"[Blockchain] Chain valid: {ga.blockchain.is_chain_valid()}")
            
        elif choice == '7':
            vmid = input("Enter target VMID (leave blank for demo): ").strip()
            pin = input("Enter actual PIN to compare (leave blank for demo): ").strip()
            if not vmid: vmid = "9876543210123456"  # Mock VMID for demo
            if not pin: pin = "4567"
            try:
                demonstrate_shor_attack(vmid=vmid, pin=pin)
            except Exception as e:
                print(f"[Error running quantum attack] {e}")

        elif choice == '8':
            print("1. Check User Balance")
            print("2. Check Franchise Balance")
            sub_choice = input("Select account type: ").strip()

            if sub_choice == '1':
                if not my_users:
                    print("[!] No users registered.")
                    continue
                vmid = input("Enter your VMID: ").strip()
                if vmid in my_users:
                    uid = my_users[vmid]["uid"]
                    pin = input("Enter 4-digit PIN: ").strip()
                    if ga.stored_users[uid]["hashed_pin"] == ga.sha3_hash(pin):
                        bal = ga.stored_users[uid]['balance']
                        print(f"[Success] {my_users[vmid]['name']} Balance: ₹{bal:.2f}")
                    else:
                        print("[Error] Invalid PIN. Access Denied.")
                else:
                    print("[Error] VMID not found.")
                    
            elif sub_choice == '2':
                if not my_franchises:
                    print("[!] No franchises registered.")
                    continue
                fid = input("Enter Franchise ID (FID): ").strip()
                if fid in ga.stored_franchises:
                    pwd = input("Enter Franchise Password: ").strip()
                    if ga.stored_franchises[fid]["hashed_pwd"] == ga.sha3_hash(pwd):
                        f_name = ga.stored_franchises[fid]["name"]
                        bal = ga.stored_franchises[fid]['balance']
                        print(f"[Success] {f_name} Balance: ₹{bal:.2f}")
                    else:
                        print("[Error] Invalid Password. Access Denied.")
                else:
                    print("[Error] FID not found.")
            else:
                print("Invalid selection.")

        elif choice == '9':
            print("Exiting...")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main_menu()

