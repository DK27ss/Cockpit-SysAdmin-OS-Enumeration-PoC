import requests
import argparse
import json
from urllib.parse import urlparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def spr(url, endpoint, payload):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    scheme = parsed_url.scheme
    
    headers = {
        "Host": f"{host}:{port}" if port else host,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    
    full_url = f"{url}{endpoint}"
    response = requests.post(full_url, headers=headers, json=payload, verify=False)
    
    try:
        return response.json()
    except json.JSONDecodeError:
        return None

def sgr(url, endpoint, cookies=None):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    
    headers = {
        "Host": f"{host}:{port}" if port else host,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    
    if cookies:
        headers["Cookie"] = cookies
    
    full_url = f"{url}{endpoint}"
    response = requests.get(full_url, headers=headers, verify=False)
    
    return response.text

def dsr(response_json):
    if response_json and "data" in response_json:
        data = response_json["data"]
        print("[+] System Ready:", "OK" if data.get("systemready") == "yes" else "NOT READY")
        print(" -  Uptime:", data.get("uptime", "N/A"))
        print(" -  Boot ID:", data.get("bootid", "N/A"))

def dbdi(response_json):
    if response_json and "data" in response_json and "propertyList" in response_json["data"]:
        prop_list = response_json["data"]["propertyList"]
        print("[+] Device Information:")
        print(" -  Product Number:", prop_list.get("ProdNbr", "N/A"))
        print(" -  Hardware ID:", prop_list.get("HardwareID", "N/A"))
        print(" -  Full Name:", prop_list.get("ProdFullName", "N/A"))
        print(" -  Version:", prop_list.get("Version", "N/A"))
        print(" -  Type:", prop_list.get("ProdType", "N/A"))
        print(" -  Brand:", prop_list.get("Brand", "N/A"))
        print(" -  Serial Number:", prop_list.get("SerialNumber", "N/A"))
        print(" -  Build Date:", prop_list.get("BuildDate", "N/A"))

def dl(response_text):
    if "OK" in response_text:
        print("[+] Login Successful")

def du(response_text):
    print("[+] User Groups:")
    for group in ["anonymous", "viewer"]:
        if group in response_text:
            print("    -", group)

def ps(url):
    print(f"\n[+] SERVER: {url}")
    print("="*40)
    
    systemready_payload = {"apiVersion": "1.0", "method": "systemready", "params": {"timeout": 10}}
    systemready_response = spr(url, "/axis-cgi/systemready.cgi", systemready_payload)
    dsr(systemready_response)
    print("="*40)
    
    basicdeviceinfo_payload = {"apiVersion": "1.3", "method": "getAllUnrestrictedProperties"}
    basicdeviceinfo_response = spr(url, "/axis-cgi/basicdeviceinfo.cgi", basicdeviceinfo_payload)
    dbdi(basicdeviceinfo_response)
    print("="*40)
    
    login_response_text = sgr(url, "/axis-cgi/login.cgi")
    dl(login_response_text)
    print("="*40)
    
    usergroup_response_text = sgr(url, "/axis-cgi/usergroup.cgi", cookies="_axis=g68MI7PkpY")
    du(usergroup_response_text)
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envoie des requêtes HTTP et affiche les réponses.")
    parser.add_argument("-u", "--url", help="URL au format http://IP:PORT ou https://IP:PORT")
    parser.add_argument("-l", "--list", help="Fichier texte contenant la liste des serveurs")
    
    args = parser.parse_args()

    if args.url:
        ps(args.url)
    
    if args.list:
        with open(args.list, "r") as file:
            servers = file.readlines()
        
        for server in servers:
            server = server.strip()
            if server: 
                ps(server)
