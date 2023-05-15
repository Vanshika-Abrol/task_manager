from django.shortcuts import render
from pytz import timezone
from django.http import JsonResponse
import json
from datetime import datetime
import pymongo
from bson import ObjectId
from emailsoops import send_mail
client =pymongo.MongoClient("mongodb://localhost:27017/")
db=client["TASK_DB"]
# Create your views here.
from django.http import HttpResponse


def create_task(request):
    # only create task if user exist
    data = json.loads(request.body)
    task_collection = db["task_create"]
    data["createdTime"] = datetime.strptime(datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
    data["modifiedTime"] = datetime.strptime(datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
    task_collection.insert_one(data)
    data["_id"] = str(data["_id"])
    return JsonResponse({"success":True,"data":data})

def view_task(request):
    email = request.GET.get("email")
    task_collection = db["task_create"]
    tasks = task_collection.find({"email":email}).sort([("date", pymongo.ASCENDING)])
    output = []
    for i in tasks:
        i["_id"] = str(i["_id"])
        output.append(i)
    return JsonResponse({"success":True,"data":output})

# by deafult sort task

def update_task(request):
    data = json.loads(request.body)
    task_collection = db["task_create"]
    data["date"] = datetime.strptime(data["date"],"%d/%m/%Y")    #datetime.strptime(data["date"],"%d/%m/%Y %H:%M")
    for any_var in data["task_list"]:
        any_var["task_time"] = datetime.strptime(any_var["task_time"],"%d/%m/%Y %H:%M")
    data2 = {}
    for i in data.keys():
        if i=="_id":
            continue
        else:
            data2[i] = data[i]
    data2["modifiedTime"] = datetime.strptime(datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
    task_collection.update_one({"_id":ObjectId(data["_id"])},{"$set":data2})

    return JsonResponse({"success":True,"data":data})

def delete_task(request):
    # if user by mistake delete the task then they can undo the task for next 5 sec
    id = request.GET.get("_id")
    task_collection = db["task_create"]
    task_collection.delete_one({"_id":ObjectId(id)})
    return JsonResponse({"success":True,"message":"Task has been deleted Successfully"})

def view_filter(request):
    email = request.GET.get("email")
    collection = db["task_create"]
    docs = collection.find({"email":email}).sort([("modifiedTime", pymongo.DESCENDING)])
    if request.GET.get("_id"):
        if request.GET.get("filter"):
            doc = collection.find_one({"_id":ObjectId(request.GET.get("_id"))})
            filtered_list = []
            for i in doc["task_list"]:
                if request.GET.get("filter").split("-")[1] == "true":
                    if i["priority"] == True:
                        filtered_list.append(i)
                if request.GET.get("filter").split("-")[1] == "false":
                    if i["priority"] == False:
                        filtered_list.append(i)       
            doc["task_list"] = filtered_list
            doc["_id"] = str(doc["_id"])
            return JsonResponse({"success":True,"data":doc})
    op = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        op.append(doc)
    return JsonResponse({"success":True,"data":op})



def search(request):
    if request.GET.get("search"):
        if len(request.GET.get("search")) <2 :
            return JsonResponse({"success":False,"message":"search term should atleast be 2 characters long"})
        query = {
            "$and": [
                {
                    "$or": [
                        {"title": {"$regex": request.GET.get("search"), "$options": "i"}},
                        {"description": {"$regex": request.GET.get("search"), "$options": "i"}},
                        {"task_list.task_title": {"$regex": request.GET.get("search"), "$options": "i"}},
                        {"task_list.task_description": {"$regex": request.GET.get("search"), "$options": "i"}}
                    ]
                },
                {"email": request.GET.get("email")}
            ]
        }
        collection = db["task_create"]
        results = collection.find(query)
        op =[]
        for i in results:
            i["_id"] = str(i["_id"])
            op.append(i)
        if len(op) == 0:
            return JsonResponse({"success":True,"data":[],"message":"no matching results found"})
        else:
            return JsonResponse({"success":True,"data":op})

def send_request(request):
    id = request.GET.get("_id")
    
    user_collection = db["users"]
    user = user_collection.find_one({"_id":ObjectId(id)})
    if user["user_status"] == "requested":
        return JsonResponse({"success":False,"message":"Request already sent"})
    if user["user_status"] == "unauthorized":
        user_collection.update_one({"_id":ObjectId(id)},{"$set":{"user_status":"requested"}})
        admins = user_collection.find({"domain":user["domain"], "user_role":"admin"})
        for admin in admins: 
            if "request_list" not in admin.keys():
                admin["request_list"] =[]
                admin["request_list"].append({"email":user["email"],"name":user["firstname"]+" "+user["lastname"]})
                user_collection.update_one({"_id":admin["_id"]},{"$set":{"request_list":admin["request_list"]}})
                send_mail(email=admin["email"],subject="Request to join",message="You are invited to join.")
        return JsonResponse({"success":True,"message":"request sent"})
    else:
        return JsonResponse({"success":True,"message":"request not sent"})
           

def accept_request(request):
    user_collection = db["users"]
    user = user_collection.find_one({"_id":ObjectId(request.GET.get("_id"))}) 
    if user["user_status"] == "requested":
        user_collection.update_one({"_id":ObjectId(request.GET.get("_id"))},{"$set":{"user_status":"active"}})
        user = user_collection.find_one({"_id":ObjectId(request.GET.get("_id"))}) 
        user["_id"] = str(user["_id"])
        send_mail(email=user["email"],subject="Request to join",message="You are invited to join.")
    return JsonResponse({"success":"True","data":user})

def reject_request(request):
    user_collection = db["users"]
    user = user_collection.find_one({"_id":ObjectId(request.GET.get("_id"))}) 
    if user["user_status"] == "requested":
        user_collection.update_one({"_id":ObjectId(request.GET.get("_id"))},{"$set":{"user_status":"rejected"}})
        user = user_collection.find_one({"_id":ObjectId(request.GET.get("_id"))})
        user["_id"] = str(user["_id"]) 
    return JsonResponse({"success":"True","data":user})





   

    

# def sort_task(request):
#     # data = json.loads(request.body)
#     id = request.GET.get("_id")
#     task_collection = db["task_create"]
#     n = task_collection.find_one({"_id":ObjectId(id)})
#     n["task_list"] = sorted(n["task_list"], key=lambda x: x["task_time"])
#     n["_id"] = str(n["_id"])
#     return JsonResponse({"success":True,"data":n})



# use filter by time, filter by priority
# search using description, title





    