from pymongo import MongoClient
import string, random

client = MongoClient('mongodb://localhost:27017/')
db = client['SSRL_DB']
Users = db['Users']
Tasks = db['Tasks']
Eqpt = db['Equipments']
lost_eqpt = db["Lost_eqpt"]


class User_db:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, usr):
        return self.collection.insert_one(usr.__dict__)
        
        
    def get_user_by_id(self, user_id):
        return self.collection.find_one({"_id":user_id})
    
    def update_user_profile(self,**kwargs):
        return self.collection.update_one({"_id":kwargs["requested_id"]},{"$set":kwargs.__dict__}).modified_count>0
    
    def delete_user(self, _id):
        return self.collection.delete_one({"_id":_id}).deleted_count>0
    
    def get_all_users(self):
        return self.collection.find()
    
    def get_users_by_stack(self, stack):
        return self.collection.find_one({"stack":stack})
    
    
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
    def __init__(self, firstname, surname, pwd, _id, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created) -> None:
        self.firstname = firstname
        self.surname = surname
        self. pwd = pwd
        self._id = _id
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



def user_view_permission(user_role, current_user_id, requested_id, stack):
    if user_role =="Admin" or current_user_id==requested_id or User_db.get_user_by_id(requested_id)["mentor_id"]==current_user_id or (user_role=="lead" and stack==User_db.get_user_by_id(requested_id)["stack"]):
        return True
    else:
        return False
    
        
    