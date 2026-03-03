import glob
import re

files = glob.glob('h:/cater-main/backend/api/*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace socketio.emit( with socketio.start_background_task(socketio.emit,
    # Negative lookbehind to prevent double replacement
    new_content = re.sub(r'(?<!start_background_task\()socketio\.emit\(', r'socketio.start_background_task(socketio.emit, ', content)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file}")
