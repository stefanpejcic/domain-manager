import os
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify, flash
import re

app = Flask(__name__)

# Define the base directory for user data
USER_DATA_DIR = "users"

# Regular expression pattern for a basic domain name validation
domain_regex = r'^(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+(?:[A-Za-z0-9-]{2,})$'

import secrets
app.secret_key = secrets.token_hex(16)



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

@app.route('/domains/<username>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def show_domains(username):
    if not user_exists(username):
        return "User not found", 404

    # Handle GET request to display domains
    if request.method == 'GET':
        user_data = load_user_data(username)
        domains = user_data.get("domains", [])
        domains_limit = user_data.get("domains_limit", 0)
        
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

        return render_template('domains.html', username=username, domains=domains, domains_limit=domains_limit)

    # Handle POST request to add a domain
    if request.method == 'POST':
        domain_name = request.form.get('domain_name')

        if not domain_name:
            flash(f"Domain name is required.", "error")
            return redirect(url_for('show_domains', username=username))
            
        # Validate the domain format using regex
        if not re.match(domain_regex, domain_name):
            flash(f"Domain {domain_name} is not added - invalid domain name format.", "error")
            return redirect(url_for('show_domains', username=username))
            
        # Load the user's existing data
        user_data = load_user_data(username)
        existing_domains = [domain['name'] for domain in user_data.get("domains", [])]
        domains_count = len(existing_domains)
        domains_limit = user_data.get("domains_limit", 0)

        if domains_count == domains_limit:
            flash(f"Domain {domain_name} is not added. Reached limit in number of domains ({domains_count}/{domains_limit}).", "error")
            return redirect(url_for('show_domains', username=username))
        
        if domain_name in existing_domains:
            flash(f"Domain {domain_name} already exists.", "error")
            return redirect(url_for('show_domains', username=username))

        # Add the new domain
        new_domain = {"name": domain_name, "status": "active"}
        user_data["domains"].append(new_domain)

        # Save the updated data back to the user's JSON file
        user_file_path = f"{USER_DATA_DIR}/{username}.json"
        with open(user_file_path, 'w') as user_file:
            json.dump(user_data, user_file, indent=4)
            

        flash(f"Domain {domain_name} ({domains_count}/{domains_limit}) has been added successfully.", "success")
        return redirect(url_for('show_domains', username=username))

    # Handle PUT request to import a list of domains
    if request.method == 'PUT':
        # Get the list of domains from the request body
        domain_list = request.data.decode('utf-8').strip()
    
        if not domain_list:
            flash(f"Domain list is required for import.", "error")
            return redirect(url_for('show_domains', username=username))
    
        # Split domains by lines or commas
        domain_names = re.split(r'[,\n]+', domain_list)
    
        # Validate and process domains
        user_data = load_user_data(username)
        existing_domains = {domain['name'] for domain in user_data.get("domains", [])}
        domains_count = len(existing_domains)
        domains_limit = user_data.get("domains_limit", 0)
    
        # Calculate the total number of domains including the new ones
        total_domains_count = domains_count + len(domain_names)
    
        if total_domains_count > domains_limit:
            flash(f"Cannot add more domains. Reached the limit of {domains_limit} domains ({domains_count}/{domains_limit}).", "error")
            return redirect(url_for('show_domains', username=username))
    
        new_domains = []
        skipped_domains = []
    
        for domain_name in domain_names:
            domain_name = domain_name.strip()
    
            if not domain_name:
                continue
    
            # Validate the domain format
            if not re.match(domain_regex, domain_name):
                skipped_domains.append({"domain": domain_name, "reason": "Invalid format"})
                continue
    
            # Check if the domain already exists
            if domain_name in existing_domains:
                skipped_domains.append({"domain": domain_name, "reason": "Already exists"})
                continue
    
            # Add the new domain
            new_domains.append({"name": domain_name, "status": "active"})
            existing_domains.add(domain_name)
    
        # Add new domains to the user's data
        user_data["domains"].extend(new_domains)
    
        # Save the updated data back to the user's JSON file
        user_file_path = f"{USER_DATA_DIR}/{username}.json"
        with open(user_file_path, 'w') as user_file:
            json.dump(user_data, user_file, indent=4)
    
        added_domains = ", ".join([domain["name"] for domain in new_domains])
        skipped_domains_str = ", ".join([f"{domain['domain']} ({domain['reason']})" for domain in skipped_domains])
    
        if new_domains:
            flash(f"Successfully imported domains: {added_domains}", "success")
        if skipped_domains_str:
            flash(f"Skipped existing domains: {skipped_domains_str}", "info")
    
        response_data = {
            "successDomains": added_domains,
            "skippedDomains": skipped_domains_str
        }
    
        return jsonify(response_data)

    
@app.route('/domains/<username>/<domain_name>', methods=['GET', 'DELETE'])
def show_domain_detail(username, domain_name):
    if not user_exists(username):
        return "User not found", 404

    if request.method == 'GET':
        
        domain = Domain(domain_name)  # Create a Domain object
    
        user_data = load_user_data(username)
        domains = user_data.get("domains", [])
    
        if not domains:
            flash(f"No domains yet", "info")
            return redirect(url_for('show_domains', username=username))
    
        
        # Check if the domain_name exists in the list of domain names
        if domain_name not in [domain['name'] for domain in domains]:
            flash(f"Domain { domain_name } not found", "error")
            return redirect(url_for('show_domains', username=username))
    
        response_file_path = f'scripts/responses/{domain_name}'
        ssl_info_file_path = f'scripts/ssl_info/{domain_name}'
        domain.response_last_row = get_last_row(response_file_path)
        domain.ssl_info_last_row = get_last_row(ssl_info_file_path)
    
        whois_dir_for_domain = f'scripts/whois_results/{domain_name}'
        whois_details = parse_whois_data(whois_dir_for_domain)
        return render_template('domains_single.html', username=username, domain=domain, whois_details=whois_details)

    # Handle DELETE request to delete a domain
    if request.method == 'DELETE':

        # Get the domain name to delete from form data
        domain_name = request.form.get('domain_name')

        if not domain_name:
            flash(f"Domain name is required.", "error")
            return redirect(url_for('show_domains', username=username))
            
        # Load the user's existing data
        user_data = load_user_data(username)

        # Find the domain and remove it
        domains = user_data.get("domains", [])
        domain_to_delete = next((domain for domain in domains if domain['name'] == domain_name), None)

        if not domain_to_delete:
            flash(f"Domain not found.", "error")
            return redirect(url_for('show_domains', username=username))
        # Remove the domain
        user_data["domains"] = [domain for domain in domains if domain['name'] != domain_name]

        # Save the updated data back to the user's JSON file
        user_file_path = f"{USER_DATA_DIR}/{username}.json"
        with open(user_file_path, 'w') as user_file:
            json.dump(user_data, user_file, indent=4)

        flash(f"Domain {domain_name} deleted successfully.", "success")
        return redirect(url_for('show_domains', username=username))

# Debug mode and running the app
if __name__ == "__main__":
    app.run(debug=True)
