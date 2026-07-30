#!/usr/bin/env python3
"""Test the Django login flow for vendedor@merkatolima.com"""
import requests
import re

session = requests.Session()

# Step 1: GET login page
r = session.get('http://localhost:8001/login/')
print('GET /login/ status:', r.status_code)

# Extract CSRF token
m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', r.text)
csrf = m.group(1) if m else ''
print('CSRF token found:', bool(csrf), csrf[:20] if csrf else '')

# Step 2: POST login
data = {
    'email': 'vendedor@merkatolima.com',
    'password': 'Vendedor123',
    'csrfmiddlewaretoken': csrf
}
r2 = session.post('http://localhost:8001/login/', data=data, 
                  headers={'Referer': 'http://localhost:8001/login/'},
                  allow_redirects=False)
print('POST /login/ status:', r2.status_code)
print('Location:', r2.headers.get('Location', 'none'))

if r2.status_code == 200:
    # Check for error messages in response
    if 'Credenciales' in r2.text or 'error' in r2.text.lower():
        # Find messages
        msgs = re.findall(r'<[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</[^>]+>', r2.text, re.DOTALL)
        for msg in msgs:
            print('Message:', msg.strip()[:200])
    print('Response snippet:', r2.text[1000:2000])
