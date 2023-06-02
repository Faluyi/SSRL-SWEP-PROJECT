from pymongo import MongoClient
from bson.objectid import ObjectId 
import string, random

client = MongoClient('mongodb://localhost:27017/')
db = client['SSRL_DB']
Users = db['Users']
Tasks = db['Tasks']
Eqpts = db['Equipments']
lost_eqpts = db["Lost_eqpt"]
Requests = db["Requests"]
Reports = db["Reports"]
Projects = db["projects"]

class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, usr):
        return self.collection.insert_one(usr.__dict__)
        
        
    def get_user_by_role(self, role):
        return self.collection.find({"role": role})
    
    def get_user_by_uid(self, user_uid):
        return self.collection.find_one({"uid": user_uid})
    
    def get_user_by_oid(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def update_user_profile(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls.__dict__}).modified_count>0
    
    def update_user_role(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls}).modified_count>0
    
    def update_user_profile_by_oid(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_user(self, _id):
        return self.collection.delete_one({"_id":ObjectId(_id)}).deleted_count>0
    
    def get_all_users(self):
        return self.collection.find()
    
    def get_all_users_limited(self):
        return self.collection.find().limit(4)
    
    def get_lead(self, stack):
        return self.collection.find_one({"role":"Lead", "stack":stack})
    
    def get_users_by_stack(self, stack):
        return self.collection.find({"stack":stack})
    
    def get_users_by_stack_limited(self, stack):
        return self.collection.find({"stack":stack}).limit(4)
    
    
class Task_db:
    def __init__(self) -> None:
        self.collection = Tasks
        
    def create_task(self, **kwargs):
        return self.collection.insert_one(kwargs.__dict__)
    
    def update_task(self, **kwargs):
        return self.collection.update_one({"_id":kwargs["task_id"]},{"$set":kwargs.__dict__}).modified_count>0

    def delete_task(self, task_id):
        return self.collection.delete_one({"_id":task_id}).deleted_count>0
    
    def get_tasks_by_stack(self, user_stack):
        return self.collection.find({"stack":user_stack})
    
    def get_task_by_task_id(self, task_id):
        return self.collection.find_one({"_id":task_id})
    
    def get_all_tasks(self):
        return self.collection.find()
    
    
class Eqptdb:
    def __init__(self) -> None:
        self.collection = Eqpts
    
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__)
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0

    def delete_existing_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def get_all_eqpt(self):
        return self.collection.find()
    
    def get_all_available_eqpt(self):
        return self.collection.find({"status":"available"})
    
    
class lost_eqptdb:
    def __init__(self) -> None:
        self.collection = lost_eqpts
        
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__)

    def get_all(self):
        return self.collection.find()
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_lost_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    
class Requestdb:
    def __init__(self) -> None:
        self.collection = Requests
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__)  
    
    def get_all(self):
        return self.collection.find()
    
    def get_by_request_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}})
    
    def get_by_recipient(self, position, _id):
        return self.collection.find({"recipient":{"position":position, "id":ObjectId(_id)}})
    
    def delete_request(self, request_id):
        return self.collection.delete_one({"_id":ObjectId(request_id)}).deleted_count>0
    
class Reportdb:
    def __init__(self) -> None:
        self.collection = Reports
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__)  
    
    def get_all(self):
        return self.collection.find()
    
    def get_by_request_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}})
    
    def get_by_recipient(self, position):
        return self.collection.find({"recipient":position})

    
class Projectdb:
    def __init__(self) -> None:
        self.collection = Projects
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__)   
    
    def get_all(self):
        return self.collection.find()
    
    def get_by_request_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}})
    
    def get_by_recipient(self, position, _id):
        return self.collection.find({"recipient":{"position":position, "id":ObjectId(_id)}})
    
    def get_by_choice_recipient(self, stack):
        return self.collection.find({"stack": stack})
    
     

    
    
class generate:   
    def password():
        password_length = int(12)
        characters = string.ascii_letters + string.digits
        password = ""   
        for index in range(password_length):
            password = password + random.choice(characters)
            
        return password

    def user_id(firstname):
        max = int(3)
        digits = string.digits
        #while 1:
            
        _id = firstname + "SSRL"
        
        for index in range(max):
            _id = _id + random.choice(digits)
            
            # if Users.find_one({"pwd":_id}) == "None": 
            #     break
            
        return _id 
    
class User:
    def __init__(self, firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self. hashed_pwd = hashed_pwd
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.mentor_id = mentor_id
        self.avatar = avatar
        self.task_id = task_id   
        self.datetime_created = datetime_created
        self.bio = bio
        self.location = location
        self.bday = bday

class Eqpt:
    def __init__(self, name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_updated) -> None:
        self.name = name
        self.quantity = quantity
        self.description = description
        self.date_of_arrival = date_of_arrival
        self.type = type
        self.status = status
        self.datetime_inputed = datetime_inputed
        self.date_updated = date_updated

class lostEqpt:
    def __init__(self, eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited) -> None:
        self.eqpt_id = eqpt_id
        self.name = name
        self.type = type
        self.quantity = quantity
        self.personnel_id = personnel_id
        self.status = status
        self.date_reported = date_reported
        self.date_edited = date_edited

class updateUser:
    def __init__(self, filename, phone_num, bio, location, bday) -> None:
        self.avatar = filename
        self.phone_num = phone_num
        self.bio = bio
        self.location = location
        self.bday = bday
        
class updateAdmin:
    def __init__(self, firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.avatar = filename 
        self.bio = bio
        self.location = location
        self.bday = bday

class AdminUpdateUser:
    def __init__(self, firstname, surname, fullname, uid, stack, niche, role) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        
class Request:
    def __init__(self, title, type, eqpt_id, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted) -> None:
        self.title = title
        self.type = type
        self.eqpt_id = eqpt_id
        self.quantity = quantity
        self.date_from = date_from
        self.date_to = date_to
        self.purpose = purpose
        self.sender = sender
        self.recipient = recipient_dtls
        self.status = status
        self.date_submitted = date_submitted
        
class Project:
    def __init__(self, topic, focus, objectives, recipient, sender, date_submitted) -> None:
        self.topic = topic
        self.focus = focus
        self.objectives = objectives
        self.recipient = recipient
        self.sender = sender
        self.date_submitted = date_submitted
        
class Report:
    def __init__(self, title, report_no, content, recipient, sender, date_submitted) -> None:
        self.title = title
        self.report_no = report_no
        self.content = content
        self.recipient = recipient
        self.sender = sender
        self.date_submitted = date_submitted
        
class Available:
    def __init__(self, _quantity, _status) -> None:
        self.status = _status
        self.quantity = _quantity
    
class updateEmail:
    def __init__(self, new_email) -> None:
        self.email = new_email
        
class updatePwd:
    def __init__(self, hashed_pwd) -> None:
        self.hashed_pwd = hashed_pwd



