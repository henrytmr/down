import requests
import json
import urllib
from random import randint
from draft_to_calendar import main as convert
import asyncio
import nest_asyncio

def upload_token(filename, token, host, ws, upec):
	s = requests.session()
	data = {
		"token": token,
		"itemid": "0",
		"filearea": "draft"
	}
	files = {
		"file": (filename, open(filename, "rb"), "application/x-subrip"),
	}
	resp = s.post(f"{host}/webservice/upload.php", data=data, files=files, verify=False)
	resp = json.loads(resp.text)[0]
	contextid, itemid, filename = resp["contextid"], resp["itemid"], resp["filename"]
	url = f"{host}/webservice/draftfile.php/{contextid}/user/draft/{itemid}/{urllib.parse.quote(filename)}?token={token}"
	if ws == False:
		url = url.replace("/webservice", "")
	if upec == True:
		url = url.replace("/webservice", "").split("?token")[0]
		nest_asyncio.apply()
		url = asyncio.run(convert(url))
		url = str(url).replace("pluginfile.php", "webservice/pluginfile.php").replace("['", "").replace("']", "") + "?token=" + token
	return url

#print(upload_token("requirements.txt", "3e7e0d514c6ea7c7040217a37dcfcc70", "https://eva.uo.edu.cu"))
