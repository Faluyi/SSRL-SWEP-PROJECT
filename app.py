from flask import Flask, session, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from db.models import *
from datetime import datetime
from werkzeug.utils import secure_filename
import os 

User_db = Userdb()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "SSRL"

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def alllowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get('/')
def login():
    
    return render_template('/forms/login.html')

@app.get('/logout')
def logout():
    if "user_uid" in session:
        session.pop("user_id", None)
        
        return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
    
@app.route('/home/me/<pwd>')
def home_args(pwd):
    if "user_uid" in session:
        user_uid = session["user_uid"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_uid(user_uid)
        
        now = datetime.now().strftime
        
        if now("%p") == "AM":
            meridian = "morning"
            
        elif int(now("%H")) >= int(12) and int(now("%H")) < int(16):
            meridian = "afternoon"
        
        else:
            meridian = "evening"
            
        date = {
            "day" : now("%A"),
            "month" : now("%B"),
            "date" : now("%d"),
            "meridian" : meridian
        }
        
        uid = session["created_id"]
        
        fullname = User_db.get_user_by_uid(uid)["fullname"]    
        app.logger.info(uid)
        app.logger.info(pwd)
        
        if user_role=="Admin":
            members = list(User_db.get_all_users_limited())
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members, uid=uid, pwd=pwd, fullname=fullname)
            
        elif user_role != "Admin":
            members = list(User_db.get_users_by_stack_limited(stack))
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members, uid=uid, pwd=pwd, fullname=fullname)
        
        else:
            flash("permission not granted!")
            return redirect(url_for('login'))

    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
    
@app.route('/home/me')
def home():
    if "user_uid" in session:
        user_uid = session["user_uid"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_uid(user_uid)
        
        now = datetime.now().strftime
        
        if now("%p") == "AM":
            meridian = "morning"
            
        elif int(now("%H")) >= int(12) and int(now("%H")) < int(16):
            meridian = "afternoon"
        
        else:
            meridian = "evening"    
            
        date = {
            "day" : now("%A"),
            "month" : now("%B"),
            "date" : now("%d"),
            "meridian" : meridian
        }
        
        if user_role=="Admin":
            members = list(User_db.get_all_users_limited())
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members)
            
        elif user_role != "Admin":
            members = list(User_db.get_users_by_stack_limited(stack))
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members)
        
        else:
            flash("permission not granted!")
            return redirect(url_for('login'))
        
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

        
@app.post('/user/authenticate')
def authenticate_user():
    user_uid = request.form.get("user_id")
    pwd = request.form.get("pwd")
    user_profile = User_db.get_user_by_uid(user_uid)
    app.logger.info(user_uid)
    app.logger.info(user_profile)
    
    authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
    
    if user_profile:
        if authenticated==True:
            session["user_uid"] = user_uid
            session["user_role"] = user_profile["role"]
            session["stack"] = user_profile["stack"]
            fullname = user_profile["fullname"]
            
            flash (f"Welcome! {fullname}")
            return redirect(url_for('home'))
        else:
            flash("Invalid password")
            return redirect(url_for("login"))
        
    else:
        flash("Invalid log in ID")
        return redirect(url_for('login'))

    
@app.route('/Admin/create/user', methods=["GET", "POST"])
def create_user():
    user_role = session["user_role"]
    
    if "user_uid" in session:
        if user_role == "Admin":
        
            firstname = request.form.get("firstname")
            surname = request.form.get("surname")
            fullname = "{0} {1}".format(surname, firstname)
            pwd = generate.password()
            hashed_pwd = generate_password_hash(pwd)
            uid = generate.user_id(firstname)
            app.logger.info(uid)
            app.logger.info(pwd)
            stack = request.form.get("stack")
            niche = request.form.get("niche")
            role = request.form.get("role")
            phone_num = "NIL"
            email = "NIL"
            mentor_id = "NIL"
            avatar = "person.svg"
            task_id = "NIL"
            bio = "NIL"
            location = "NIL"
            bday = "NIL"
            datetime_created = datetime.now()
            
            usr = User(firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created)
            app.logger.info(usr)
            
            User_db.create_user(usr)
            
            session["created_id"]=uid
            
            flash(f"user {uid} created successfully","created")
            return redirect(url_for('home_args', pwd=pwd))
        
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.get('/view/members' )
def view_members():
    user_role = session["user_role"]
    stack = session["stack"]
    uid = session["user_uid"]
    user_profile = User_db.get_user_by_uid(uid)
    
    if "user_uid" in session:
        if user_role=="Admin":
            
            leads = list(User_db.get_user_by_role(role = "Lead"))
            app.logger.info(leads)
            interns = list(User_db.get_user_by_role(role="Intern"))
            return render_template('pages/all_members.html', leads=leads, interns=interns, user_profile=user_profile)
            
        elif user_role != "Admin":
            members = list(User_db.get_users_by_stack(stack))
            app.logger.info(members)
            return render_template('pages/all_members.html',members=members, user_profile=user_profile)
        
        else:
            flash("permission not granted!")
            return redirect(url_for('login'))
    
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/show/profile/<requested_id>', methods=["POST","GET"])
def show_user_profile(requested_id):
    user_role = session["user_role"]
    stack = session["stack"]
    current_user_id = session["user_id"]
    
    if "user" in session:
        if user_view_permission(user_role, current_user_id, requested_id, stack) is True:
            requested_profile = User_db.get_user_by_uid(requested_id)
            
            return render_template('pages/view_profile.html', requested_profile=requested_profile, user_profile=user_profile)
        else:
            flash('permission not granted')
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.post('/request/profile')
def request_profile():
    
    requested_id = request.form.get("uid")
    
    if "user_uid" in session:
        
        return redirect(url_for('show_user_profile', requested_id=requested_id))
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
    
    
@app.get('/view/profile/me')
def view_profile_me():
    current_user_id = session["user_uid"]
    if "user_uid" in session:
        requested_profile = User_db.get_user_by_uid(current_user_id)
        return render_template('pages/view_profile.html', user_profile=requested_profile, current_uid=current_user_id)            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.post('/user/edit/profile')
def user_edit_profile():
    user_role = session["user_role"]
    user_id = session["user_uid"]
    
    if "user_uid" in session:
        
        if  user_role !="Admin":
            avatar = request.files['avatar']
            phone_num = request.form.get("phone_num")
            email = request.form.get("email")
            bio = request.form.get("bio")
            location = request.form.get("location")
            bday = request.form.get("bday")
            uid = request.form.get("uid")
            
            if avatar and alllowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                dtls = updateUser(filename, phone_num, email, bio, location, bday)
                
                updated = User_db.update_user_profile(user_id, dtls)
                
                if updated:
                    flash("profile updated successfully")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("profile update unsuccessful!")
                    return redirect(url_for('view_profile_me'))
                
            else:
                user_profile = User_db.get_user_by_uid(user_id)
                filename = user_profile["avatar"]
                dtls = updateUser(filename, phone_num, email, bio, location, bday)
                
                updated = User_db.update_user_profile(user_id, dtls)
                
                flash("profile updated successfully")
                return redirect(url_for('view_profile_me'))
            
        if user_role=="Admin":
            
            firstname = request.form.get("firstname")
            surname = request.form.get("surname")
            fullname = "{0} {1}".format(surname, firstname)
            stack = request.form.get("stack")
            niche = request.form.get("niche")
            role = request.form.get("role")
            #mentor_id = request.form.get("mentor_id")
            avatar = request.files['avatar']
            phone_num = request.form.get("phone_num")
            email = request.form.get("email")
            bio = request.form.get("bio")
            location = request.form.get("location")
            bday = request.form.get("bday")

            if User_db.get_user_by_uid(user_id)["firstname"]==firstname:
                uid = user_id
                
                if avatar and alllowed_file(avatar.filename):
                    filename = secure_filename(avatar.filename)
                    avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                    updated = User_db.update_user_profile(user_id, dtls)
                
                    if updated:
                        flash("profile updated successfully")
                        return redirect(url_for('view_profile_me'))
                    else:
                        flash("profile update unsuccessful!")
                        return redirect(url_for('view_profile_me'))
                
                else:
                    user_profile = User_db.get_user_by_uid(user_id)
                    filename = user_profile["avatar"]
                    dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                    updated = User_db.update_user_profile(user_id, dtls)
                    
                    if updated:
                        flash("profile updated successfully")
                        return redirect(url_for('view_profile_me'))
                    else:
                        flash("profile update unsuccessful!")
                        return redirect(url_for('view_profile_me'))
                
                
            else:
                uid = generate.user_id(firstname)
                
                if avatar and alllowed_file(avatar.filename):
                    filename = secure_filename(avatar.filename)
                    avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                    updated = User_db.update_user_profile(user_id, dtls)
                    if updated:
                        flash("profile updated successfully,")
                        return redirect(url_for('login'))
                    else:
                        flash("profile update unsuccessful!")
                        return redirect(url_for('user_profile'))
                    
                else:
                    user_profile = User_db.get_user_by_uid(user_id)
                    filename = user_profile["avatar"]
                    dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                    updated = User_db.update_user_profile(user_id, dtls)
                    flash("profile updated successfully")
                    return redirect(url_for('user_profile'))
            
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.route('/admin/edit/profile')
def admin_edit_profile():
    user_role = session["role"]
    requested_id = request.form.get("personnel_id")
    
    if "user_id" in session:
        if user_role == "Admin":
            
            firstname = request.form.get("firstname")
            surname = request.form.get("surname")
            stack = request.form.get("stack")
            niche = request.form.get("niche")
            role = request.form.get("role")
            mentor_id = request.form.get("mentor_id")
            
            if User_db.get_user_by_uid(requested_id)["firstname"]==firstname:
                uid = requested_id
                updated = User_db.update_user_profile(requested_id, uid, firstname, surname, stack, niche, role, mentor_id)
                
                if updated:
                    flash("profile updated successfully")
                    return redirect(url_for('user_profile'))
                else:
                    flash("profile update unsuccessful!")
                    return redirect(url_for('user_profile'))
            
            else:
                uid = generate.user_id(firstname)
                
                updated = User_db.update_user_profile(requested_id, uid, firstname, surname, stack, niche, role, mentor_id)

                if updated:
                    flash("profile updated successfully")
                    return redirect(url_for('user_profile'))
                else:
                    flash("profile update unsuccessful!")
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
            
 
@app.post('/update/email')
def update_email():
    if "user_id" in session:
        uid = session["user_uid"]
        
        pwd = request.form.get("pwd")
        new_email = request.form.get("new_email")
        confirm_email = request.form.get("confirm_email")
        
        user_profile = User_db.get_user_by_uid(uid)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
        
        if authenticated:
            if new_email == confirm_email:
                dtls = updateEmail(new_email)
                updated = User_db.update_user_profile(uid, dtls)
                
                if updated:
                    flash("Email address updated successfully!")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("Unable to update your email address! Try again")
                    return redirect(url_for('view_profile_me')) 
            else:
                flash("Unmatching email address! Unable to update email address")
                return redirect(url_for('view_profile_me'))
                
        else:
            flash("Invalid password")
            return redirect(url_for('view_profile_me'))
        
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))

@app.post('/update/password')
def update_password():
    if "user_id" in session:
        uid = session["user_uid"]
        
        old_pwd = request.form.get("old_pwd")
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")
        
        user_profile = User_db.get_user_by_uid(uid)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], old_pwd)
        
        if authenticated:
            if new_pwd == confirm_pwd:
                hashed_pwd = generate_password_hash(new_pwd)
                dtls = updatePwd(hashed_pwd)
                updated = User_db.update_user_profile(uid, dtls)
                
                if updated:
                    flash("Password updated successfully!")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("Unable to change your password! Try again")
                    return redirect(url_for('view_profile_me')) 
            else:
                flash("Unmatching password input! Unable to update your password")
                return redirect(url_for('view_profile_me'))
                
        else:
            flash("Invalid password")
            return redirect(url_for('view_profile_me'))
        
    else:
        flash  ('you are not logged in!')
        return redirect(url_for('login'))
 


if __name__=="__main__":
    app.run(debug=True)