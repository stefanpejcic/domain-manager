from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

# Create routes
@app.route('/domains/<username>')
def show_domains(username):
    user = User.query.filter_by(username=username).first()

    if user:
        domains = Domain.query.filter_by(user_id=user.id).all()
        return render_template('domains.html', user=user, domains=domains)
    else:
        return "User not found"


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
