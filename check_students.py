import os
os.environ["API_URL"] = "https://rehapp-backend-production.up.railway.app"

import sys
sys.path.insert(0, ".")
import api_client as api

students = api.get_students()
print(f"Toplam öğrenci: {len(students)}")
for s in students:
    name = s['name'].lower()
    if 'ismail' in name or 'serdar' in name or 'kerem' in name:
        diags = [d['name'] for d in s.get('diagnoses', [])]
        mods  = [m['name'] for m in s.get('modules', [])]
        print(f"\n{s['name']}")
        print(f"  dob: {s.get('dob')}")
        print(f"  tanı: {diags}")
        print(f"  modül: {mods}")
