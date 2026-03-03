import requests

try:
    sids = []
    print("Fetching 3 SIDs rapidly...")
    for i in range(3):
        r = requests.get('https://info.hotelshanmugabhavaan.com/socket.io/?EIO=4&transport=polling', timeout=10)
        import json
        text = r.text
        if text.startswith('0'):
            data = json.loads(text[1:])
            sids.append(data['sid'])
            print(f"Got SID {i}: {data['sid']}")
        else:
            print("Failed to get SID:", text)
    
    if len(sids) > 0:
        print(f"Polling SID {sids[0]}...")
        r2 = requests.get(f'https://info.hotelshanmugabhavaan.com/socket.io/?EIO=4&transport=polling&sid={sids[0]}', timeout=10)
        print("Poll response 1:", r2.status_code, r2.text)
        r3 = requests.get(f'https://info.hotelshanmugabhavaan.com/socket.io/?EIO=4&transport=polling&sid={sids[0]}', timeout=10)
        print("Poll response 2:", r3.status_code, r3.text)

except Exception as e:
    print("Exception:", e)
