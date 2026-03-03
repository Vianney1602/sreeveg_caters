import requests, re
r = requests.get('https://info.hotelshanmugabhavaan.com/')
js_files = re.findall(r'src=\"(/static/js/main\.[^\"]+\.js)\"', r.text)
if js_files:
    js_url = 'https://info.hotelshanmugabhavaan.com' + js_files[0]
    js_content = requests.get(js_url).text
    idx1 = js_content.find('127.0.0.1') 
    idx2 = js_content.find('localhost')
    if idx1 != -1:
        print('FOUND 127.0.0.1 IN JS:', js_content[max(0, idx1-50):idx1+50])
    if idx2 != -1:
        print('FOUND LOCALHOST IN JS:', js_content[max(0, idx2-50):idx2+50])
    if idx1 == -1 and idx2 == -1:
        print('No localhost or 127.0.0.1 found in js bundle.')
else:
    print('No js files found in index.html')
