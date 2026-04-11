def make_transaction():
    '''
    1. Scan QR → get encrypted FID
    2. Enter: VMID, PIN, Amount
    3. Hash PIN
    4. Encrypt the data
    5. Send to kiosk

    The details should be RSA encrypted
    '''
    
    # decrpyt QR for fid
    fid = int(input)
    vmid = int(input())
    pin = int(input())
    amount = int(input())
    
    return {vmid, pin, amount, fid}
