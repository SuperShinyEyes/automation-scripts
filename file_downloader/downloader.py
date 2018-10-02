import urllib.request

urls = []
with open("filelinks") as f:
    urls = f.readlines()



# Download the file from `url` and save it locally under `file_name`:
for url in urls[19:]:
	file_name = "downloads/" + url.split('filename=')[-1]
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		data = response.read() # a `bytes` object
		out_file.write(data)
