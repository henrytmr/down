import requests
import time
import urllib

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_url_file_name(url, req):
    try:
        if "Content-Disposition" in req.headers.keys():
                name = str(req.headers["Content-Disposition"]).replace('attachment; ','')
                name = name.replace('filename=','').replace('"','')
                return name
        else:
            urlfix = urllib.parse.unquote(url,encoding='utf-8', errors='replace')
            tokens = str(urlfix).split('/');
            return tokens[len(tokens)-1]
    except:
        urlfix = urllib.parse.unquote(url,encoding='utf-8', errors='replace')
        tokens = str(urlfix).split('/');
        return tokens[len(tokens)-1]

def download_file(url):
    req = requests.get(url)
    if req.status_code == 200:
        file_size = req_file_size(req)
        file_name = get_url_file_name(url, req)
        file_wr = open(file_name, 'wb')
        chunk_por = 0
        chunkrandom = 100
        total = file_size
        time_start = time.time()
        time_total = 0
        size_per_second = 0
        clock_start = time.time()
        for chunk in req.iter_content(chunk_size = 1024):
                #if stoping:break
                chunk_por += len(chunk)
                size_per_second+=len(chunk);
                tcurrent = time.time() - time_start
                time_total += tcurrent
                time_start = time.time()
                if time_total>=1:
                    clock_time = (total - chunk_por) / (size_per_second)
                    time_total = 0
                    size_per_second = 0
                file_wr.write(chunk)
        file_wr.close()
    return file_name