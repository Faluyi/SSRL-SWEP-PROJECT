from flask import Flask, session, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from db.models import *
from datetime import datetime
from werkzeug.utils import secure_filename
import os 

User_db = Userdb()
Eqpt_db = Eqptdb()
lost_eqpt_db = lost_eqptdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.secret_key = "SSRL"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'smartsystemlaboratory@gmail.com'
app.config['MAIL_PASSWORD'] = 'pztlwqclbadcrhyo'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


def alllowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get('/')
def login():
    
    return render_template('/forms/login.html')

@app.get('/logout')
def logout():
    if "user_id" in session:
        session.pop("user_id", None)
        
        return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
    
@app.route('/home/me')
def home():
    if "user_id" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
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
            flash("permission not granted!", "danger")
            return redirect(url_for('login'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

        
@app.post('/user/authenticate')
def authenticate_user():
    user_uid = request.form.get("user_id")
    pwd = request.form.get("pwd")
    user_profile = User_db.get_user_by_uid(user_uid)
    app.logger.info(user_uid)
    app.logger.info(user_profile)
    
    
    
    if user_profile:
        authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
        if authenticated is True:
            session["user_uid"] = user_uid
            session["user_id"] = str(user_profile["_id"])
            session["user_role"] = user_profile["role"]
            session["stack"] = user_profile["stack"]
            fullname = user_profile["fullname"]
            
            flash (f"Welcome! {fullname}", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid password", "danger")
            return redirect(url_for("login"))
        
    else:
        flash("Invalid log in ID", "danger")
        return redirect(url_for('login'))

    
@app.route('/Admin/create/user', methods=["GET", "POST"])
def create_user():
    user_role = session["user_role"]
    
    if "user_id" in session:
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
            email = request.form.get("email")
            mentor_id = "NIL"
            avatar = "person.svg"
            task_id = "NIL"
            bio = "NIL"
            location = "NIL"
            bday = "NIL"
            now = datetime.now().strftime
            month = now("%B")
            year =  now("%Y")
            datetime_created = "{0}, {1}".format(month, year)
            
            usr = User(firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created)
            app.logger.info(usr)
            
            
            try:
                msg = Message('SSRL Login credentials', sender = 'smartsystemlaboratory@gmail.com', recipients = [email])
                msg.body = f"Welcome to SSRL🤗 \nCheck out your login credentials below\n\nUnique I.D: {uid} \nPassword: {pwd}  \n\n\nFrom SSRL Team"
                
                mail.send(msg)
                
                User_db.create_user(usr)
                
                flash(f"user {uid} created successfully","success")
                return redirect(url_for('home'))
            except:
                flash("Unable to create user at the moment! Please confirm that the inputed email is correct or check your internet connection.", "danger")
                return redirect(url_for('home'))
                
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/members' )
def view_members():
    user_role = session["user_role"]
    stack = session["stack"]
    id = session["user_id"]
    user_profile = User_db.get_user_by_oid(id)
    
    if "user_id" in session:
        if user_role=="Admin":
            softlead = []
            hardlead= []
            hardinterns = []
            softinterns = []
            
            leads = list(User_db.get_user_by_role(role = "Lead"))
            interns = list(User_db.get_user_by_role(role="Intern"))
            
            for lead in leads:
                if lead['stack']=="Software":
                    softlead.append(lead)
                else:
                    hardlead.append(lead)
            
            for intern in interns:
                if intern['stack']=="Hardware":
                    hardinterns.append(intern)
                else:
                    softinterns.append(intern)
                    
            app.logger.info(leads)
            return render_template('pages/all_members.html',softlead=softlead, hardlead=hardlead, softinterns=softinterns, hardinterns=hardinterns, user_profile=user_profile)
            
        elif user_role == "Lead" and (stack=="Software" or stack=="Hardware"):
            members = list(User_db.get_users_by_stack(stack))
            app.logger.info(members)
            return render_template('pages/all_members.html',members=members, user_profile=user_profile)
        
        else:
            flash("permission not granted!", "danger")
            return redirect(url_for('login'))
    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.route('/show/profile/<requested_id>', methods=["POST","GET"])
def show_user_profile(requested_id):
    user_role = session["user_role"]
    stack = session["stack"]
    current_user_id = session["user_id"]
    user_profile = User_db.get_user_by_oid(current_user_id)
    
    if "user_id" in session:
        requested_profile = User_db.get_user_by_oid(requested_id)
        if user_role == "Admin" or (user_role== "Lead" and stack==requested_profile["stack"]):
            
            return render_template('pages/view_user_profile.html', requested_profile=requested_profile, user_profile=user_profile)
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

    
    
@app.get('/view/profile/me')
def view_profile_me():
    current_user_id = session["user_id"]
    if "user_id" in session:
        requested_profile = User_db.get_user_by_oid(current_user_id)
        return render_template('pages/view_profile.html', user_profile=requested_profile, current_uid=current_user_id)            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.post('/user/edit/profile')
def user_edit_profile():
    user_id = session["user_id"]

    if "user_id" in session:
        
            avatar = request.files['avatar']
            phone_num = request.form.get("phone_num")
            #email = request.form.get("email")
            bio = request.form.get("bio")
            location = request.form.get("location")
            bday = request.form.get("bday")
            
            if avatar and alllowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                dtls = updateUser(filename, phone_num, bio, location, bday)
                
                updated = User_db.update_user_profile_by_oid(user_id, dtls)
                
                if updated:
                    flash("profile updated successfully", "success")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("profile update unsuccessful!", "danger")
                    return redirect(url_for('view_profile_me'))
                
            else:
                user_profile = User_db.get_user_by_oid(user_id)
                filename = user_profile["avatar"]
                dtls = updateUser(filename, phone_num, bio, location, bday)
                
                updated = User_db.update_user_profile_by_oid(user_id, dtls)
                
                if updated:
                    flash("profile updated successfully", "success")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("profile update unsuccessful!", "danger")
                    return redirect(url_for('view_profile_me'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

            
@app.post('/admin/edit/profile/<edit_id>')
def admin_edit_profile(edit_id):
    user_role = session["user_role"]
    user_id = session["user_id"]
    if "user_id" in session:
        
        if user_role=="Admin" and edit_id == user_id:
                
                firstname = request.form.get("firstname")
                profile = User_db.get_user_by_oid(user_id)
                
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

                if profile["firstname"]==firstname:
                    uid = profile["uid"]
                    
                    
                    
                    if avatar and alllowed_file(avatar.filename):
                        filename = secure_filename(avatar.filename)
                        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                        updated = User_db.update_user_profile_by_oid(user_id, dtls)
                    
                        if updated:
                            flash("profile updated successfully", "success")
                            return redirect(url_for('view_profile_me'))
                        else:
                            flash("profile update unsuccessful!", "danger")
                            return redirect(url_for('view_profile_me'))
                    
                    else:
                        user_profile = User_db.get_user_by_oid(user_id)
                        filename = user_profile["avatar"]
                        dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                        updated = User_db.update_user_profile_by_oid(user_id, dtls)
                        
                        if updated:
                            flash("profile updated successfully", "success")
                            return redirect(url_for('view_profile_me'))
                        else:
                            flash("profile update unsuccessful!", "danger")
                            return redirect(url_for('view_profile_me'))
                    
                    
                else:
                    uid = generate.user_id(firstname)
                    
                    
                    if avatar and alllowed_file(avatar.filename):
                        filename = secure_filename(avatar.filename)
                        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                        updated = User_db.update_user_profile_by_oid(user_id, dtls)
                        if updated:
                            flash("profile updated successfully,", "success")
                            return redirect(url_for('view_profile_me'))
                        else:
                            flash("profile update unsuccessful!", "danger")
                            return redirect(url_for('view_profile_me'))
                        
                    else:
                        user_profile = User_db.get_user_by_oid(user_id)
                        filename = user_profile["avatar"]
                        dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                        try:
                            msg = Message('SSRL Profile Updated', sender = 'smartsystemlaboratory@gmail.com', recipients = [user_profile["email"]])
                            msg.body = f"Your profile has been updated\n Check out your new Id below below\n\nUnique I.D: {uid}\n\n\nFrom SSRL Team"
                            
                            mail.send(msg)
                            
                            updated = User_db.update_user_profile_by_oid(user_id, dtls)
                            if updated:
                                flash("Profile updated successful!", "success")
                                return redirect(url_for('view_profile_me'))
                            else:
                                flash("profile update unsuccessful!", "danger")
                                return redirect(url_for('view_members'))
                        except: 
                            flash("Profile update unsuccessful! Please confirm that the inputed email address is correct and that you are connected to the internet.", "danger")
                            return redirect(url_for('view_members'))
                        
                    
        elif user_role=="Admin" and edit_id != user_id:
            firstname = request.form.get("firstname")
            surname = request.form.get("surname")
            fullname = "{0} {1}".format(surname, firstname)
            stack = request.form.get("stack")
            niche = request.form.get("niche")
            role = request.form.get("role")
            #mentor_id = request.form.get("mentor_id")
            edit_profile = User_db.get_user_by_oid(edit_id)

            if edit_profile["firstname"]==firstname:
                uid = edit_profile["uid"]
                dtls = AdminUpdateUser(firstname, surname, fullname, uid, stack, niche, role)

                updated = User_db.update_user_profile_by_oid(edit_id, dtls)
            
                if updated:
                    flash("profile updated successfully", "success")
                    return redirect(url_for('show_user_profile', requested_id=edit_profile["_id"]))
                else:
                    flash("profile update unsuccessful!", "danger")
                    return redirect(url_for('view_members'))
            
                
            else:
                uid = generate.user_id(firstname)
                
                dtls = AdminUpdateUser(firstname, surname, fullname, uid, stack, niche, role)

                try:
                    msg = Message('SSRL Profile Updated', sender = 'faluyiisaiah@gmail.com', recipients = [edit_profile["email"]])
                    msg.body = f"Your profile has been updated\n Check out your new Id below below\n\nUnique I.D: {uid}\n\n\nFrom SSRL Team"
                    
                    mail.send(msg)
                    
                    updated = User_db.update_user_profile_by_oid(edit_id, dtls)
                    if updated:
                        flash("Profile updated successful!", "success")
                        return redirect(url_for('show_user_profile', requested_id=edit_profile["_id"]))
                    else:
                        flash("profile update unsuccessful!", "danger")
                        return redirect(url_for('view_members'))
                except: 
                    flash("Profile update unsuccessful! Please confirm that the inputed email address is correct and that you are connected to the internet.", "danger")
                    return redirect(url_for('view_members'))
                        
                    
                    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

    


@app.route('/Add/lead/<intern_uid>')
def admin_add_lead(intern_uid):
    user_role = session["user_role"]
    if "user_id" in session:
        if user_role == "Admin":
            dtls = {
                "role": "Lead"
            }
            updated = User_db.update_user_role(intern_uid, dtls)
            
            if updated:
                flash("profile updated successfully", "success")
                return redirect(url_for('view_members'))
            else:
                flash("profile update unsuccessful!", "danger")
                return redirect(url_for('view_members'))
            
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.route('/admin/delete_user/<requested_id>')
def admin_delete_user(requested_id):
    user_role = session["user_role"]
    
    if "user_id" in session:
        if user_role == "Admin":
            deleted = User_db.delete_user(requested_id)
            
            if deleted:
                flash(f"User {requested_id} deleted successfully!", "success")
                return redirect(url_for('view_members'))
            else:
                flash(f'The request to delete {requested_id} not successful!', "danger")
                return redirect(url_for('view_users'))
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('home'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    

@app.route('/create/task', methods=["GET", "POST"])
def create_task():
    user_role = session["role"]
    
    if "user_id" in session:
        if user_role == "lead" or user_role == "mentor":
            if request.method == "POST":
                
            
            
                return redirect(url_for('view_stack_tasks'))
            else:
                return render_template('forms/create_task.html')
        else:
            flash  ('permission not granted!', "danger")
            return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.route('/stack/tasks')
def view_stack_tasks():
    user_stack = session["stack"]
    
    if "user_id" in session:
        stack_tasks = list(Task_db.get_tasks_by_stack(user_stack))
        return render_template('pages/view_tasks.html', tasks=stack_tasks)
            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.route('/view/task')
def view_task():
    if "user_id" in session:
        task_id = request.form.get('task_id')
        task = Task_db.get_task_by_task_id(task_id)
        return render_template('pages/view_task.html', task=task)
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/delete/task/<task_id>')
def delete_task():
    user_role = session["role"]
    
    if "user_id" in session:
        if user_role =="lead":
            task_id = request.form.get("task_id")
            deleted = Task_db.delete_task(task_id)
            
            if deleted:
                flash(f"Task {task_id} deleted successfully!", "success")
                return redirect(url_for('view_stack_tasks'))
            else:
                flash(f"The request to delete {task_id} not successful!","danger")
                return redirect(url_for('view_stack_tasks'))
        else:
            flash  ('permission not granted!', "danger")
            return redirect(url_for('login'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/equipments')
def view_all_eqpt():
    user_id = session["user_id"]
    user_role = session["user_role"]
    stack = session["stack"]
    user_profile = User_db.get_user_by_oid(user_id)
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            equipments = list(Eqpt_db.get_all_eqpt())
            personnels = User_db.get_all_users()
            lost_eqpts = lost_eqpt_db.get_all()
            availables = Eqpt_db.get_all_available_eqpt()
            
            return render_template('pages/equipments.html', user_profile=user_profile, equipments=equipments, lost_eqpts=lost_eqpts, personnels=personnels, availables=availables)

        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/equipments/<eqpt_id>')        
def view_eqpt_dtls(eqpt_id):
    user_id = session["user_id"]
    user_role = session["user_role"]
    stack = session["stack"]
    user_profile = User_db.get_user_by_oid(user_id)
    
    if "user_uid" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            eqpt_dtls = Eqpt_db.get_eqpt_by_id(eqpt_id)
            
            return render_template('pages/view_equipment.html', user_profile=user_profile, eqpt_dtls=eqpt_dtls)
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


    
@app.post('/equipment/new')
def eqpt_new_input():
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
         
            name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            date_of_arrival = request.form.get("arrival")
            type = request.form.get("type")
            status = "available"
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            datetime_inputed = "{0} {1}, {2}".format(month, date, year)
            date_updated = ""
        
            dtls = Eqpt(name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_updated)
            
            Eqpt_db.new_input(dtls)
            flash (f"Equipment {name} inputed successfully!", "success")
            return redirect(url_for('view_all_eqpt'))
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/equipment/update/<eqpt_id>')
def update_eqpt_dtls(eqpt_id):
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            date_of_arrival = request.form.get("arrival")
            type = request.form.get("type")
            status = request.form.get("status")
            datetime_inputed = request.form.get("date_inputed")
            now = datetime.now()
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_updated = "{0} {1}, {2}".format(month, date, year)

            dtls = Eqpt(name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_updated)
            
            updated = Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            if updated:
                flash(f"{name} details updated successfully!", "success")
                return redirect(url_for('view_eqpt_dtls'), eqpt_id)
            else:
                flash("The request was unsuccessful!", "danger")
                return redirect(url_for('view_eqpt_dtls'), eqpt_id)
                    
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))  
    
    
    
@app.get('/delete/equipment/<eqpt_id>')
def delete_eqpt(eqpt_id):
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            
            deleted = Eqpt_db.delete_existing_eqpt(eqpt_id)
            
            if deleted:
                flash ("Equipment deleted successfully!", "success")
                return redirect(url_for('view_all_eqpt'))
            else:
                flash ('The request was unsuccessful!', "danger")
                redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/lost/equiment')
def lost_eqpt():
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
            eqpt_id = request.form.get("id")
            eqpt = Eqpt_db.get_eqpt_by_id(eqpt_id)
            name = eqpt["name"]
            type = eqpt["type"]
            old_quant = int(eqpt["quantity"])
            quantity = request.form.get("quantity")
            personnel_id = request.form.get("person_resp")
            status = request.form.get("status")
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_reported = "{0} {1}, {2}".format(month, date, year)
            date_edited = ""
            
            dtls = lostEqpt(eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited)
            lost_eqpt_db.new_input(dtls)
            
            curr_quantity1 = old_quant - int(quantity)
            if curr_quantity1 > 1 :
                availability = "available"
                curr_quantity = curr_quantity1
            else:
                availability = "unavailable"
                curr_quantity = "0"
                
           
            _quantity = curr_quantity
            _status = availability

            dtls = Available(_quantity, _status)
            
            Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            
            flash (f"Equipment {name} recorded {status} successfully!", "success")
            return redirect(url_for('view_all_eqpt'))
            
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))   
    
@app.get('/view/lost/equipment/<eqpt_id>')        
def view_lost_eqpt_dtls(eqpt_id):
    user_id = session["user_id"]
    user_role = session["user_role"]
    stack = session["stack"]
    user_profile = User_db.get_user_by_oid(user_id)
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            eqpt_dtls = lost_eqpt_db.get_eqpt_by_id(eqpt_id)
            personnels = User_db.get_all_users()
            
            return render_template('pages/lost_equipment.html', user_profile=user_profile, eqpt_dtls=eqpt_dtls, personnels=personnels)
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/edit/lost/equiment/<eqpt_id>')
def edit_lost_eqpt(eqpt_id):
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
            name = request.form.get("name")
            type = request.form.get("type")
            quantity = request.form.get("quantity")
            personnel_id = request.form.get("person_resp")
            status = request.form.get("status")
            date_reported = request.form.get("date_reported")
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_edited = "{0} {1}, {2}".format(month, date, year)
            
            dtls = lostEqpt(eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited)
            updated = lost_eqpt_db.update_eqpt_dtls(eqpt_id, dtls)

            if updated:
                flash ("Report details edited successfully!", "success")
                return redirect(url_for('view_lost_eqpt_dtls', eqpt_id))
            
            else:
                flash ("Report details edit unsuccessfully!", "danger")
                return redirect(url_for('view_lost_eqpt_dtls', eqpt_id))
            
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))   

    
@app.get('/delete/lost/equipment/<eqpt_id>')
def delete_lost_eqpt(eqpt_id):
    user_role = session["user_role"]
    stack = session["stack"]
    
    if "user_id" in session:
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            
            deleted = lost_eqpt_db.delete_lost_eqpt(eqpt_id)
            
            if deleted:
                flash ("Equipment deleted successfully!", "success")
                return redirect(url_for('view_all_eqpt'))
            else:
                flash ('The request was unsuccessful!', "danger")
                return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
     
            
 
@app.post('/update/email')
def update_email():
    if "user_id" in session:
        id = session["user_id"]
        
        pwd = request.form.get("pwd")
        new_email = request.form.get("new_email")
        confirm_email = request.form.get("confirm_email")
        user_profile = User_db.get_user_by_oid(id)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
        
        if authenticated:
            if new_email == confirm_email:
                dtls = updateEmail(new_email)
                updated = User_db.update_user_profile_by_oid(id, dtls)
                
                if updated:
                    flash("Email address updated successfully!", "success")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("Unable to update your email address! Try again", "danger")
                    return redirect(url_for('view_profile_me')) 
            else:
                flash("Unmatching email address! Unable to update email address", "danger")
                return redirect(url_for('view_profile_me'))
                
        else:
            flash("Invalid password", "danger")
            return redirect(url_for('view_profile_me'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.post('/update/password')
def update_password():
    if "user_id" in session:
        id = session["user_id"]
        
        old_pwd = request.form.get("old_pwd")
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")
        
        user_profile = User_db.get_user_by_oid(id)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], old_pwd)
        
        if authenticated:
            if new_pwd == confirm_pwd:
                hashed_pwd = generate_password_hash(new_pwd)
                dtls = updatePwd(hashed_pwd)
                updated = User_db.update_user_profile_by_oid(id, dtls)
                
                if updated:
                    flash("Password updated successfully!", "success")
                    return redirect(url_for('view_profile_me'))
                else:
                    flash("Unable to change your password! Try again", "danger")
                    return redirect(url_for('view_profile_me')) 
            else:
                flash("Unmatching password input! Unable to update your password", "danger")
                return redirect(url_for('view_profile_me'))
                
        else:
            flash("Invalid password", "danger")
            return redirect(url_for('view_profile_me'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
 

@app.get('/submissions/forms/request')
def get_request_form():
    user_id = session["user_id"]
    
    if "user_id" in session:
        eqpts = Eqpt_db.get_all_eqpt()
        user_profile = User_db.get_user_by_oid(user_id)
        return render_template('forms/request_form.html', eqpts=eqpts, user_profile=user_profile)
    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
    
@app.get('/all/submissions')
def all_submissions():
    role = session["user_role"]
    _id = session["user_id"]
    uid = session["user_uid"]
    stack = session["stack"]
    user_profile = User_db.get_user_by_oid(_id)
    
    
    if "user_id" in session:
        if role == "Intern":
            reports =list(Report_db.get_by_sender(_id, uid))
            requests = list(Request_db.get_by_sender(_id, uid))
            projects = list(Project_db.get_by_choice_recipient(stack))
            
            return render_template('pages/all_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile)
        
        elif role == "Lead":
            if stack == "Software":
                position = "Software"
                reports =  list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                app.logger.info(requests)
                projects = list(Project_db.get_by_sender(_id, uid))
                personnels = list(User_db.get_users_by_stack(stack))
            
                return render_template('pages/all_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels)
            else:
                position = "Hardware"
                reports = list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                projects = list(Project_db.get_by_sender(_id, uid))
                personnels = list(User_db.get_users_by_stack(stack))
            
                return render_template('pages/all_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels)

        elif role == "Admin":
            position = "Admin"
            reports = list(Report_db.get_by_recipient(position))
            requests = list(Request_db.get_by_recipient(position, _id))
            projects = list(Project_db.get_by_sender(_id, uid))
            personnels = list(User_db.get_all_users())
            
            return render_template('pages/all_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels)
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.post('/submissions/submit/request_form')
def post_request_form():
    user_id = session["user_id"]
    uid = session["user_uid"]
    if "user_id" in session:
        
        title = request.form.get("title")
        type = request.form.get("type")
        eqpt_id = request.form.get("eqpt_id")
        quantity = request.form.get("quantity")
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        purpose = request.form.get("purpose")
        recipient = request.form.get("recipient")
        sender = {
            "_id": user_id,
            "uid": uid  
                  
        }
        status = "Pending"
        now = datetime.now().strftime
        month = now("%B")
        date = now("%d")
        year = now("%Y")
        date_submitted = "{0} {1}, {2}".format(month, date, year)
        
        if recipient == "Admin":
            role = "Admin"
            id = User_db.get_user_by_role(role)["_id"]
            
            recipient_dtls = {
                "position": "Admin",
                "id": id
            }
        elif recipient == "software":
            stack = "Software"
            id = User_db.get_lead(stack)["_id"]
            
            recipient_dtls = {
                "position": "Software",
                "id": id
            }
        elif recipient == "hardware":
            stack="Hardware" 
            id = User_db.get_lead(stack)["_id"]
            recipient_dtls = {
                "position": "Hardware",
                "id": id
            }
        
        requested = Request(title, type, eqpt_id, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted)
        Request_db.insert_new(requested)
        
        flash("Request submitted successfully!", "success")
        return redirect(url_for('all_submissions'))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/request/<request_id>')
def view_request(request_id):
    id = session["user_id"]
    
    if "user_id" in session:
        user_profile = User_db.get_user_by_oid(id)
        request = Request_db.get_by_request_id(request_id)
    
        return render_template('pages/view_request.html', request=request, user_profile=user_profile)
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))    
        

@app.post('/submissions/submit/report')
def post_report_form():
    user_id = session["user_id"]
    uid = session["user_uid"]
    
    if "user_id" in session:
        
        title = request.form.get("title")
        report_no = request.form.get("report_no")
        content = request.form.get("content")
        recipient = request.form.get("recipient")
        sender = {
            "_id": user_id,
            "uid": uid  
                  
        }
        now = datetime.now().strftime
        month = now("%B")
        date = now("%d")
        year = now("%Y")
        date_submitted = "{0} {1}, {2}".format(month, date, year)
        
        
        
        report = Report(title, report_no, content, recipient, sender, date_submitted)
        Report_db.insert_new(report)
        
        flash("Report submitted successfully!", "success")
        return redirect(url_for('all_submissions'))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.post('/submissions/create/projects')
def post_project_form():
    user_id = session["user_id"]
    uid = session["user_uid"]
    
    if "user_id" in session:
        
        topic = request.form.get("topic")
        focus = request.form.get("focus")
        objectives = request.form.get("objectives")
        recipient = request.form.get("recipient")
        
        sender = {
            "_id": user_id,
            "uid": uid  
                  
        }
        now = datetime.now().strftime
        month = now("%B")
        date = now("%d")
        year = now("%Y")
        date_submitted = "{0} {1}, {2}".format(month, date, year)
        
        project = Project(topic, focus, objectives, recipient, sender, date_submitted)
        Project_db.insert_new(project)
        
        flash("Project created successfully!", "success")
        return redirect(url_for('all_submissions'))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))







if __name__=="__main__":
    app.run(debug=True)