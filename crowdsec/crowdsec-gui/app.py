from flask import Flask, render_template, request, jsonify
import subprocess
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_banned_ips():
    """Execute cscli to get currently banned IPs in JSON format."""
    try:
        # Run cscli command
        result = subprocess.run(
            ['sudo', 'cscli', 'decisions', 'list', '-o', 'json'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            logging.error(f"Error running cscli: {result.stderr}")
            return []
            
        output = result.stdout.strip()
        if not output:
             return []
             
        decisions_data = json.loads(output)
        
        # Parse the JSON. cscli returns a list of active decisions.
        banned_list = []
        for item in decisions_data:
             # Depending on cscli version, JSON structure might slightly vary. 
             # Usually it's a list containing dicts with "decisions" inside them.
             decisions = item.get("decisions") or []
             for decision in decisions:
                 if decision.get("type") == "ban":
                     banned_list.append({
                         "id": decision.get("id"),
                         "ip": decision.get("value"),
                         "reason": decision.get("scenario"),
                         "duration": decision.get("duration"),
                     })
                     
        return banned_list
        
    except FileNotFoundError:
        logging.error("cscli not found. Ensure crowdsec is installed and in PATH.")
        # Return mock data for local testing when Crowdsec is not present
        return [
            {"id": 1, "ip": "192.168.1.55", "reason": "open-appsec/malicious-request", "duration": "4h"},
            {"id": 2, "ip": "10.0.0.21", "reason": "crowdsec/http-probing", "duration": "2h30m"}
        ]
    except Exception as e:
        logging.error(f"Failed to parse cscli output: {e}")
        return []

@app.route('/')
def index():
    """Render the dashboard."""
    banned_ips = get_banned_ips()
    return render_template('index.html', banned_ips=banned_ips)

@app.route('/unban', methods=['POST'])
def unban_ip():
    """Unban an IP using cscli."""
    data = request.get_json()
    ip_to_unban = data.get('ip')
    
    if not ip_to_unban:
        return jsonify({"success": False, "error": "IP address is required"}), 400
        
    try:
        # sudo cscli decisions delete -i <ip>
        result = subprocess.run(
            ['sudo', 'cscli', 'decisions', 'delete', '-i', str(ip_to_unban)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logging.info(f"Successfully unbanned IP: {ip_to_unban}")
            return jsonify({"success": True, "message": f"{ip_to_unban} has been unbanned."})
        else:
            logging.error(f"Failed to unban {ip_to_unban}: {result.stderr}")
            return jsonify({"success": False, "error": result.stderr}), 500
            
    except FileNotFoundError:
         # Mock success for local testing
         return jsonify({"success": True, "message": f"{ip_to_unban} has been unbanned. (Mock)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
