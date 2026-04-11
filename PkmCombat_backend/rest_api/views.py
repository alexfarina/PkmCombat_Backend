import requests
from django.shortcuts import render

# Create your views here.
import json
import secrets
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_api.constants import NATURES, POKEDEX_LIST
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


def update_pokemon(request, team_id, slot):
    if request.method!="GET":
        return JsonResponse({"error":"HTTP method unsupportable"}, status=405)

    name = (request.GET.get("name") or "").lower().strip()

    if not name:
        return JsonResponse({"error":"You must enter a name"}, status=400)
    if name not in POKEDEX_LIST:
        sugerencias = [p for p in POKEDEX_LIST if p.startswith(name)][:20]
        return JsonResponse({"suggestions": sugerencias})

    lvl = max(1, min(int(request.GET.get("lvl") or 50), 99))

    nature = request.GET.get("nature", "serious").lower().strip()
    if not nature:
        nature = "serious"
    if nature not in NATURES:
        return JsonResponse({"error": "Invalid nature"}, status=400)

    ev_hp = max(0, min(int(request.GET.get("ev_hp") or 0), 252))
    ev_att = max(0, min(int(request.GET.get("ev_att") or 0), 252))
    ev_att_esp = max(0, min(int(request.GET.get("ev_att_esp") or 0), 252))
    ev_def = max(0, min(int(request.GET.get("ev_def") or 0), 252))
    ev_def_esp = max(0, min(int(request.GET.get("ev_def_esp") or 0), 252))
    ev_speed = max(0, min(int(request.GET.get("ev_speed") or 0), 252))
    total_ev = (
            ev_hp + ev_att + ev_att_esp +
            ev_def + ev_def_esp + ev_speed
    )

    if total_ev > 510:
        return JsonResponse({"error": "EV total cannot exceed 510"}, status=400)


    if name:
        url= f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                name=data.get("name")
                moves=data.get("moves",[])
                learnable_moves=[]
                for move in moves:
                    move_name=move.get("move").get("name")
                    learnable_moves.append(move_name)
                cries=data.get("cries",{}).get("legacy")
                sprites = data.get("sprites", {}).get("versions", {}).get("generation-i", {}).get("red-blue", {})
                front_sprite = sprites.get("front_default")
                back_sprite = sprites.get("back_default")
                types = data.get("types", [])
                first_type = types[0].get("type").get("name") if len(types) > 0 else None
                second_type = types[1].get("type").get("name") if len(types) > 1 else None

                stats=data.get("stats",[])
                hp=stats[0].get("base_stat") if len(stats)>0 else None
                attack=stats[1].get("base_stat") if len(stats)>1 else None
                defense=stats[2].get("base_stat") if len(stats)>2 else None
                spe_att=stats[3].get("base_stat") if len(stats)>3 else None
                spe_def=stats[4].get("base_stat") if len(stats)>4 else None
                speed=stats[5].get("base_stat") if len(stats)>5 else None


                iv = 31
                #Stats by level
                hp=((2 * hp + iv + (ev_hp//4)) * lvl // 100 ) + lvl + 10
                attack=((2 * attack + iv + (ev_att // 4)) * lvl // 100) + 5
                defense=((2 * defense + iv + (ev_def // 4)) * lvl // 100) + 5
                spe_att=((2 * spe_att + iv + (ev_att_esp // 4)) * lvl // 100) + 5
                spe_def=((2 * spe_def + iv + (ev_def_esp // 4)) * lvl // 100) + 5
                speed=((2 * speed + iv + (ev_speed // 4)) * lvl // 100) + 5

                attack, defense, spe_att, spe_def, speed = aplicar_naturaleza(nature, attack, defense, spe_att, spe_def, speed)


                pkm_stats={"hp": hp,
                       "att":attack,
                       "def": defense,
                       "spe_att":spe_att,
                       "spe_def":spe_def,
                       "speed": speed}

                pkm_json = {"name": name,
                            "lvl":lvl,
                        "crie": cries,
                        "front_sprite":front_sprite,
                        "back_sprite":back_sprite,
                        "first_tpye": first_type,
                        "second_type": second_type,
                        "pkm_stats": pkm_stats,
                        "learned-moves": learnable_moves
                      }
                return JsonResponse(pkm_json, status=200)
            else:
                return JsonResponse({"error": "Pokemon not found"}, status=404)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Connection error"}, status=500)


def aplicar_naturaleza(nature, attack, defense, spe_att, spe_def, speed):
    natures = NATURES.get(nature.lower(), {})
    if "up_att" in natures : attack *= natures.get("up_att")
    if "up_def" in natures : defense *= natures.get("up_def")
    if "up_att_esp" in natures : spe_att *= natures.get("up_att_esp")
    if  "up_def_esp" in natures : spe_def *= natures.get("up_def_esp")
    if "up_speed" in natures : speed *= natures.get("up_speed")

    if "low_att" in natures : attack *= natures.get("low_att")
    if "low_def" in natures : defense *= natures.get("low_def")
    if "low_att_esp" in natures : spe_att *= natures.get("low_att_esp")
    if  "low_def_esp" in natures : spe_def *= natures.get("low_def_esp")
    if "low_speed" in natures : speed *= natures.get("low_speed")

    return int(attack), int(defense), int(spe_att), int(spe_def), int(speed)