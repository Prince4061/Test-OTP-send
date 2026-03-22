from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
STATE_FILE = 'state.json'

# Function to read the current state
def get_state():
    if not os.path.exists(STATE_FILE):
        return {"active_group": "group_1", "system_active": True}
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            # Ensure system_active key exists for old state files
            if "system_active" not in state:
                state["system_active"] = True
            return state
    except:
        return {"active_group": "group_1", "system_active": True}

# Function to write the current state
def set_state(data):
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f)

# GUI web interface
@app.route('/', methods=['GET', 'POST'])
def index():
    state = get_state()
    if request.method == 'POST':
        data = request.json
        if data and 'group' in data and data['group'] in ['group_1', 'group_2', 'group_3', 'group_4', 'group_5']:
            state['active_group'] = data['group']
            set_state(state)
            return jsonify({"success": True, "active_group": state['active_group']})
        return jsonify({"error": "Invalid input"}), 400

    return render_template('index.html',
                           active_group=state['active_group'],
                           system_active=state['system_active'])

# Toggle system ON/OFF
@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.json
    if data is None or 'active' not in data:
        return jsonify({"error": "Invalid input"}), 400
    state = get_state()
    state['system_active'] = bool(data['active'])
    set_state(state)
    return jsonify({"success": True, "system_active": state['system_active']})

# API Endpoint for n8n to check the status
@app.route('/api/active-group', methods=['GET'])
def api_active_group():
    state = get_state()
    # If system is OFF, return "none" so n8n's Route by Group doesn't match anything
    if not state.get('system_active', True):
        return jsonify({"active_group": "none", "system_active": False})
    return jsonify({"active_group": state['active_group'], "system_active": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
