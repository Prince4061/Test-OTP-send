from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
STATE_FILE = 'state.json'

# Function to read the current state
def get_state():
    if not os.path.exists(STATE_FILE):
        return {"active_group": "group_1"}
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"active_group": "group_1"}

# Function to write the current state
def set_state(group):
    with open(STATE_FILE, 'w') as f:
        json.dump({"active_group": group}, f)

# GUI web interface
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        if data and 'group' in data and data['group'] in ['group_1', 'group_2', 'group_3']:
            set_state(data['group'])
            return jsonify({"success": True, "active_group": data['group']})
        return jsonify({"error": "Invalid input"}), 400
    
    state = get_state()
    return render_template('index.html', active_group=state['active_group'])

# API Endpoint for n8n to check the status ALWAYS
@app.route('/api/active-group', methods=['GET'])
def api_active_group():
    return jsonify(get_state())

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
