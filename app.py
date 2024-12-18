import os
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify

app = Flask(__name__)

# Define the base directory for user data
USER_DATA_DIR = "users"

# Helper function to load user data
def load_user_data(username):
    file_path = os.path.join(USER_DATA_DIR, f"{username}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return None

# Helper function to save user data
def save_user_data(username, data):
    file_path = os.path.join(USER_DATA_DIR, f"{username}.json")
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Helper function to check if a user exists
def user_exists(username):
    return os.path.exists(os.path.join(USER_DATA_DIR, f"{username}.json"))

# helper for single doamin page
class Domain:
    def __init__(self, name):
        self.name = name
        self.response_last_row = None
        self.ssl_info_last_row = None
        self.whois_results_last_row = None




# File Handling Helpers
def get_last_row(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                return lines[-1].strip()
    return None

def parse_whois_data(directory_path):
    # Similar logic as before, but tailored for a directory-based system
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return {}
    newest_file = max(
        (os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))),
        key=os.path.getmtime,
        default=None
    )
    if not newest_file:
        return {}
    details = {'dns': []}
    with open(newest_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line_lower = line.lower()
            if "domain status" in line_lower:
                details["status"] = line.split(":", 1)[-1].strip()
            elif "dnssec" in line_lower:
                details["dnssec"] = line.split(":", 1)[-1].strip()
            elif "registrar" in line_lower:
                details["registrar"] = line.split(":", 1)[-1].strip()
            elif "expiration date" in line_lower or "expiry date" in line_lower:
                details["expiration"] = line.split(":", 1)[-1].strip()
            elif "name server" in line_lower or "dns:" in line_lower:
                dns = line.split(":", 1)[-1].strip()
                if dns not in details["dns"]:
                    details["dns"].append(dns)
    return details









# Routes
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/domains/<username>', methods=['GET', 'POST'])
def show_domains(username):
    # Handle GET request to display domains
    if request.method == 'GET':
        if not user_exists(username):
            return "User not found", 404

        user_data = load_user_data(username)
        domains = user_data.get("domains", [])
        
        # Fetch the last row of relevant files for each domain
        for domain in domains:
            response_file_path = f"scripts/responses/{domain['name']}"
            ssl_info_file_path = f"scripts/ssl_info/{domain['name']}"
            whois_results_file_path = f"scripts/whois_results/{domain['name']}"

            response_last_row = get_last_row(response_file_path)
            ssl_info_last_row = get_last_row(ssl_info_file_path)
            whois_results_last_row = parse_whois_data(whois_results_file_path)

            domain['response_last_row'] = response_last_row
            domain['ssl_info_last_row'] = ssl_info_last_row
            domain['whois_results_last_row'] = whois_results_last_row

        return render_template('domains.html', user=username, domains=domains)

    # Handle POST request to add a domain
    if request.method == 'POST':
        if not user_exists(username):
            return "User not found", 404

        # Get the domain name from the form data
        domain_name = request.form.get('domain_name')

        if not domain_name:
            return "Domain name is required", 400

        # Load the user's existing data
        user_data = load_user_data(username)

        # Check if the domain already exists
        existing_domains = [domain['name'] for domain in user_data.get("domains", [])]
        if domain_name in existing_domains:
            return "Domain already exists", 400

        # Add the new domain
        new_domain = {"name": domain_name, "status": "active"}
        user_data["domains"].append(new_domain)

        # Save the updated data back to the user's JSON file
        user_file_path = f"{USER_DATA_DIR}/{username}.json"
        with open(user_file_path, 'w') as user_file:
            json.dump(user_data, user_file, indent=4)

        return redirect(url_for('show_domains', username=username))

@app.route('/domains/<username>/<domain_name>')
def show_domain_detail(username, domain_name):
    if not user_exists(username):
        return "User not found", 404

    domain = Domain(domain_name)  # Create a Domain object
    response_file_path = f'scripts/responses/{domain_name}'
    ssl_info_file_path = f'scripts/ssl_info/{domain_name}'
    domain.response_last_row = get_last_row(response_file_path)
    domain.ssl_info_last_row = get_last_row(ssl_info_file_path)

    whois_dir_for_domain = f'scripts/whois_results/{domain_name}'
    whois_details = parse_whois_data(whois_dir_for_domain)
    return render_template('domains_single.html', user=username, domain=domain, whois_details=whois_details)


# Debug mode and running the app
if __name__ == "__main__":
    app.run(debug=True)
