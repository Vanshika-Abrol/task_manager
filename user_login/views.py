from django.shortcuts import render
from mongoops import mongo_initializer
import json
from pytz import timezone
import re
from bson import ObjectId
from datetime import datetime
import os
from emailsoops import send_mail
# Create your views here.
from django.http import HttpResponse , JsonResponse

client = mongo_initializer()
db = client["TASK_DB"]

def signup(request):
    data = json.loads(request.body)

    user_collection = db["users"]
    user = user_collection.find_one({"email":data["email"]})
    if user is None:
        if "domain" in data.keys():
            already_invited = user_collection.find_one({"domain":data["domain"],"email":data["email"], "user_status":"invited"})
            if already_invited is not None:
                user_collection.update_one({"_id":ObjectId(already_invited["_id"])},{"$set":{"user_status":"active","joined_at":datetime.strptime(datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')}})
                data = user_collection.find_one({"_id":ObjectId(already_invited["_id"])})
                data["_id"] = str(data["_id"])
                send_mail(email=data["email"],subject="Welcome to TASK MASTER",message="You can assign tasks.")
                return JsonResponse({"success":True,"data":data})
            else:
               data["user_status"] = "unauthorized"
               data = validation_checks(data)
               if "success" in data.keys():
                   return JsonResponse(data)
               else:
                   ins = user_collection.insert_one(data)
                   data = user_collection.find_one({"_id":ObjectId(ins.inserted_id)})
                   data["_id"] = str(data["_id"])
                   send_mail(email=data["email"],subject="Welcome to TASK MASTER",message="You can assign tasks.")
                   return JsonResponse({"success":True,"data":data}) 
        
        else:
           data["user_role"] = "admin"
           data["user_status"] = "active"
           data = validation_checks(data)
           if "success" in data.keys():
              return JsonResponse(data)
           else:
              ins = user_collection.insert_one(data)
              data = user_collection.find_one({"_id":ObjectId(ins.inserted_id)})
              data["_id"] = str(data["_id"])
              send_mail(email=data["email"],subject="Welcome to TASK MASTER",message="You can assign tasks.")
              return JsonResponse({"success":True,"data":data}) 
    else:
        return JsonResponse({"success":False,"message":"User already exist. Please Login"})

    



def validation_checks(payload):
    user_collection = db["users"]
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    pattern1= r"(0|91)?[6-9][0-9]{9}"
    if not re.match(pattern, payload["email"]):
        return {"success":False,"message":"email is invalid"}
    # existing_user = user_collection.find_one({"email":payload["email"]})
    # if existing_user is not None:
    #     return {"success":False,"message": "user already exist"}
    
    if not re.search(r'[A-Z]',payload["password"]) and re.search(r'\d',payload["password"]):
         return {"success":False,"message":"invalid password"}
    
    if not re.match(pattern1 , payload["mobile"]):
        return {"success":False,"message":"Invalid mobile no."}
   
    # data["user_role"] = "admin"
    # data["user_status"] = "active"
    
    # user_collection.insert_one(data)
    # data["_id"] = str(data["_id"])
    return payload

# def invite_user(request):
#     data = json.loads(request.body)
#     user_collection = db["users"]
#     user = user_collection.find_one({"_id":ObjectId(data["_id"])})
#     if user["user_role"] != "admin":
#         return JsonResponse({"succcess":False,"message":"You have no authorization to perform this action"})
#     else:
#         failed_users=[]
#         already_invited =[]
#         for invited_user in data["users"]:
#             exist_or_not = user_collection.find_one({"email":invited_user["email"],"user_status":"active"})
#             if exist_or_not is not None:
#                 already_invited.append(exist_or_not)
#             pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
#             if re.match(pattern,invited_user["email"]):
#                 invited_user["user_status"] = "invited"
#                 invited_user["invited_at"] = datetime.now()
#                 user_collection.insert_one(invited_user)
#                 send_mail(email=invited_user["email"],subject="Invitation to join",message="You are invited to join.")
#                 data["_id"] = str(data["_id"])
                
#             else:
#                 failed_users.append(invited_user["email"])
                 
#         if len(failed_users)>0 or len(already_invited)>0:
#             data["_id"] = str(data["_id"])
#             return JsonResponse({"success":False,"data":{"failed_users":failed_users,"already_invited":already_invited},"message":"some users failed"})
#         else:
#             ##email
#             data["_id"] = str(data["_id"])
#             return JsonResponse({"success":True,"data":data})
def invite_user(request):
    data = json.loads(request.body)
    user_collection = db["users"]
    user = user_collection.find_one({"_id":ObjectId(data["_id"])})
    if user["user_role"] != "admin":
        return JsonResponse({"succcess":False,"message":"You have no authorization to perform this action"})
    else:
        failed_users=[]
        already_invited =[]
        for invited_user in data["users"]:
            exist_or_not = user_collection.find_one({"email":invited_user["email"],"user_status":"active"})
            if exist_or_not is not None:
                already_invited.append(exist_or_not)
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if re.match(pattern,invited_user["email"]):
                invited_user["user_status"] = "invited"
                invited_user["invited_at"] = datetime.now()
                user_collection.insert_one(invited_user)
                send_mail(email=data["email"],subject="Invitation to join",message="You are invited to join.")
                data["_id"] = str(data["_id"])
                
            else:
                failed_users.append(invited_user["email"])
                 
        if len(failed_users)>0 or len(already_invited)>0:
            data["_id"] = str(data["_id"])
            # print(data)
            return JsonResponse({"success":False,"data":{"failed_users":failed_users,"already_invited":already_invited},"message":"some users failed"})
        else:
            ##email
            # print(data)
            # print(type(data))
            # print(len(data))
            data["_id"] = str(data["_id"])
            for i in data["users"]:
                i["_id"] = str(i["_id"])
            # for j in data:
            #     print(j)
            #     print("**********")
                # j["_id"] = str(j["_id"])
            
            return JsonResponse({"success":True,"data":data})





def login(request):
    data = json.loads(request.body)
    user_collection = db["users"]

    user = user_collection.find_one({"email":data["email"]})

    if user is None:
        return JsonResponse({"success":False, "message":"User not found. Please sign up to continue"})

    if user["password"] != data["password"]:
        return JsonResponse({"success":False, "message":"Invalid password"})

    user["_id"] = str(user["_id"])
    del user["password"] 
    return JsonResponse({"success":True,"data":user})

def create_profile(request):
    data=json.loads(request.body)
    profile_collection=db["profiles"]
    profile_collection.find_one({"email":data["email"]})
    if profile_collection is not None:
        return JsonResponse({"success":True,"message":"profile already exist "})
    profile_collection.insert_one(data)
    data["_id"]=str(data["_id"])
    return JsonResponse({"success":True,"Data":data})


def create_task(request):
    data = json.loads(request.body)
    task_collection = db["task_create"]
    task_collection.insert_one(data)
    data["_id"] = str(data["_id"])
    return JsonResponse({"success":True,"data":data})

def add_profile_photo(request):
    collection = db["users"]
    user_photos = db["user_photos"]
    data = request.POST
    profile = collection.find_one({"_id":ObjectId(data["_id"])})
    user_gallary = user_photos.find_one({"email":profile["email"]})
    if user_gallary is None:
        inserted_doc = user_photos.insert_one({"email":profile["email"]})
        user_gallary = user_photos.find_one({"_id":ObjectId(inserted_doc.inserted_id)})
    if "profile_photos" not in user_gallary.keys():
        user_gallary["profile_photos"] = []
    photo = request.FILES['photo']
    if "user_albums" not in os.listdir():
        os.mkdir("user_albums")
    if str(user_gallary["_id"]) not in os.listdir(os.getcwd()+"/user_albums"):
        os.makedirs(os.getcwd()+"/user_albums/"+str(user_gallary["_id"])+"/")
    print(user_gallary["_id"])
    PHOTOS_PATH = os.getcwd()+"/user_albums/"+str(user_gallary["_id"])+"/"+str(len(user_gallary["profile_photos"]))+".jpeg" 
    with open(PHOTOS_PATH, 'wb+') as destination:
        for chunk in photo.chunks():
            destination.write(chunk)
    user_photos.update_one({"email":profile["email"]},{ "$push": { "profile_photos": PHOTOS_PATH}})
    return JsonResponse({"success":True, "message":"profile photo updated successful+ly"})



# def update_task(request):
#     data = json.loads(request.body)
#     task_collection = db["task_create"]
#     task = task_collection.find_one({"Task_List":data["Task_List"]})
#     if task is None:
#         return JsonResponse({"success":False, "message":"task not found."})
#     else:
#         task_collection.update_one({"Task_List":data["Task_List"]})
#         return JsonResponse({"success":True,"message":"Task Updated"})
    
#     data["_id"] = str(data["_id"])
#     return JsonResponse({"success":True,"data":task})
    

# def delete_task(request):
#     data = json.loads(request.body)
#     task_collection = db["task_create"]
#     task_delete = task_collection.find_one({"Task_List":data["Task_List"]})
#     if task_delete is None:
#         return JsonResponse({"success":False, "message":"task not found."})
#     else:
#         task_collection.delete_one({"Task_List":data["Task_List"]})
#         return JsonResponse({"success":True,"message":"Task Delete"})
    
#     data["_id"] = str(data["_id"])
#     return JsonResponse({"success":True,"data":task_delete})




































    # emails = data["email"]
    # passwords = data["password"]   
    # if emails in email  and passwords in password:
    #     return JsonResponse({"success":True, "message":"Login Successfull"})
    # else:
    #     return JsonResponse({"sucess":False,"message":"account does not exist"}) 
    
    # user_collection.insert_one(data)
    # return JsonResponse({"success":True,"data":data})

