import glob
import re

files = glob.glob('h:/cater-main/backend/api/*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace socketio.emit with emit_with_namespace inside start_background_task
    new_content = content.replace("socketio.start_background_task(socketio.emit, ", "socketio.start_background_task(emit_with_namespace, ")
    
    # 2. Add emit_with_namespace to imports if changed
    if new_content != content:
        if 'emit_with_namespace' not in new_content:
            new_content = re.sub(r'from extensions import (.*)socketio(.*)', r'from extensions import \1socketio, emit_with_namespace\2', new_content)
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched wrapper in {file}")
