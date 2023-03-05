#!/usr/bin/env python3

import sys
import re
import time
import requests
import concurrent.futures
from bs4 import BeautifulSoup

def crtdump(domain):
    url_pattern = re.compile(r'(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?')
    try:
        response = requests.get(f'https://crt.sh/?q={domain}')
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()
        for element in soup(text=url_pattern):
            url_match = re.search(url_pattern, element)
            if url_match:
                url = url_match.group()
                if url.endswith(f'.{domain}') or url.endswith(f'.{domain}.'):
                    urls.add(url)
        return urls
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        sys.exit(1)

def show_usage():
    print("Usage: ./SubHound [-h] domain\n")
    print("positional arguments:")
    print("  domain        domain to search for subdomains\n")
    print("optional arguments:")
    print("  -h, --help    show this help message and exit\n")

def check_status(url):
    if not url.startswith('https'):
        url = 'https://' + url

    try:
        response = requests.head(url, allow_redirects=False, timeout=10)
        status_code = response.status_code
        print(f"[{status_code}] - {url}")
        return f"[{status_code}] - {url}\n"
    except requests.exceptions.RequestException as e:
        pass

def main():
    print("SubHound is a subdomain enumeration tool via crt.sh certs database.\n")
    print("Querying the database...\n")
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        show_usage()
        sys.exit(0)

    domain = sys.argv[1]
    urls = crtdump(domain)
    if len(urls) > 0:
        print("Subdomains found!\n")
        time.sleep(1)
    else:
        print("No subdomains found :(")
        sys.exit(1)

    for url in urls:
        print(url)

    print("\nChecking for status code...\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_status, url) for url in urls]

    with open(f"{domain}.txt", "w") as file:
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                file.write(result)

    print("\nDone!")
    sys.exit(0)
    
if __name__ == '__main__':
    main()