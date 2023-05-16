from flask import Flask, session, render_template, redirect, url_for, request, flash,
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from db.models import *
from datetime import datetime
from werkzeug.utils import secure_filename
import os 

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "SSRL"

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def alllowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def login():
    if "user" in session:
        return redirect(url_for('home'))
    
    else:
        return render_template('forms/login.html', greetings="greetings")
    
@app.route('/home/me')
def home():
    if "user" in session:
        user_id = session["user_id"]
        user_profile = User_db.get_user_by_id(user_id)
        return render_template("user_dashboard.html", user_profile=user_profile)
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
        
@app.route('/user/authenticate')
def authenticate_user():
    user_id = request.form.get("user_id")
    pwd = request.form.get("pwd")
    user_profile = User_db.get_user_by_id(user_id)
    authenticated = check_password_hash(user_profile["password"], pwd)
    
    if user_profile:
        if authenticated==True:
            session["user_id"] = user_id
            session["user_role"] = user_profile["role"]
            session["stack"] = user_profile["stack"]
            fullname = user_profile["fullname"]
            
            flash (f"Welcome! {fullname}")
            return redirect(url_for('home'), user_profile=user_profile)
        else:
            flash("Invalid password")
            return redirect(url_for("login"))
        
    else:
        flash("Invalid log in ID")
        return redirect(url_for('login'))

    
@app.route('Admin/create/user', methods=["GET", "POST"])
def create_user():
    user_role = session["role"]
    
    if "user" in session:
        if user_role == "Admin":
            if request.method == "POST":
                firstname = request.form.get("firstname")
                surname = request.form.get("surname")
                pwd = generate_password_hash(generate.password())
                _id = generate.user_id(firstname)
                stack = request.form.get("stack")
                niche = request.form.get("niche")
                role = request.form.get("role")
                phone_num = ""
                email = ""
                mentor_id = request.form.get("mentor_id")
                avatar = "person.svg"
                task_id = ""
                bio = ""
                location = ""
                bday = ""
                datetime_created = datetime.now()
                
                usr = User(firstname, surname, pwd, _id, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created)
                
                User_db.create_user(usr)

                flash(f"user {_id} created successfully")
                return redirect(url_for('view_user_profile'))
            else:
                return render_template('forms/create_user.html')
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/view/users' )
def view_users():
    user_role = session["role"]
    stack = session["stack"]

    if "user" in session:
        if user_role=="Admin":
            users = list(User_db.get_all_users())
            return render_template('pages/view_users.html', users=users)
            
        elif user_role == "lead":
            users = list(User_db.get_users_by_stack(stack))
            return render_template('pages/view_users.html', users=users)
        
        else:
            flash("permission not granted!")
            return redirect(url_for('login'))
    
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/view/user/profile')
def view_user_profile():
    user_role = session["role"]
    stack = session["stack"]
    requested_id = request.form.get("_id")
    current_user_id = session["_id"]
    
    if "user" in session:
        if user_view_permission(user_role, current_user_id, requested_id, stack) is True:
            requested_profile = User_db.get_user_by_id(requested_id)
            
            return render_template('pages/view_profile.html', requested_profile=requested_profile)
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
        

@app.route('/admin/edit_profile')
def admin_edit_user_profile():
    user_role = session["role"]
    user_id = session["_id"]
    requested_id = request.form.get("current_id")
    
    if "user" in session:
        if user_role == "Admin":
            firstname = request.form.get("firstname")
            surname = request.form.get("surname")
            _id = generate.user_id(firstname)
            stack = request.form.get("stack")
            niche = request.form.get("niche")
            role = request.form.get("role")
            mentor_id = request.form.get("mentor_id")
            
            updated = User_db.update_user_profile(requested_id, firstname, surname, _id, stack, niche, role, mentor_id)
            
            if updated:
                flash(f"{requested_id} updated! New ID is {_id}")
                return redirect(url_for('view_user_profile'))
                
        elif user_id == requested_id:
            avatar = request.files['avatar']
            pwd = generate_password_hash(request.form.get("pwd"))
            phone_num = request.form.get("phone_num")
            email = request.form.get("email")
            bio = request.form.get("bio")
            location = request.form.get("location")
            bday = request.form.get("bday")
            
            if avatar and alllowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                updated = User_db.update_user_profile(filename, pwd, phone_num, email, bio, location, bday)
                
                if updated:
                    flash("profile updated successfully")
                    return redirect(url_for('user_profile'))
                else:
                    flash("profile update unsuccessful!")
                    return redirect(url_for('user_profile'))
                
            else:
                user_profile = User_db.get_user_by_id("requested_id")
                filename = user_profile["avatar"]
                updated = User_db.update_user_profile(filename, pwd, phone_num, email, bio, location, bday)
                
                flash("profile updated successfully")
                return redirect(url_for('user_profile'))
            
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/admin/delete_user')
def admin_delete_user():
    user_role = session["role"]
    
    if "user" in session:
        if user_role == "Admin":
            _id = request.form.get("_id")
            deleted = User_db.delete_user(_id)
            
            if deleted:
                flash(f"User {_id} deleted successfully!")
                return redirect(url_for('view_users'))
            else:
                flash(f'The request to delete {_id} not successful!')
                return redirect(url_for('view_users'))
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
    

@app.route('/create/task', methods=["GET", "POST"])
def create_task():
    user_role = session["role"]
    
    if "user" in session:
        if user_role == "lead" or user_role == "mentor":
            if request.method == "POST":
                
            
            
                return redirect(url_for('view_stack_tasks'))
            else:
                return render_template('forms/create_task.html')
        else:
            flash  ('permission not granted!')
            return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/stack/tasks')
def view_stack_tasks():
    user_stack = session["stack"]
    
    if "user" in session:
        stack_tasks = list(Task_db.get_tasks_by_stack(user_stack))
        return render_template('pages/view_tasks.html', tasks=stack_tasks)
            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/view/task')
def view_task():
    if "user" in session:
        task_id = request.form.get('task_id')
        task = Task_db.get_task_by_task_id(task_id)
        return render_template('pages/view_task.html', task=task)
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/delete/task')
def delete_task():
    user_role = session["role"]
    
    if "user" in session:
        if user_role =="lead":
            task_id = request.form.get("task_id")
            deleted = Task_db.delete_task(task_id)
            
            if deleted:
                flash(f"Task {task_id} deleted successfully!")
                return redirect(url_for('view_stack_tasks'))
            else:
                flash(f"The request to delete {task_id} not successful!")
                return redirect(url_for('view_stack_tasks'))
        else:
            flash  ('permission not granted!')
            return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/view/equipments')
def view_all_eqpt():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            equipments = list(Eqpt_db.get_all_eqpt())
            return render_template('pages/all_eqpt.html', equipments=equipments)

        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/view/equipments/details')        
def view_eqpt_dtls(eqpt_id):
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            eqpt_dtls = Eqpt_db.get_eqpt_by_id(eqpt_id)
            
            return render_template('pages/eqpt_dtls.html', eqpt_dtls=eqpt_dtls)
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

def eqpt_dtls():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            eqpt_id = request.form.get("eqpt_id")
            
            return redirect(url_for('view_eqpt_dtls'),eqpt_id)   
    
@app.route('/equipment/new')
def eqpt_new_input():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
         
            name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            date_of_arrival = request.form.get("date_of_arrival")
            datetime_inputed = datetime.now()
            datetime_updated = ""
        
            Eqpt_db.new_input(name, quantity, description, date_of_arrival, datetime_inputed, datetime_updated)
            
            flash (f"Equipment {name} inputed successfully!")
            return redirect(url_for('view_all_eqpt'))
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))  
    
@app.route('/equipment/update')
def update_eqpt_dtls():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            eqpt_id = request.form.get("eqpt_id")
            name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            datetime_updated = datetime.now()

            updated = Eqpt_db.update_eqpt_dtls(eqpt_id, name, quantity, description, datetime_updated)
            if updated:
                flash(f"{name} details updated successfully!")
                return redirect(url_for('view_eqpt_dtls'), eqpt_id)
            else:
                flash("The request was unsuccessful!")
                return redirect(url_for('view_eqpt_dtls'), eqpt_id)
                    
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))  
    
    
    
@app.route('/component/delete')
def delete_eqpt():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            
            eqpt_id = request.form.get("eqpt_id")
            deleted = Eqpt_db.delete_existing_eqpt(eqpt_id)
            
            if deleted:
                flash ("Equipment deleted successfully!")
                return redirect(url_for('view_all_eqpt'))
            else:
                flash ('The request was unsuccessful!')
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
    
@app.route('/lost/equiment')
def lost_eqpt():
    user_role = session["role"]
    stack = session["stack"]
    
    if "user" in session:
        if user_role=="Admin" or (user_role =="lead" and stack =="hardware"):
            eqpt_id = request.form.get("eqpt_id")
            quantity = request.form.get("quantity")
            personnel_name = request.form.get("personnel_name")
            datetime_reported = datetime.now()
            
            lost_eqpt_db.new_input(eqpt_id, quantity, personnel_name, datetime_reported)
            flash ("Report filed successfully!")
            return redirect(url_for('view_all_eqpts'))
            
            
        else:
                flash('permission not granted')
                return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))        
            
 
 
 
 
 
 


if __name__=="__main__":
    app.run(debug=True)