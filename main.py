from flask import Flask, request, Response
import json
import base64
import socket
import yaml
import os
from flask import render_template_string

app = Flask(__name__)

def decode_vmess(vmess):
    try:
        if vmess.startswith('vmess://'):
            vmess = vmess[8:]
        decoded = base64.b64decode(vmess).decode('utf-8')
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"Invalid VMess format: {str(e)}"}

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        return {"error": f"Failed to resolve domain: {str(e)}"}

def read_template(file):
    try:
        with open(file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {"error": f"Failed to read YAML template: {str(e)}"}

def update_conf(decoded, yaml_file):
    if "error" in decoded:
        return decoded
    
    config_name = decoded.get('ps', 'Unnamed Proxy')
    user_id = decoded.get('id', None)
    server = decoded.get('add', None)
    port = decoded.get('port', None)
    v_path = decoded.get('path', '/')
    
    server_ip = get_ip(server)
    if isinstance(server_ip, dict):  # Error handling
        return server_ip
    
    for proxy in yaml_file.get('proxies', []):
        proxy['name'] = proxy.get('name') + ' - ' + config_name.replace(' ', '')
        proxy['uuid'] = user_id
        proxy['server'] = server_ip
        proxy['port'] = port
        proxy.setdefault('ws-opts', {})['path'] = v_path
    
    for group in yaml_file.get('proxy-groups', []):
        
        for i in range(1, len(group['proxies'])):
            group['proxies'][i] = group['proxies'][i] + ' - ' + config_name
    
    return yaml_file

@app.route('/generate_yaml', methods=['GET'])
def generate_yaml():
    encoded_vmess = request.args.get('vmess')
    if not encoded_vmess:
        return {"error": "No VMess config provided"}, 400
    
    decoded = decode_vmess(encoded_vmess)
    if "error" in decoded:
        return decoded, 400
    
    yaml_file = read_template('config.yaml')
    if "error" in yaml_file:
        return yaml_file, 500
    
    data = update_conf(decoded, yaml_file)
    if "error" in data:
        return data, 500
    
    return Response(yaml.dump(data), mimetype='text/yaml')

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
    <html>
    <head>
        <title>Clash Config Generator</title>
    </head>
    <body>
        <h1>Clash Config Generator</h1>
        <form action="/generate_yaml" method="get">
            <label for="vmess">VMess:</label>
            <input type="text" id="vmess" name="vmess" required>
            <button type="submit">Generate YAML</button>
        </form>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

# Dockerization support
# Create a Dockerfile with the following content:
# FROM python:3.9
# WORKDIR /app
# COPY . /app
# RUN pip install flask pyyaml
# CMD ["python", "app.py"]
