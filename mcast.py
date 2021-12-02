import socket
import struct
import requests
import json

BASE_URL = "http://192.168.48.226:2080"

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

multicast_group = '224.1.1.1'
server_address = ('', 1235)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind to the server address
sock.bind(server_address)

group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    data, address = sock.recvfrom(1024)
    decoded = data.decode('utf-8')
    try:
        tweet_split = decoded.split(',')
        tweet_type = tweet_split[0].strip()
        if 'Service' in tweet_type:
            jsonified_name = json.loads('{' + tweet_split[1].strip() + '}')
            name = jsonified_name['Name']
            jsonified_thing_id = json.loads('{' + tweet_split[2].strip() + '}')
            thing_id = jsonified_thing_id['Thing ID']
            jsonified_entity = json.loads('{' + tweet_split[3].strip() + '}')
            entity = jsonified_entity['Entity ID']
            jsonified_space = json.loads('{' + tweet_split[4].strip() + '}')
            space = jsonified_space['Space ID']

            service_data = {
                'name': name,
                'thing': thing_id,
                'entity': entity,
                'space': space
            }

            print('Found service : {}'.format(service_data))
            response = requests.post(BASE_URL + '/services', json=service_data)
        elif 'Identity_Thing' in tweet_type:
            jsonified_thing_id = json.loads('{' + tweet_split[1].strip() + '}')
            thing_id = jsonified_thing_id['Thing ID']
            jsonified_space_id = json.loads('{' + tweet_split[2].strip() + '}')
            space_id = jsonified_space_id['Space ID']
            jsonified_name = json.loads('{' + tweet_split[3].strip() + '}')
            name = jsonified_name['Name']
            jsonified_desc = json.loads('{' + tweet_split[7].strip() + '}')
            desc = jsonified_desc['Description']

            thing_data = {
                'id': thing_id,
                'space': space,
                'name': name,
                'desc': desc,
                'ip': extract_ip()
            }

            print('Found thing : {}'.format(thing_data))
            response = requests.post(BASE_URL + '/things', json=thing_data)
            
    except Exception as e:
        print(e)
        print(decoded)