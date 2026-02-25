import urllib.request
import json
req = urllib.request.Request("https://api.quran.com/api/v4/chapters?language=en", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())
surahs = [f"{c['id']}. {c['name_simple']} ({c['translated_name']['name']})" for c in data['chapters']]
with open("utils/surahs.py", "w", encoding="utf-8") as f:
    f.write("SURAHS = [\n")
    for s in surahs:
        f.write(f'    "{s}",\n')
    f.write("]\n")
