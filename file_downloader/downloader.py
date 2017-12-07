import urllib.request

urls = []
with open("filelinks") as f:
    urls = f.readlines()

# Download the file from `url` and save it locally under `file_name`:
for url in urls:
    with urllib.request.urlopen(url) as response, open(url.split('/')[-1], 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)
