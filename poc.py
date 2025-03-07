import requests
import argparse
import json
import re
from urllib.parse import urlparse

def ed(response_text):
    try:
        match = re.search(r"var environment = ({.*?});", response_text, re.DOTALL)

        if match:
            data = match.group(1)
            
            environment_data = json.loads(data)
            
            require_host = environment_data.get("page", {}).get("require_host", None)
            hostname = environment_data.get("hostname", None)
            os_release = environment_data.get("os-release", None)

            print(f"[+] Require Host: {require_host}")
            print(f"[+] Hostname: {hostname}")

            if os_release:
                print(f"[+] Sysinfo:")
                for key, value in os_release.items():
                    print(f"  {key}: {value}")
            else:
                print("[!] Sysinfo: Not available")
        else:
            print("[!] Couldn't find 'var environment' in the response text.")
    except json.JSONDecodeError as e:
        print(f"[!] Error decoding JSON: {e}")
    except Exception as e:
        print("[!] Error while extracting data:", e)

def sr(url, host):
    headers = {
        "Host": host,
        "Cookie": "cockpit=deleted",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Sec-Ch-Ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Accept": "*/*",
        "Sec-Gpc": "1",
        "Accept-Language": "fr-FR,fr;q=0.5",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        print("[+] STATUS:", response.status_code)

        ed(response.text)

    except requests.RequestException as e:
        print("[!] Request failed:", e)

def puf(file_path):
    try:
        with open(file_path, "r") as file:
            urls = file.readlines()
            
        for url in urls:
            url = url.strip()
            if url:
                print(f"\n[+] Scan => {url}")
                parsed_url = urlparse(url)
                if not parsed_url.scheme:
                    print("[!] Invalid URL format. Make sure it starts with http:// or https://")
                else:
                    host = parsed_url.netloc
                    sr(url, host)
    except FileNotFoundError:
        print(f"[!] File '{file_path}' not found.")
    except Exception as e:
        print(f"[!] Error reading file '{file_path}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send HTTP GET request to a specified URL or from a list of URLs in a file")
    parser.add_argument("-u", "--url", type=str, help="Target URL in the format http://IP:PORT")
    parser.add_argument("-l", "--list", type=str, help="File containing a list of URLs to test (one per line)")

    args = parser.parse_args()

    if args.url:
        parsed_url = urlparse(args.url)
        if not parsed_url.scheme:
            print("[!] Invalid URL format. Make sure it starts with http:// or https://")
        else:
            host = parsed_url.netloc
            sr(args.url, host)
    
    elif args.list:
        puf(args.list)
    
    else:
        print("[!] Please provide either a single URL with -u or a file with -l.")
