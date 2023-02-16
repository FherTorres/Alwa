import json, requests, time


#Config
painal_ip = "192.168.1.70"
painal_port = "20500"

groups = ['Xelhua', 'Nez', 'Painal', 'Chimalli']
catalogs = ['Documentacion', 'Software (codigo)', 'Base de datos', 'Contenedores (servicios)', 'Multimedia']

painal_url = "http://"+painal_ip+":"+painal_port


user="TestAdmin"
email="admin@test.edu"
password="Admin_1*"






#Start flow
print("GET ORGANIZATIONS!!!")
url = painal_url+"/auth/v1/view/hierarchy/all"
payload = json.dumps({})
    
headers = {
}
    
response = requests.request("GET", url, headers=headers, data=payload).json()
print(response)



if 'data' in response:
    organizations = response['data']
    token_org = organizations[0]['tokenorg']
else:
    print("\n\n\nNO ORGANIZATIONS. NEED TO CREATE ONE!")
    url = painal_url + "/auth/v1/hierarchy/create"

    payload = json.dumps({
        "fullname": "CINVESTAV",
        "acronym": "Cinves",
        "fathers_token": "/"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    token_org = response['tokenhierarchy']

time.sleep(4)



print("\n\n\nCREATE USER!!!!")
url = painal_url + "/auth/v1/users/create"
payload = json.dumps({
  "username": user,
  "email": email,
  "password": password,
  "tokenorg": token_org
})

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)

time.sleep(4)



print("\n\n\nLOGIN!!!!")
url = painal_url+"/auth/v1/users/login"

payload = json.dumps({
  "user": user,
  "password": password
})

headers = {
}
response = requests.request("POST", url, headers=headers, data=payload).json()
print(response)

user_data = response['data']

token_user = user_data['tokenuser']
api_key = user_data['apikey']
access_token = user_data['access_token']

create_group_url = painal_url + "/pub_sub/v1/groups/create?access_token="+access_token
create_catalog_url = painal_url + "/pub_sub/v1/catalogs/create?access_token="+access_token


for group in groups:
    print("\n\n\nCREATE GROUP!!!")
    print(group)
    payload = json.dumps({
        "groupname": group,
        "fathers_token": "/",
        "isprivate": True
    })
    headers = {
         'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", create_group_url, headers=headers, data=payload).json()
    print(response)
    token_group = response['tokengroup']
    time.sleep(4)

for catalog in catalogs:
    print("\n\n\nCREATE CATALOG!!")
    print(catalog)
    payload = json.dumps({
        "catalogname": catalog,
        "dispersermode": "SINGLE",
        "encryption": True,
        "group": token_group,
        "fathers_token": "/",
        "processed": False
     })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", create_catalog_url, headers=headers, data=payload)
    print(response.text)
    time.sleep(3)
    





