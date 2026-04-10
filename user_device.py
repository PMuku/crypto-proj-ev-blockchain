def make_transaction():
    '''
    1. Scan QR → get encrypted FID
    2. Enter: VMID, PIN, Amount
    3. Send to kiosk
    '''
    
    # decrpyt QR for fid
    fid = int(input)
    vmid = int(input())
    pin = int(input())
    amount = int(input())
    
    return {vmid, pin, amount, fid}