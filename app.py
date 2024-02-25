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
class Domain(db.Model):
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



@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/domains/<username>')
def show_domains(username):
    user = User.query.filter_by(username=username).first()

    if user:
        domains = Domain.query.filter_by(user_id=user.id).all()

        for domain in domains:
            # Construct file paths for each domain
            response_file_path = f'responses/{domain.domain}'
            ssl_info_file_path = f'ssl_info/{domain.domain}'
            whois_results_file_path = f'whois_results/{domain.domain}'

            # Check if files exist and get the last row from each
            response_last_row = get_last_row(response_file_path)
            ssl_info_last_row = get_last_row(ssl_info_file_path)
            whois_results_last_row = get_last_row(whois_results_file_path)

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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
