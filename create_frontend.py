import os

BASE = r"C:/Users/cobra/grants-assistant/frontend"

def w(rel, content):
    full = os.path.join(BASE, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK: {rel}')

