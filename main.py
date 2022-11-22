# Import Modules
from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import bleach
import requests

# Create a database object from SQLAlchemy
db = SQLAlchemy()

# Create app object from Flask Class
app = Flask(__name__)

# Connect to SQL Database. This can be customized and modified with a different Database if wanted
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"  # Configure the app object to link back to database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Turn modification tracking off on app object

# Configure the app object with a secret key. It can be whatever you want.
app.config['SECRET_KEY'] = 'THISISYOURSECRETKEYCOMEUPWITHSOMETHINGGREAT'

# Create object from CKEditor.
ckeditor = CKEditor(app)

# Specify that Bootstrap shall be utilized with app object
Bootstrap(app)

# Initiate the database.
db.init_app(app)


# Function to strip any invalid text from the form sheet
# Not needed but if a login page and users were added than this would be important to restrict SQL injection
def strip_invalid_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']
    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }
    # Bleach cleans the text of these attributes or tags prior to placing in database.
    cleaned = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    return cleaned


# Create task Class with input of the database object
class Tasks(db.Model):
    # Set columns of the SQL database
    id = db.Column(db.Integer, primary_key=True)  # ID column
    task_name = db.Column(db.String(250), unique=True, nullable=False)  # "Task Name" column
    task_due_date = db.Column(db.String(500), nullable=False)  # "Task Due Date" column.
    task_complete = db.Column(db.Boolean, nullable=False)  # "Task Complete" Column. 0 = False & 1 = True


# Create Class for adding new tasks to the database with WTForms
class TaskForm(FlaskForm):
    name = StringField("New Task?", validators=[DataRequired()])
    date = StringField("Due Date?")
    submit = SubmitField("Done")


# # Creates the database and table from the Class Task
# # Comment out after database is created.
# with app.app_context():
#     db.create_all()


# Set home page routing
@app.route("/")
def home():
    tasks = db.session.query(Tasks).all()  # Pull all task data into an object
    return render_template("index.html", all_tasks=tasks)  # Returns index.html page from templates folder


# Route to add new tasks
@app.route("/add", methods=["GET", "POST"])
def add_task():
    # Create form object from TaskForm Class
    form = TaskForm()
    # If statement for when the "Done" button on the form is clicked
    if form.validate_on_submit():
        new_task = Tasks(
            task_name=strip_invalid_html(form.name.data),
            task_due_date=strip_invalid_html(form.date.data),
            task_complete=False
        )
        db.session.add(new_task)  # Adds the new task to the database
        db.session.commit()  # Commits the changes to the database
        return redirect(url_for("home"))  # Redirect back to the homepage
    return render_template("new_task.html", form=form)  # Load the "new_task" page and the form template


# Create Route to mark task complete and delete from database
@app.route("/delete/<task_id>")
def delete_task(task_id):
    task_to_delete = Tasks.query.get(task_id)  # Create Task object and query for its task id from the database
    db.session.delete(task_to_delete)  # Delete the database entry from its id number
    db.session.commit()  # Commit the change to the database
    return redirect(url_for("home"))  # Redirect back to the home page


# Initiate the script and start a development server
if __name__ == "__main__":
    app.run(debug=True)
