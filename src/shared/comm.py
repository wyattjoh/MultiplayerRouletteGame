import json

debug_mode = False

PORT = 9004

def prepare_data(data):
    if debug_mode:
        print("Preparing data:" + str(data))
    
    data = json.dumps(data)
    data = data.encode('utf-8')
    
    return data

def extract_data(data):
    data = json.loads(data)

    if debug_mode:
        print("Extracted data:" + str(data))
    
    return data
