from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://manager:ds732bfsd@localhost/domains'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'  # explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    # Add other user-related fields as needed

    def __repr__(self):
        return f"<User {self.username}>"



# Define the Domains model
class Domains(db.Model):
    __tablename__ = 'domains' 
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    registrar_id = db.Column(db.Integer, db.ForeignKey('registrars.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20))
    ssl_status = db.Column(db.String(20))
    http_response = db.Column(db.Integer)
    note = db.Column(db.Text)



@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/domains/<username>')
def show_domains(username):
    user = User.query.filter_by(username=username).first()

    if user:
        domains = Domains.query.filter_by(user_id=user.id).all()

        for domain in domains:
            # Construct file paths for each domain
            response_file_path = f'responses/{domain.domain}'
            ssl_info_file_path = f'ssl_info/{domain.domain}'
            whois_results_file_path = f'whois_results/{domain.domain}'

            # Check if files exist and get the last row from each
            response_last_row = get_last_row(response_file_path)
            ssl_info_last_row = get_last_row(ssl_info_file_path)
            whois_results_last_row = parse_whois_data(whois_results_file_path)

            # Update domain object with file information
            domain.response_last_row = response_last_row
            domain.ssl_info_last_row = ssl_info_last_row
            domain.whois_results_last_row = whois_results_last_row

        return render_template('domains.html', user=user, domains=domains)
    else:
        return "User not found"

# Helper function to get the last row from a file
def get_last_row(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                return lines[-1]
    return None

# Helper function to get all lines from a file
def get_all_rows(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines  # Return all lines
    return []



# helper for single doamin page
class Domain:
    def __init__(self, name):
        self.name = name
        self.response_last_row = None
        self.ssl_info_last_row = None
        self.whois_results_last_row = None

import os

def parse_whois_data(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return {}
    
    # Get all files in the directory
    all_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path)]
    
    # Filter out directories, leaving only files
    all_files = [f for f in all_files if os.path.isfile(f)]
    
    # Find the newest file based on modification time
    newest_file = max(all_files, key=os.path.getmtime)
    
    # Initialize 'details' if not already done:
    details = {'dns': []}
    
    # Assuming 'newest_file' is the path to the file you want to read.
    with open(newest_file, 'r') as file:
        # Read the entire file content and split by lines
        content = file.read()
        lines = content.split('\n')
        
        for line in lines:
            # Convert the line to lowercase for case-insensitive comparison
            line_lower = line.lower()
            
            if 'domain status' in line_lower:
                # Keep the entire line content from the match till the end of the line
                details['status'] = line[line_lower.find('domain status'):].strip()
            elif 'dnssec' in line_lower:
                details['dnssec'] = line[line_lower.find('dnssec'):].strip()
            elif 'registrar:' in line_lower:
                details['registrar'] = line[line_lower.find('registrar'):].strip()


            if 'expiration date' in line_lower:
                details['expiration'] = line[line_lower.find('expiration date'):].strip()
                #fix for .club domains
            elif 'expiry date' in line_lower:
                details['expiration'] = line[line_lower.find('expiry date'):].strip()
            
            # for ns we need to conver both cases when whois returns "Name Servers" or just "DNS"
            # check for 'name server' in the line
            if 'name server' in line_lower:
                dns_line = line[line_lower.find('name server'):].strip()
                # Assuming that each 'Name Server' entry is on a separate line
                if dns_line not in details['dns']:
                    details['dns'].append(dns_line)
            # If 'name server' is not found, then look for 'dns:'
            elif 'dns:' in line_lower:
                dns_line = line[line_lower.find('dns:'):].strip()
                # Assuming that each 'dns:' entry is on a separate line
                if dns_line not in details['dns']:
                    details['dns'].append(dns_line)


    
    return details
    




@app.route('/domains/<username>/<domain_name>')
def show_domain_detail(username, domain_name):
    domain = Domain(domain_name)  # Create a Domain object

    # Construct file paths for each domain
    response_file_path = f'responses/{domain_name}'
    ssl_info_file_path = f'ssl_info/{domain_name}'

    # Check if files exist and get the last row from each
    domain.response_last_row = get_last_row(response_file_path)
    domain.ssl_info_last_row = get_last_row(ssl_info_file_path)
    
    #domain.whois_results_last_row = get_all_rows(whois_results_file_path)
    whois_dir_for_domain = f'whois_results/{domain_name}'
    whois_details = parse_whois_data(whois_dir_for_domain)
    return render_template('domains_single.html', user=username, domain=domain, whois_details=whois_details)



#NOT READY!
@app.route('/domains/<username>/<domain>/info')
def show_domain_detail_api(username, domain):
    user = User.query.filter_by(username=username).first_or_404(description='User not found')
    domain = Domain.query.filter_by(user_id=user.id, domain=domain).first_or_404(description='Domain not found')

    # Construct file paths for the domain
    response_file_path = f'responses/{domain.domain}'
    ssl_info_file_path = f'ssl_info/{domain.domain}'
    whois_results_file_path = f'whois_results/{domain.domain}'

    # Check if files exist and get the last row from each
    response_all_row = get_all_rows(response_file_path)
    ssl_info_all_row = get_all_rows(ssl_info_file_path)
    whois_results_all_row = get_all_rows(whois_results_file_path)

    # Update domain object with file information
    domain.response_all_row = response_all_row
    domain.ssl_info_all_row = ssl_info_all_row
    domain.whois_results_all_row = whois_results_all_row

    return render_template('domains_single.html', user=user, domain=domain)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
