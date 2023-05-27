##!/bin/python3 
# remove the first # in line above if running on *nix 
# transcription of a found powershell script to call API(s) to update cloudflare dynamic dns
import requests, os
from dotenv import load_dotenv

load_dotenv()

email = os.environ["CF_EMAIL"]
token = os.environ["CF_TOKEN"]
domain = os.environ["CF_DOMAIN"]
record = os.environ["CF_RECORD"]

# build request headers once. these headers will be used throughout:
headers = {
    "X-Auth-Email": email,
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

# region token test
# verifies API key validity
# if not, exit


def tokentest(token):
    """creating function for to test token validity"""
    uri = "https://api.cloudflare.com/client/v4/user/tokens/verify"
    r = requests.get(url=uri, headers=headers)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(f"There was a problem. Status {r.status_code}")
        exit()
    print(f"API Token validation success.")
    return


tokentest(token)

# endregion

# region get zone ID
# retrieves domain's zone ID based on name.
# if ID not found, quit


def zoneID(domain):
    """validate zone ID"""
    uri = f"https://api.cloudflare.com/client/v4/zones?={domain}"
    r = requests.get(url=uri, headers=headers)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(f"Problem: {r.status_code}")
        exit()
    result = r.json()["result"][0]["id"]
    print(f"Domain zone found. Domain: {domain}\nZone: {result}")
    return result


zone_ID = zoneID(domain)

# endregion


# region get DNS record
# retrieve existing DNS record details from cloudflare
def getDNS(zoneID):
    """get existing DNS record"""
    uri = (
        f"https://api.cloudflare.com/client/v4/zones/{zoneID}/dns_records?name={record}"
    )
    r = requests.get(url=uri, headers=headers)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(f"There was an issue! {r.status_code}")
        exit()
    old_ip = r.json()["result"][0]["content"]
    record_type = r.json()["result"][0]["type"]
    record_id = r.json()["result"][0]["id"]
    record_ttl = r.json()["result"][0]["ttl"]
    record_proxied = r.json()["result"][0]["proxied"]
    print(f"DNS Record: {record}\nType: {record_type}\nIP: {old_ip}")
    other_values = [old_ip, record_type, record_id, record_ttl, record_proxied]
    return other_values


information = getDNS(zone_ID)
old_ip = information[0]
record_type = information[1]
record_id = information[2]
record_ttl = information[3]
record_proxied = information[4]
# endregion


# region get current public IP address
def getCurrentIP(information):
    """get current public IP address"""
    uri = "https://v4.ident.me"
    r = requests.get(url=uri)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(f"ERROR. {r.status_code}")
    currentIP = r.content.decode()
    print(f"Old IP: {old_ip}\nNew IP: {currentIP}")
    return currentIP


currentIP = getCurrentIP(information)

# endregion


# region update DNS record
def checkRec(currentIP, old_ip):
    """compare current IP with current record, update if different"""
    if currentIP == old_ip:
        print("Matches. Nothing to do.")
        quit()
    elif currentIP != old_ip:
        uri = f"https://api.cloudflare.com/client/v4/zones/{zone_ID}/dns_records/{record_id}"
        params = {
            "type": record_type,
            "name": record,
            "content": currentIP,
            "ttl": record_ttl,
            "proxied": record_proxied,
        }
        r = requests.put(url=uri, headers=headers, json=params)
        try:
            r.raise_for_status()
        except:
            print("Update call failed!")
            quit()
        print("DNS record update successful.")
    else:
        print("Something is totally [REDACTED] UP if you see this.")
        quit()
    return


checkRec(currentIP, old_ip)
# endregion
