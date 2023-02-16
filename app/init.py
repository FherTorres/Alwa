import json, requests, time


#Config
dspace_ip = "192.168.1.64"


subcomunitties = ['Xelhua', 'Nez', 'Painal', 'Chimalli']
collections = ['Documentacion', 'Software (codigo)', 'Base de datos', 'Contenedores (servicios)', 'Multimedia']
dspace_url = "http://"+dspace_ip+":8080/server/api"
user="test@test.edu"
password="admin"

with open('dspace_templates/community_template.json') as json_file:
    data = json.load(json_file)

with open('dspace_templates/collection_template.json') as json_file_2:
            collection_data = json.load(json_file_2)






#Start flow
print("FIRST GET!!!")
url = dspace_url+"/authn/status"
payload = json.dumps({})
    
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
    
response = requests.request("GET", url, headers=headers, data=payload)
print(response)
print(response.cookies)
cookie_dict = dict(response.cookies)

XSRF_COOKIE = cookie_dict["DSPACE-XSRF-COOKIE"]








print("\n\n\n LOGIN!!!!!")
url = dspace_url+"/authn/login?user="+user+"&password="+password

payload={}
headers = {
    'X-XSRF-TOKEN': XSRF_COOKIE,
    'Cookie': 'DSPACE-XSRF-COOKIE='+XSRF_COOKIE
}
print(response)
print(headers)

response = requests.request("POST", url, headers=headers, data=payload)
print(response.headers)
    

headers_dict = dict(response.headers)

XSRF_COOKIE = headers_dict['DSPACE-XSRF-TOKEN']
token_bearer = headers_dict['Authorization']
    
print(XSRF_COOKIE)
print(token_bearer)   





print("\n\nINSERT COMMUNITY!!")
url = dspace_url+"/core/communities"

payload = json.dumps(data)
headers = {
    'X-XSRF-TOKEN': XSRF_COOKIE,
    'Authorization': token_bearer,
    'Content-Type': 'application/json',
    'Cookie': 'DSPACE-XSRF-COOKIE='+XSRF_COOKIE
}
    
community_response = requests.request("POST", url, headers=headers, data=payload).json()

print(community_response)


url = dspace_url+"/core/communities?parent="+community_response['uuid']
headers = {
    'X-XSRF-TOKEN': XSRF_COOKIE,
    'Authorization': token_bearer,
    'Content-Type': 'application/json',
    'Cookie': 'DSPACE-XSRF-COOKIE='+XSRF_COOKIE
}





for subcomunity in subcomunitties:
    print("\n\n\nINSERT SUBCOMMUNITY!!!")

    data['name'] = subcomunity
    data['metadata']['dc.title'][0]['value'] = subcomunity
    print(data)
    payload = json.dumps(data)
        
        
    subcommunity_response = requests.request("POST", url, headers=headers, data=payload).json()

    print(subcommunity_response)

    url_subcommunity = dspace_url+"/core/collections?parent="+subcommunity_response['uuid']
    
    
    
    for collection in collections:
        print("\n\n\n INSERT COLLECTION")

        collection_data['name'] = collection
        collection_data['metadata']['dc.title'][0]['value'] = collection
        print(collection_data)
        collection_payload = json.dumps(collection_data)
        headers = {
            'X-XSRF-TOKEN': XSRF_COOKIE,
            'Authorization': token_bearer,
            'Content-Type': 'application/json',
            'Cookie': 'DSPACE-XSRF-COOKIE='+XSRF_COOKIE
        }
        response = requests.request("POST", url_subcommunity, headers=headers, data=collection_payload).json()
        print(response)
        time.sleep(2)