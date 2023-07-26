from flask import Flask, session, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from db.models import *
from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO
import os 
from properties import *
import cloudinary
from cloudinary import uploader
import urllib.request

User_db = Userdb()
Eqpt_db = Eqptdb()
lost_eqpt_db = lost_eqptdb()
Inventory_db = Inventorydb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()

UPLOAD_FOLDER = 'static/images'
PROJECT_FOLDER = 'submissions/projects'


app = Flask(__name__)

bcrypt = Bcrypt(app)

app.secret_key = os.urandom(32)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROJECT_FOLDER'] = PROJECT_FOLDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'smartsystemlaboratory@gmail.com'
app.config['MAIL_PASSWORD'] = email_pswd
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

cloudinary.config( 
  cloud_name = "diaownipw", 
  api_key = cloud_key, 
  api_secret = cloud_secret,
  secure = True
)

mail = Mail(app)




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
    
@app.get('/forgot/password')
def forgot_password():
    session["confirmed"]="false"
    return render_template('forms/forgot_password.html')

@app.post('/confirm/credentials')
def confirm_credentials():
    status = session["confirmed"]
    
    if status == "false":
        uid = request.form.get("uid")
        email = request.form.get("email")
        user = User_db.get_user_by_uid(uid)
        if user:
            if user["email"]==email:
                otp = generate.OTP()
                try:
                    msg = Message('SSRL password recovery', sender = 'smartsystemlaboratory@gmail.com', recipients = [email])
                    msg.body = f"Enter the OTP below into the requested field \nThe OTP will expire in 24 hours\n\nOTP: {otp}  \n\n\nFrom SSRL Team"
                    
                    mail.send(msg)
                    
                    session["uid"]=uid
                    session["otp"]=otp
                    flash("Check your email for the OTP","info")
                    return render_template('forms/confirm_otp.html')
                    
                except:
                    flash("Unable to recover your account at the moment! Please confirm that the inputed email is correct or check your internet connection.", "danger")
                    return redirect(url_for('forgot_password'))
            else:
                flash("Please confirm that the inputed email is correct!", "danger")
                return redirect(url_for('forgot_password'))
    elif status == "true":
        return redirect(url_for('forgot_password'))
    
    else:
        flash("Please confirm that the inputed ID is correct!", "danger")
        return redirect(url_for('forgot_password'))
    

@app.post('/confirm/otp')
def confirm_otp():
    status = session["confirmed"]
    
    if status == "false":
        input = request.form.get("otp")
        otp = session["otp"]
        if input==otp:
            session.pop("otp",None)
            session["confirmed"] = "true"
            return render_template('forms/change_password.html')
        else:
            flash("Invalid OTP!", "danger")
            return render_template('forms/confirm_otp,html')
    elif status == "true":
        return redirect(url_for('forgot_password'))

@app.post('/change/password')
def change_password():
        
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")
        
        
        if new_pwd == confirm_pwd:
            uid = session["uid"]
            hashed_pwd = generate_password_hash(new_pwd)
            dtls = updatePwd(hashed_pwd)
            updated = User_db.update_user_profile(uid, dtls)
            
            if updated:
                user_profile = User_db.get_user_by_uid(uid)
                session["user_uid"] = uid
                session["user_id"] = str(user_profile["_id"])
                session["user_role"] = user_profile["role"]
                session["stack"] = user_profile["stack"]
                fullname = user_profile["fullname"]
                session.pop("uid", None)
                flash(f"Password changed successfully! Welcome back {fullname}", "success")
                return redirect(url_for('home'))
            else:
                flash("Unable to change your password! Try again", "danger")
                return render_template('forms/change_password.html')
        else:
            flash("Unmatching password input! Unable to update your password", "danger")
            return render_template('forms/change_password.html')

@app.post('/Admin/create/user')
def create_user():
    
    # if "user_id" in session:
    #     user_role = session["user_role"]
        
    #     if user_role == "Admin":
        
            firstname = "Folashade"
            surname = "Dahunsi"
            fullname = "{0} {1}".format(surname, firstname)
            pwd = generate.password()
            hashed_pwd = generate_password_hash(pwd)
            uid = generate.user_id(firstname)
            app.logger.info(uid)
            app.logger.info(pwd)
            stack = ""
            niche =""
            role = "Admin"
            phone_num = "NIL"
            email = "faluyiisaiah@gmail.com"
            mentor_id = "NIL"
            avatar = "https://res.cloudinary.com/diaownipw/image/upload/v1687873502/smart_app/avatars/zeaqhw6su6xkchl1o4im.svg"
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
                
                user_id = User_db.create_user(usr)
                
                flash(f"user {uid} created successfully","success")
                return redirect(url_for('show_user_profile', requested_id=user_id ))
            except:
                flash("Unable to create user at the moment! Please confirm that the inputed email is correct or check your internet connection.", "danger")
                return redirect(url_for('home'))
                
    #     else:
    #         flash('permission not granted', "danger")
    #         return redirect(url_for('login'))            
    # else:
    #     flash  ('you are not logged in!', "danger")
    #     return redirect(url_for('login'))

            
@app.post('/user/authenticate')
def authenticate_user():
    user_uid = request.form.get("user_id")
    pwd = request.form.get("pwd")
    user_profile = User_db.get_user_by_uid(user_uid)
    
    
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

        
    
@app.get('/home/me')
def home():
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        todos = list(Todos_db.get_todos_by_user_id_limited(user_id))
        all_todos = list(Todos_db.get_todos_by_user_id(user_id))
        
        now = datetime.now().strftime
        
        if now("%p") == "AM":
            meridian = "morning"
            
        elif int(now("%H")) >= int(12) and int(now("%H")) < int(16):
            meridian = "afternoon"
        
        else:
            meridian = "evening"  
            
        taskCompleted = 0
        for td in all_todos:
            if td["completed"]==True:
                if (td["date_time"]).strftime("%U")==datetime.now().strftime("%U"):
                        taskCompleted = int(taskCompleted) + 1
                else:
                    continue  
            else:
                continue
            
        date = {
            "day" : now("%A"),
            "month" : now("%B"),
            "date" : now("%d"),
            "meridian" : meridian,
            "taskCompleted": taskCompleted
        }
        
        if user_role=="Admin":
            members = list(User_db.get_all_users_limited())
            reports = list(Report_db.get_by_recipient_limited(position=user_role))
            requests = list(Request_db.get_by_recipient_limited(position=user_role, user_id=user_id))
            projects = list(Project_db.get_by_sender_limited(user_id, uid))
            personnels = list(User_db.get_all_users())

            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members, reports=reports, requests=requests, projects=projects, personnels=personnels, todos=todos)
            
        elif user_role == "Intern":
            reports =list(Report_db.get_by_sender(user_id, uid))
            requests = list(Request_db.get_by_sender(user_id, uid))
            projects = []
            
            project_all = list(Project_db.get_by_recipient_dtls(category="all", recipient=stack, name="All stack members"))
            for project in project_all:
                projects.append(project)
                
            project_one = list(Project_db.get_by_recipient_dtls(category="one", recipient=user_id, name=uid))
            for project in project_one:
                projects.append(project)
                
            projects.sort(reverse=True, key=sortFunc)
                
            members = list(User_db.get_users_by_stack_limited(stack))
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members, reports=reports, requests=requests, projects=projects, todos=todos)
        
        elif user_role == "Lead":
            reports =list(Report_db.get_by_sender(user_id, uid))
            requests = list(Request_db.get_by_sender(user_id, uid))
            projects = list(Project_db.get_by_recipient_dtls(category="one", recipient=user_id, name=uid))
                
            members = list(User_db.get_users_by_stack_limited(stack))
            return render_template("pages/home.html", user_profile=user_profile, date=date, members=members, reports=reports, requests=requests, projects=projects, todos=todos)
        
        else:
            flash("permission not granted!", "danger")
            return redirect(url_for('login'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))



@app.get('/view/members' )
def view_members():
    
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        id = session["user_id"]
        user_profile = User_db.get_user_by_oid(id)
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

@app.get('/show/profile/<requested_id>')
def show_user_profile(requested_id):
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        current_user_id = session["user_id"]
        user_profile = User_db.get_user_by_oid(current_user_id)
        
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
    if "user_id" in session:
        current_user_id = session["user_id"]
        requested_profile = User_db.get_user_by_oid(current_user_id)
        return render_template('pages/view_profile.html', user_profile=requested_profile, current_uid=current_user_id)            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.post('/user/edit/profile')
def user_edit_profile():
    
    if "user_id" in session:
        user_id = session["user_id"]
        avatar = request.files['avatar']
        phone_num = request.form.get("phone_num")
        bio = request.form.get("bio")
        location = request.form.get("location")
        bday = request.form.get("bday")
        if avatar and AllowedExtension.images(secure_filename(avatar.filename)):

            try: 
                uploaded = cloudinary.uploader.upload(avatar, folder="smart_app/avatars", resource_type="image")
            
                app.logger.info(uploaded)
                if "secure_url" in uploaded:
                    filename = uploaded["secure_url"]
                    dtls = updateUser(filename, phone_num, bio, location, bday)
                    
                    updated = User_db.update_user_profile_by_oid(user_id, dtls)
                
                    if updated:
                        flash("profile updated successfully", "success")
                        return redirect(url_for('view_profile_me'))
                    else:
                        flash("profile update unsuccessful!", "danger")
                        return redirect(url_for('view_profile_me'))
                else:
                    flash("image upload error!", "danger")
                    return redirect(url_for('view_profile_me'))
            except:
                flash("Unable to update your profile at the moment! Please make sure you have a strong internet connection", "danger")
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
    if "user_id" in session:
        user_role = session["user_role"]
        user_id = session["user_id"]
        
        if user_role=="Admin" and edit_id == user_id:
                
                firstname = request.form.get("firstname")
                profile = User_db.get_user_by_oid(user_id)
                
                surname = request.form.get("surname")
                fullname = "{0} {1}".format(surname, firstname)
                stack = request.form.get("stack")
                niche = request.form.get("niche")
                role = request.form.get("role")
                avatar = request.files['avatar']
                phone_num = request.form.get("phone_num")
                email = request.form.get("email")
                bio = request.form.get("bio")
                location = request.form.get("location")
                bday = request.form.get("bday")

                if profile["firstname"]==firstname:
                    uid = profile["uid"]
                                        
                    if avatar and AllowedExtension.images(secure_filename(avatar.filename)):
                        try:
                            uploaded = cloudinary.uploader.upload(avatar, folder="smart_app/avatars", resource_type="image")
                            
                            if "secure_url" in uploaded:
                                filename = uploaded["secure_url"]
                                dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                                updated = User_db.update_user_profile_by_oid(user_id, dtls)
                            
                                if updated:
                                    flash("profile updated successfully", "success")
                                    return redirect(url_for('view_profile_me'))
                                else:
                                    flash("profile update unsuccessful!", "danger")
                                    return redirect(url_for('view_profile_me'))
                            else:
                                flash("image upload error!", "danger")
                                return redirect(url_for('view_profile_me'))
                    
                        except:
                            flash("Unable to update your profile at the moment! Please make sure you have a strong internet connection", "danger")
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
                    
                    if avatar and AllowedExtension.images(secure_filename(avatar.filename)):
                        try:
                            uploaded = cloudinary.uploader.upload(avatar, folder="smart_app/avatars", resource_type="image")
                        
                            if "secure_url" in uploaded:
                                filename = uploaded["secure_url"]
                                dtls = updateAdmin(firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday)

                                updated = User_db.update_user_profile_by_oid(user_id, dtls)
                                if updated:
                                    flash("profile updated successfully,", "success")
                                    return redirect(url_for('view_profile_me'))
                                else:
                                    flash("profile update unsuccessful!", "danger")
                                    return redirect(url_for('view_profile_me'))
                            else:
                                flash("image upload error!", "danger")
                                return redirect(url_for('view_profile_me'))
                        
                        except:
                            flash("Unable to update your profile at the moment! Please make sure you have a strong internet connection", "danger")
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
                        flash("profile update undsuccessful!", "danger")
                        return redirect(url_for('view_members'))
                except: 
                    flash("Profile update unsuccessful! Please confirm that the inputed email address is correct and that you are connected to the internet.", "danger")
                    return redirect(url_for('view_members'))
                        
                    
                    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

    


@app.get('/Add/lead/<intern_uid>')
def admin_add_lead(intern_uid):
    if "user_id" in session:
        user_role = session["user_role"]
        
        if user_role == "Admin":
            stack = User_db.get_user_by_uid(intern_uid)["stack"]
            uid = User_db.get_lead(stack)["uid"]
            
            dtls = {
                "role": "Intern"
            }
            updated = User_db.update_user_role(uid, dtls)
            
            if updated:
                dtls = {
                    "role": "Lead"
                }
                updated = User_db.update_user_role(intern_uid, dtls)
            
                if updated:
                    flash(f"You've successfully made {intern_uid} the {stack} Lead", "success")
                    return redirect(url_for('view_members'))
                else:
                    flash("profile update unsuccessful!", "danger")
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
    
    if "user_id" in session:
        user_role = session["user_role"]
        
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
    



@app.get('/view/equipments')
def view_all_eqpt():
    
    if "user_id" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            equipments = list(Eqpt_db.get_all_eqpt())
            personnels = User_db.get_all_users()
            lost_eqpts = lost_eqpt_db.get_all()
            availables = Eqpt_db.get_all_available_eqpt()
            inventory = list(Inventory_db.get_all())
            
            return render_template('pages/equipments.html', user_profile=user_profile, equipments=equipments, lost_eqpts=lost_eqpts, personnels=personnels, availables=availables, inventory=inventory)

        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/equipments/<eqpt_id>')        
def view_eqpt_dtls(eqpt_id):
    
    if "user_uid" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
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
   
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
    
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
         
            Name = request.form.get("name")
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
            date_inserted = now("%x")
        
            dtls = Eqpt(Name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
            
            eqpt_id = Eqpt_db.new_input(dtls)
            if eqpt_id:
                name = {
                    "name": Name,
                    "id": eqpt_id
                }
                dtls = Eqpt(Name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
                Inventory_db.insert_new(dtls)
            
                flash (f"Equipment {name} inputed successfully!", "success")
                return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
            else:
                flash('An error occured!try again', 'danger')
                return redirect(url_for('view_all_eqpt'))
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/equipment/existing/input')
def eqpt_existing_input():
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
         
            eqpt_id = request.form.get("eqpt_id")
            added_quantity = request.form.get("quantity")
            eqpt = Eqpt_db.get_eqpt_by_id(eqpt_id)
            name = {
                "name": eqpt["name"],
                "id" : eqpt_id
                
            }
            existing_quantity = eqpt["quantity"]
            quantity = int(added_quantity) + int(existing_quantity)
            description = eqpt["description"]
            date_of_arrival = request.form.get("arrival")
            type = eqpt["type"]
            status = "available"
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            datetime_inputed = "{0} {1}, {2}".format(month, date, year)
            date_inserted = now("%x")
        
            dtls = existEqpt(quantity, datetime_inputed, status)
            
            updated = Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            
            if updated:
                dtls = Eqpt(name, added_quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
                Inventory_db.insert_new(dtls)
                flash (f"Equipment inputed successfully!", "success")
                return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
            else:
                flash('An error occured!try again', 'danger')
                return redirect(url_for('view_all_eqpt'))
                
        else:
            flash('permission not granted', "danger")
            return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    

    
@app.post('/equipment/update/<eqpt_id>')
def update_eqpt_dtls(eqpt_id):
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
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
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
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
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
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
            lost_id = lost_eqpt_db.new_input(dtls)
            
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
            return redirect(url_for('view_lost_eqpt_dtls', eqpt_id=lost_id))
            
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))            
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))   
    
@app.get('/view/lost/equipment/<eqpt_id>')        
def view_lost_eqpt_dtls(eqpt_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
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
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
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

    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
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
    
    if "user_id" in session:
        user_id = session["user_id"]
        
        eqpts = Eqpt_db.get_all_eqpt()
        user_profile = User_db.get_user_by_oid(user_id)
        return render_template('forms/request_form.html', eqpts=eqpts, user_profile=user_profile)
    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
    
@app.get('/all/submissions')
def all_submissions():
    
    if "user_id" in session:
        role = session["user_role"]
        _id = session["user_id"]
        uid = session["user_uid"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(_id)
        eqpts = Eqpt_db.get_all_available_eqpt()
        
        if role == "Intern":
            reports =list(Report_db.get_by_sender(_id, uid))
            requests = list(Request_db.get_by_sender(_id, uid))
            projects = []
            
            project_all = list(Project_db.get_by_recipient_dtls(category="all", recipient=stack, name="All stack members"))
            for project in project_all:
                projects.append(project)
                
            project_one = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
            for project in project_one:
                projects.append(project)
                
            projects.sort(reverse=True, key=sortFunc)
            
            for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
            for x in requests:
                date_time = x["date_time"].strftime("%j")
                diff = int(datetime.now().strftime("%j")) - int(date_time)
                
                if diff == 0:
                    date_time_H = x["date_time"].strftime("%H")
                    diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                    if diff_H == 0:
                        date_time_M = x["date_time"].strftime("%M")
                        diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                        if diff_M == 0:
                            x["date_submitted"] = "now"
                        else:
                            x["date_submitted"] = f"{diff_M} minutes ago"
                    elif diff_H > 0:
                        x["date_submitted"] = f"{diff_H} hours ago"
                        
                elif diff==1:
                    x["date_submitted"] = "yesterday"
                    
            for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
            return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
        
        elif role == "Lead":
            if stack == "Software":
                reports =list(Report_db.get_by_sender(_id, uid))
                requests = list(Request_db.get_by_sender(_id, uid))
                projects = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                    
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
            
            else:
                reports =list(Report_db.get_by_sender(_id, uid))
                requests = list(Request_db.get_by_sender(_id, uid))
                projects = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                        
                    
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.get('/submissions/interns')
def intern_submissions():
    
    if "user_id" in session:
        role = session["user_role"]
        _id = session["user_id"]
        uid = session["user_uid"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(_id)
        eqpts = Eqpt_db.get_all_available_eqpt()
        
        if role == "Lead":
            if stack == "Software":
                position = "Software"
                reports =  list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                projects = list(Project_db.get_by_sender(_id, uid))
                personnels = list(User_db.get_users_by_stack(stack))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_created"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels)
            else:
                position = "Hardware"
                reports = list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                projects = list(Project_db.get_by_sender(_id, uid))
                personnels = list(User_db.get_users_by_stack(stack))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_created"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"


                return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels)
        
        elif role == "Admin":
            position = "Admin"
            reports = list(Report_db.get_by_recipient(position))
            requests = list(Request_db.get_by_recipient(position, _id))
            projects = list(Project_db.get_by_sender(_id, uid))
            personnels = list(User_db.get_all_users())
            
            for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
            for x in requests:
                date_time = x["date_time"].strftime("%j")
                diff = int(datetime.now().strftime("%j")) - int(date_time)
                
                if diff == 0:
                    date_time_H = x["date_time"].strftime("%H")
                    diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                    if diff_H == 0:
                        date_time_M = x["date_time"].strftime("%M")
                        diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                        if diff_M == 0:
                            x["date_submitted"] = "now"
                        else:
                            x["date_submitted"] = f"{diff_M} minutes ago"
                    elif diff_H > 0:
                        x["date_submitted"] = f"{diff_H} hours ago"
                        
                elif diff==1:
                    x["date_submitted"] = "yesterday"
            
            for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
            return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, personnels=personnels, eqpts=eqpts)
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.post('/submissions/submit/request_form')
def post_request_form():
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
        title = request.form.get("title")
        type = request.form.get("type")
        eqpt_id = request.form.get("eqpt_id")
        
        if type =="Equipment":
            eqpt = {
                "id": eqpt_id,
                "name": Eqpt_db.get_eqpt_by_id(eqpt_id)["name"] 
            }
        else:
            eqpt = "None"
            
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
        date_time = datetime.now()
        
        if recipient == "Admin":
            role = "Admin"
            id = User_db.get_user_by_role_one(role)["_id"]
            
            recipient_dtls = {
                "position": "Admin",
                "id": id
            }
            requested = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            request_id = Request_db.insert_new(requested)
            
            flash("Request submitted successfully!", "success")
            return redirect(url_for('view_request', request_id=request_id))
        
        elif recipient == "software":
            stack = "Software"
            id = User_db.get_lead(stack)["_id"]
             
            recipient_dtls = {
                "position": "Software",
                "id": id
            }
            requested = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            request_id = Request_db.insert_new(requested)
            
            flash("Request submitted successfully!", "success")
            return redirect(url_for('view_request', request_id=request_id))
        
        elif recipient == "hardware":
            stack="Hardware" 
            id = User_db.get_lead(stack)["_id"]
            recipient_dtls = {
                "position": "Hardware",
                "id": id
            }
        
            requested = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            request_id = Request_db.insert_new(requested)
            
            flash("Request submitted successfully!", "success")
            return redirect(url_for('view_request', request_id=request_id))
        
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/view/request/<request_id>')
def view_request(request_id):
    
    if "user_id" in session:
        id = session["user_id"]
        
        user_profile = User_db.get_user_by_oid(id)
        request = Request_db.get_by_request_id(request_id)
        eqpts = Eqpt_db.get_all_available_eqpt()
    
        return render_template('pages/view_request.html', request=request, user_profile=user_profile, eqpts=eqpts)
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/request/approve/<request_id>')
def approve_request(request_id):
    
    if "user_id" in session:
        approved = Request_db.approve_request(request_id)

        if approved: 
            flash('Request approved',"success")
            return redirect(url_for('view_request', request_id=request_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_request', request_id=request_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/request/decline/<request_id>')
def decline_request(request_id):
    
    if "user_id" in session:
        declined = Request_db.decline_request(request_id)

        if declined: 
            flash('Request declined',"success")
            return redirect(url_for('view_request', request_id=request_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_request', request_id=request_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 

@app.post('/request/edit/<request_id>')
def edit_request(request_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
        title = request.form.get("title")
        type = request.form.get("type")
        eqpt_id = request.form.get("eqpt_id")
        
        if type == "Equipment":
            eqpt = {
                "id": eqpt_id,
                "name": Eqpt_db.get_eqpt_by_id(eqpt_id)["name"] 
            }
        else:
            eqpt = "None"
            
            
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
        date_time = datetime.now()
        
        if recipient == "Admin":
            role = "Admin"
            id = User_db.get_user_by_role_one(role)["_id"]
            
            recipient_dtls = {
                "position": "Admin",
                "id": id
            }
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)
            
            if updated:
                flash("Request edited successfully!", "success")
                return redirect(url_for('view_request', request_id=request_id))
            else:
                flash('An error occurred! Try again', "danger")
                return redirect(url_for('view_request', request_id=request_id))

        elif recipient == "software":
            stack = "Software"
            id = User_db.get_lead(stack)["_id"]
            
            recipient_dtls = {
                "position": "Software",
                "id": id
            }
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)
            if updated:
                flash("Request edited successfully!", "success")
                return redirect(url_for('view_request', request_id=request_id))
            else:
                flash('An error occurred! Try again', "danger")
                return redirect(url_for('view_request', request_id=request_id))

        elif recipient == "hardware":
            stack="Hardware" 
            id = User_db.get_lead(stack)["_id"]
            recipient_dtls = {
                "position": "Hardware",
                "id": id
            }
        
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)

            if updated:
                flash("Request edited successfully!", "success")
                return redirect(url_for('view_request', request_id=request_id))
            else:
                flash('An error occurred! Try again', "danger")
                return redirect(url_for('view_request', request_id=request_id))
            
        else:
                flash('permission not granted', "danger")
                return redirect(url_for('login'))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/delete/request/<request_id>')
def delete_request(request_id):
    
    if "user_id" in session:
            
            deleted = Request_db.delete_request(request_id)
            
            if deleted:
                flash ("Request deleted successfully!", "success")
                return redirect(url_for('all_submissions'))
            else:
                flash ('The request was unsuccessful!', "danger")
                return redirect(url_for('view_request', request_id=request_id))
                  
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
  
        

@app.post('/submissions/submit/report')
def post_report_form():
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
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
        status = "Submitted"
        date_time = datetime.now()
        
        report = Report(title, report_no, content, recipient, sender, date_submitted, status, date_time)
        report_id = Report_db.insert_new(report)
        
        flash("Report submitted successfully!", "success")
        return redirect(url_for('view_report', report_id=report_id))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.get('/view/report/<report_id>')
def view_report(report_id):   
     
    if "user_id" in session:
        id = session["user_id"]
        
        user_profile = User_db.get_user_by_oid(id)
        report = Report_db.get_by_report_id(report_id)
    
        return render_template('pages/view_report.html', report=report, user_profile=user_profile)
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/report/completed/<report_id>')
def mark_report_completed(report_id):
    
    if "user_id" in session:
        marked = Report_db.mark_completed(report_id)

        if marked: 
            flash('Report marked completed',"success")
            return redirect(url_for('view_report', report_id=report_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_report', report_id=report_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/report/incomplete/<report_id>')
def mark_report_incomplete(report_id):
    
    if "user_id" in session:
        marked = Report_db.mark_incomplete(report_id)

        if marked: 
            flash('Report marked incomplete',"success")
            return redirect(url_for('view_report', report_id=report_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_report', report_id=report_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/report/feedback/<report_id>') 
def report_feedback(report_id):
    
    if "user_id" in session:
        feedback = {"feedback": request.form.get("feedback")}
        submitted = Report_db.report_feedback(report_id, feedback)
        
        if submitted: 
            flash('Feedback sent successfully',"success")
            return redirect(url_for('view_report', report_id=report_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_report', report_id=report_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/report/edit/<report_id>')
def edit_report(report_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
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
        status = "Submitted"
        date_time = datetime.now()
        
        dtls = Report(title, report_no, content, recipient, sender, date_submitted, status, date_time)
        updated = Report_db.update_report_dtls(report_id, dtls)
        
        if updated:
            flash("Report edited successfully!", "success")
            return redirect(url_for('view_report', report_id=report_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_report', report_id=report_id))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 

@app.get('/delete/report/<report_id>')
def delete_report(report_id):
    
    if "user_id" in session:
            
            deleted = Report_db.delete_report(report_id)
            
            if deleted:
                flash ("Report deleted successfully!", "success")
                return redirect(url_for('all_submissions'))
            else:
                flash ('The request was unsuccessful!', "danger")
                return redirect(url_for('view_report', report_id=report_id))
                  
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.post('/submissions/create/projects')
def post_project_form():
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
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
        date_created = "{0} {1}, {2}".format(month, date, year)
        deadline_str = request.form.get("deadline")
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        date_time = datetime.now()
        
        if recipient=="Software" or recipient=="Hardware":
            recipient_dtls = {
                "category":"all",
                "recipient": recipient,
                "name": "All stack members"
            }
        else:
            recipient_dtls = {
                "category":"one",
                "recipient": str(recipient),
                "name": User_db.get_user_by_oid(recipient)["uid"]
            }
        
        project = Project(topic, focus, objectives, recipient_dtls, sender, date_created, deadline, date_time)
        project_id = Project_db.insert_new(project)
        
        flash("Project created successfully!", "success")
        return redirect(url_for('view_project', project_id=project_id))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.get('/view/project/<project_id>')
def view_project(project_id):
    
    if "user_id" in session:
        id = session["user_id"]
        role = session["user_role"]
        stack = session["stack"]
        
        user_profile = User_db.get_user_by_oid(id)
        project = Project_db.get_by_project_id(project_id)
        completed = int(0)
        
        if "submissions" in project:
            for x in project["submissions"]:
                if x["id"]==id and x["status"]=="Completed":
                    completed = completed + 1
                    break
        if completed > 0:
            display = "None"
        else:
            display = "block"
           
                
        if role=="Admin":
            personnels = User_db.get_all_users()
            return render_template('pages/view_project.html', project=project, user_profile=user_profile, personnels=personnels, id=id)
        
        elif role=="Lead":
            personnels = User_db.get_users_by_stack(stack)
            return render_template('pages/view_project.html', project=project, user_profile=user_profile, personnels=personnels, id=id, display=display)
        else:
            return render_template('pages/view_project.html', project=project, user_profile=user_profile, id=id, display=display)
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/project/completed/<project_id>/<id>')
def mark_project_completed(project_id, id):
    
    if "user_id" in session:
        project = Project_db.get_by_project_id(project_id)["submissions"]
        for x in project:
            if x["id"]==id:
                x["status"] = "Completed"
                project[project.index(x)] = x
                break
        marked = Project_db.mark_project(project_id, project)
    

        if marked: 
            flash('Project marked completed',"success")
            return redirect(url_for('project_submissions', project_id=project_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('project_submissions', project_id=project_id))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/project/incomplete/<project_id>/<id>') 
def mark_project_incomplete(project_id, id):
    
    if "user_id" in session:
        project = Project_db.get_by_project_id(project_id)["submissions"]
        for x in project:
            if x["id"]==id:
                x["status"] = "Incomplete"
                project[project.index(x)] = x
                break
        marked = Project_db.mark_project(project_id, project)
    

        if marked: 
            flash('Project marked incomplete',"success")
            return redirect(url_for('project_submissions', project_id=project_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('project_submissions', project_id=project_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.post('/project/edit/<project_id>')
def edit_project(project_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
        topic = request.form.get("topic")
        focus = request.form.get("focus")
        objectives = request.form.get("objectives")
        recipient = request.form.get("recipient")
        deadline_str = request.form.get("deadline")
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        date_time = datetime.now()
        
        sender = {
            "_id": user_id,
            "uid": uid  
                  
        }
        now = datetime.now().strftime
        month = now("%B")
        date = now("%d")
        year = now("%Y")
        date_submitted = "{0} {1}, {2}".format(month, date, year)
        
        if recipient=="Software" or recipient=="Hardware":
            recipient_dtls = {
                "category":"all",
                "recipient": recipient,
                "name": "All stack members"
            }
        else:
            recipient_dtls = {
                "category":"one",
                "recipient": str(recipient),
                "name": User_db.get_user_by_oid(recipient)["uid"]
            }
        
        dtls = Project(topic, focus, objectives, recipient_dtls, sender, date_submitted, deadline, date_time)
        updated = Project_db.update_project_dtls(project_id, dtls)
        
        if updated:
            flash("Project details edited successfully!", "success")
            return redirect(url_for('view_project', project_id=project_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('view_project', project_id=project_id))

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login')) 
    
@app.get('/delete/project/<project_id>')
def delete_project(project_id):
    
    if "user_id" in session:
            
            deleted = Project_db.delete_project(project_id)
            
            if deleted:
                flash ("Project deleted successfully!", "success")
                return redirect(url_for('intern_submissions'))
            else:
                flash ('The request was unsuccessful!', "danger")
                return redirect(url_for('view_project', project_id=project_id))
                  
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

    
@app.post('/project/submit/<project_id>')
def submit_project(project_id):
    
    
    if "user_id" in session:
        uid = session["user_uid"]
        id = session["user_id"]
        project = request.files["file"]
        filename = secure_filename(project.filename)
        
        if project and AllowedExtension.files(filename):
            
            try:
                uploaded = cloudinary.uploader.upload(project, folder="smart_app/projects", resource_type="raw")

                if "secure_url" in uploaded:
                    filepath = uploaded["secure_url"]
            
                
                    if "submissions" in Project_db.get_by_project_id(project_id):
                        submitted = Project_db.get_by_project_id(project_id)["submissions"]
                        now = datetime.now().strftime
                        month = now("%B")
                        date = now("%d")
                        year = now("%Y")
                        date_submitted = "{0} {1}, {2}".format(month, date, year)
                        
                        for x in submitted:
                            if x["id"]==id:
                                submitted.remove(x)
                                break
                        submitted.append({
                            "id": id,
                            "uid": uid,
                            "project_id": project_id,
                            "file_name": filename,
                            "file_path": filepath,
                            "status": "submitted",
                            "date_submitted": date_submitted,
                            "datetime": datetime.now()
                        })
                        no_submissions = len(submitted)
                        uploaded = Project_db.submit_project(project_id, submitted, no_submissions)

                        if uploaded:
                            flash('Project submitted successfully',"success")
                            return redirect(url_for('view_project', project_id=project_id))
                        else:
                            flash('An error occurred! Try again', "danger")
                            return redirect(url_for('view_project', project_id=project_id))
                    else:
                        now = datetime.now().strftime
                        month = now("%B")
                        date = now("%d")
                        year = now("%Y")
                        date_submitted = "{0} {1}, {2}".format(month, date, year)
                        project_submitted = [{
                            "id": id,
                            "uid": uid,
                            "project_id": project_id,
                            "file_name": filename,
                            "file_path": filepath,
                            "status": "submitted",
                            "date_submitted": date_submitted,
                            "datetime": datetime.now()  
                        }]
                        no_submissions = int(1)
                        
                        uploaded = Project_db.submit_project(project_id, project_submitted, no_submissions)

                        if uploaded: 
                            flash('Project submitted successfully',"success")
                            return redirect(url_for('view_project', project_id=project_id))
                        else:
                            flash('An error occurred! Try again', "danger")
                            return redirect(url_for('view_project', project_id=project_id))
            except:
                flash("Couldn't upload your project at the moment! Please make sure you have a strong internet connection.", "danger")
                return redirect(url_for('view_project', project_id=project_id))
            
            else:
                flash('file upload error!', "danger")
                return redirect(url_for('view_project', project_id=project_id))
        
        else:
            flash('Invalid file format! Try again', "danger")
            return redirect(url_for('view_project', project_id=project_id))
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.get('/project/submissions/<project_id>')
def project_submissions(project_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        user_profile = User_db.get_user_by_oid(user_id)
        if "submissions" in Project_db.get_by_project_id(project_id):
            submissions = Project_db.get_by_project_id(project_id)["submissions"]
            topic = Project_db.get_by_project_id(project_id)["topic"]

            
            return render_template('pages/project_submissions.html', details=submissions, user_profile=user_profile, topic=topic)
        else:
            flash('No submissions made yet', "info")
            return redirect(url_for('view_project', project_id=project_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.get('/project/submissions/download/<project_id>/<id>')
def download_project_submissions(project_id, id):
    #user_id = session["user_id"]
    #user_profile = User_db.get_user_by_oid(user_id)
    
    if "user_id" in session:

        submissions = Project_db.get_by_project_id(project_id)["submissions"]
        app.logger.info(submissions)
        
        for x in submissions:
            if x["id"]==id:
                upload = x
                break
        file_url = upload["file_path"]
        file_name = upload["file_name"]
        app.logger.info(file_url)
        
        return send_file(urllib.request.urlopen(file_url), download_name=file_name, as_attachment=True)

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.get('/project/send/feedback/<project_id>/<id>')
def send_feedback(project_id, id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        user_profile = User_db.get_user_by_oid(user_id)
        project = Project_db.get_by_project_id(project_id)
        submissions = project["submissions"]
        
        for x in submissions:
            if x["id"]==id:
                submission=x
                break
        
        return render_template('pages/send_feedback.html', user_profile=user_profile, project=project, submission=submission)

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/submit/feedback/<project_id>/<id>') 
def submit_feedback(project_id, id):
    
    if "user_id" in session:
        submissions = Project_db.get_by_project_id(project_id)["submissions"]
        
        for  x in submissions:
            if x["id"]==id:
                x["feedback"] = request.form.get("feedback")
                
        submitted = Project_db.mark_project(project_id, submissions)
    

        if submitted: 
            flash('Feedback sent successfully',"success")
            return redirect(url_for('project_submissions', project_id=project_id))
        else:
            flash('An error occurred! Try again', "danger")
            return redirect(url_for('project_submissions', project_id=project_id))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))
    
@app.post('/todo/create') 
def create_todo():
    
    if "user_id" in session:
        user_id = session["user_id"]
        description = request.get_json()['description']
        
        dtls = {
            "uid": user_id,
            "description": description,
            "date_time": datetime.now(),
            "completed": False
        }
        id = str(Todos_db.create_todo(dtls))
        
        return jsonify({
            'description': description,
            'id' : id
        })
    
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.get('/todo/delete/<todo_id>')
def delete_todo(todo_id):    
    if "user_id" in session:        
        deleted = Todos_db.delete_todo(todo_id)
        
        if deleted:
            return jsonify({
                'description':"deleted"
            })
        else:
            flash  ('An error occured!', "danger")
            return redirect(url_for('home'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

@app.post('/todo/<todo_id>/set-completed')
def mark_completed(todo_id):    
    
    if "user_id" in session:   
        user_id = session["user_id"]
        
        status = request.get_json()['completed']
        dtls = {
            "completed": status
        }     
        marked = Todos_db.update_todo(todo_id, dtls)
        todo = Todos_db.get_specific_todo(user_id, todo_id)
        if marked:
            return jsonify({
                'id': todo_id,
                'description': todo["description"],
                'completed':status  
            })
        else:
            flash  ('An error occured!', "danger")
            return redirect(url_for('home'))
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.post('/todos/filter')
def task_filter():
    
    if "user_id" in session:
        user_id = session["user_id"]
        
        option = request.get_json()['filter']
        todos = list(Todos_db.get_todos_by_user_id(user_id))
        app.logger.info(option)
        
        taskCompleted = 0
        if option == "week":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%U")==datetime.now().strftime("%U"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            
            return jsonify({ 'taskCompleted': taskCompleted})
        
        elif option == "month":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%m")==datetime.now().strftime("%m"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            return jsonify({ 'taskCompleted': taskCompleted})
            
                
        elif option == "year":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%Y")==datetime.now().strftime("%Y"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            return jsonify({ 'taskCompleted': taskCompleted})
            
             
        
    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))


@app.get('/all/todos')
def all_todos():
    if "user_id" in session:
        user_id = session["user_id"]
        user_profile = User_db.get_user_by_oid(user_id)
        all_todos = list(Todos_db.get_todos_by_user_id(user_id))
        
        return render_template('pages/all_todos.html', all_todos=all_todos, user_profile=user_profile)

    else:
        flash  ('you are not logged in!', "danger")
        return redirect(url_for('login'))

if __name__=="__main__":
    app.run(debug=True)