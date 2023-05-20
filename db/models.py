from pymongo import MongoClient
from bson.objectid import ObjectId 
import string, random

client = MongoClient('mongodb://localhost:27017/')
db = client['SSRL_DB']
Users = db['Users']
Tasks = db['Tasks']
Eqpt = db['Equipments']
lost_eqpt = db["Lost_eqpt"]


class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, usr):
        return self.collection.insert_one(usr.__dict__)
        
        
    def get_user_by_role(self, role):
        return self.collection.find({"role": role})
    
    def get_user_by_uid(self, user_uid):
        return self.collection.find_one({"uid": user_uid})
    
    def update_user_profile(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_user(self, uid):
        return self.collection.delete_one({"uid":uid}).deleted_count>0
    
    def get_all_users(self):
        return self.collection.find()
    
    def get_all_users_limited(self):
        return self.collection.find().limit(4)
    
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
    
    
class Eqpt_db:
    def __init__(self) -> None:
        self.collection = Eqpt
    
    def new_input(self, **kwargs):
        return self.collection.insert_one(kwargs.__dict__)
    
    def update_eqpt_dtls(self, **kwargs):
        return self.collection.update_one({"_id":kwargs["eqpt_id"]},{"$set":kwargs.__dict__}).modified_count>0

    def delete_existing_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":eqpt_id}).deleted_count>0
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find({"_id":eqpt_id})
    
    def get_all_eqpt(self):
        return self.collection.find()
    
    
class lost_eqpt_db:
    def __init__(self) -> None:
        self.collection = lost_eqpt
        
    def new_input(self, **kwargs):
        return self.collection.insert_one(kwargs.__dict__)

    
    
    
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
        _id = firstname + "SSRL"
        while 1:
            for index in range(max):
                _id = _id + random.choice(digits)
            
            if Users.find({"pwd":_id}) is None:
                break
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
        
class updateUser:
    def __init__(self, filename, phone_num, email, bio, location, bday) -> None:
        self.avatar = filename
        self.phone_num = phone_num
        self.email = email
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
        
class updateEmail:
    def __init__(self, new_email) -> None:
        self.email = new_email
        
class updatePwd:
    def __init__(self, hashed_pwd) -> None:
        self.hashed_pwd = hashed_pwd


def user_view_permission(user_role, current_user_id, requested_id, stack):
    if user_role =="Admin" or current_user_id==requested_id or Userdb.get_user_by_id(requested_id)["mentor_id"]==current_user_id or (user_role=="lead" and stack==User_db.get_user_by_uid(requested_id)["stack"]):
        return True
    else:
        return False
    
        