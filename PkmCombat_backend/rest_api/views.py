from django.shortcuts import render

# Create your views here.
import json
import secrets
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_api.models import User,Team,Battle,Moves,PkmMoves,PkmStats,Pokemon


@csrf_exempt
def register(request):
    if request.method!="POST":
        return JsonResponse({"error": "HTTP method unsupported"},status=405)
    try:
        body_json=json.loads(request.body)
        json_name=body_json["name"]
        json_email=body_json["email"]
        json_password=body_json["password"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error":"Missing parametres in body request"},status=400)

    if len(json_name)<3:
        return JsonResponse({"error": "The name is too short"}, status=400)
    if len(json_email)<6:
        return JsonResponse({"error": "The email is too short"}, status=400)
    if len(json_password)<6:
        return JsonResponse({"error": "The password is too short"}, status=400)
    if "@" not in json_email:
        return JsonResponse({"error": "Invalid json email"}, status=400)
    if User.objects.filter(name=json_name).exists():
        return JsonResponse({"error": "This username already exists"}, status=409)
    if User.objects.filter(email=json_email).exists():
        return JsonResponse({"error": "This email already exists"}, status=409)

    salted_and_hashed_pass = bcrypt.hashpw(
        json_password.encode("utf8"),
        bcrypt.gensalt()
    ).decode("utf8")
    radom_token= secrets.token_hex(10)

    User.objects.create(name=json_name, email= json_email, encrypted_pass=salted_and_hashed_pass)

    return JsonResponse({"registered": True, "token": radom_token}, status=201)


@csrf_exempt
def login(request):
    if request.method!="POST":
        return JsonResponse({"error":"HTTP method unsupportable"}, status=405)
    try:
        body_json=json.loads(request.body)

        json_name=body_json["name"]
        json_password=body_json["encrypted_pass"]
    except KeyError:
        return JsonResponse({"error":"Missing body json parameter"}, status=400)

    try:
        db_user = User.objects.get(name=json_name)
    except User.DoesNotExist:
        return JsonResponse({"error":"User not found"}, status=401)

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_pass.encode('utf8')):
        random_token=secrets.token_hex(10)
        db_user.token_sesion=random_token
        db_user.save()
        return JsonResponse({"token":random_token, "user": db_user.name, "email": db_user.email}, status=200)
    return JsonResponse({"error":"Incorrect password"}, status=401)