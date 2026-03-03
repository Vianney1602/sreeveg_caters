import requests, re
r = requests.get('https://hotelshanmugabhavaan.com/')
js_files = re.findall(r'src=\"(/static/js/main\.[^\"]+\.js)\"', r.text)
if js_files:
    js_url = 'https://hotelshanmugabhavaan.com' + js_files[0]
    js_content = requests.get(js_url).text
    idx = js_content.find('application/json')
    if idx != -1:
        # Get surrounding text
        print('JS context around JSON:', js_content[max(0, idx-50):idx+100])
    else:
        print('Could not find application/json globally in bundle.')
else:
    print('No JS files found.')
