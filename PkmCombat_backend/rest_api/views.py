import requests
from django.shortcuts import render

# Create your views here.
import json
import secrets
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_api.constants import NATURES, POKEDEX_LIST
from rest_api.models import User,Team,Battle,Moves,PkmMoves,PkmStats,Pokemon , TeamMember , TurnBattle


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

    User.objects.create(name=json_name, email= json_email, encrypted_pass=salted_and_hashed_pass, token_sesion=radom_token)

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

def __get_request_user(request):
    header_token=request.headers.get("Session", None)
    if not header_token:
        return None
    else:
        try:
            return  User.objects.get(token_sesion=header_token)
        except User.DoesNotExist:
            return  None


def update_or_create_pokemon(request, team_id, slot):
    if request.method!="GET":
        return JsonResponse({"error":"HTTP method unsupportable"}, status=405)
    auth_user = __get_request_user(request)
    if not auth_user:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    name = (request.GET.get("name") or "").lower().strip()
    suggestions_pkm = []
    suggestions_natures = []

    if not name:
        return JsonResponse({"error":"You must enter a name"}, status=400)
    if name not in POKEDEX_LIST:
        for p in POKEDEX_LIST:
            if p.startswith(name):
                suggestions_pkm.append(p)

    lvl = int(request.GET.get("lvl") or 50)
    nature = request.GET.get("nature", "serious").lower().strip()
    if not nature:
        nature = "serious"
    if nature not in NATURES:
        for n in NATURES.keys():
            if n.startswith(nature):
                suggestions_natures.append(n)

    if name not in POKEDEX_LIST or nature not in NATURES:
        return JsonResponse({
            "suggestions_pkm": suggestions_pkm,
            "suggestions_natures": suggestions_natures
        }, status=200)

    ev_hp = int(request.GET.get("ev_hp") or 0)
    ev_att = int(request.GET.get("ev_att") or 0)
    ev_att_esp = int(request.GET.get("ev_att_esp") or 0)
    ev_def = int(request.GET.get("ev_def") or 0)
    ev_def_esp = int(request.GET.get("ev_def_esp") or 0)
    ev_speed = int(request.GET.get("ev_speed") or 0)


    if name:
        url= f"https://pokeapi.co/api/v2/pokemon/{name}"

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
                gen1_sprites = data.get("sprites", {}).get("versions", {}).get("generation-i", {}).get("red-blue", {})
                front_sprite=gen1_sprites.get("front_default")
                back_sprite=gen1_sprites.get("back_default")
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

                attack, defense, spe_att, spe_def, speed = apply_nature(nature, attack, defense, spe_att, spe_def, speed)

                stats_obj = PkmStats.objects.create(
                    hp=hp, att_fis=attack, def_fis=defense,
                    att_esp=spe_att, def_esp=spe_def, speed=speed
                )
                bd_pkm = Pokemon.objects.create(
                    name=name,
                    sound=cries,
                    front_sprite=front_sprite,
                    back_sprite=back_sprite,
                    lvl=lvl,
                    first_type=first_type,
                    second_type=second_type,
                    pkm_stats=stats_obj
                )
                try:
                    team=Team.objects.get(id=team_id,user=auth_user)
                    team_members = TeamMember.objects.get(team=team.id, slot=slot)
                    if team_members.pokemon:
                        if team_members.pokemon.pkm_stats:
                            team_members.pokemon.pkm_stats.delete()
                        team_members.pokemon.delete()
                    team_members.pokemon = bd_pkm
                    team_members.save()
                except Team.DoesNotExist:
                    team_created=Team.objects.create(user=auth_user)
                    TeamMember.objects.create(team=team_created, slot=slot, pokemon=bd_pkm)
                except TeamMember.DoesNotExist:
                    return JsonResponse({"error": "Slot not found in this team"}, status=404)
                return JsonResponse({"OK": "created"}, status=201)
            else:
                return JsonResponse({"error": "Pokemon not found"}, status=404)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Connection error"}, status=500)


def apply_nature(nature, attack, defense, spe_att, spe_def, speed):
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


def update_or_create_move(request, team_id , slot):
    if request.method!="GET":
        return JsonResponse({"error":"HTTP method unsupportable"}, status=405)

    mov1_name = (request.GET.get("mov1") or "").lower().strip()
    mov2_name = (request.GET.get("mov2") or "").lower().strip()
    mov3_name = (request.GET.get("mov3") or "").lower().strip()
    mov4_name = (request.GET.get("mov4") or "").lower().strip()


    if not mov1_name  and  not mov2_name  and not mov3_name  and not mov4_name :
        return JsonResponse({"error": "At a minimum, the pokemon must have a move"},status=400)

    authenticated_user=__get_request_user(request)
    if authenticated_user is None:
        return JsonResponse({"error": "Unauthorized: Missing or invalid token"}, status=401)
    try:
        team=Team.objects.get(id=team_id, user=authenticated_user)#user=authenticated_user
        try:
            team_member=TeamMember.objects.get(team=team.id, slot=slot)
        except TeamMember.DoesNotExist:
            return JsonResponse({"error": "The slot where you want to add the moves doesn't have any Pokémon"}, status=404)
        pk_name=team_member.pokemon.name
        url = f"https://pokeapi.co/api/v2/pokemon/{pk_name}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                learned_moves=[]
                pkm_moves={"mov1": None,
                           "mov2": None,
                           "mov3": None,
                           "mov4": None}
                moves = data.get("moves", [])
                for move in moves:
                    move.get("move",{}).get("name")
                    learned_moves.append(move.get("move").get("name"))

                suggestion_mov1 = []
                suggestion_mov2 = []
                suggestion_mov3 = []
                suggestion_mov4 = []

                if mov1_name in learned_moves:
                    pkm_moves["mov1"] = mov1_name
                elif mov1_name:
                    for l in learned_moves:
                        if l.startswith(mov1_name):
                            suggestion_mov1.append(l)

                if mov2_name in learned_moves:
                    pkm_moves["mov2"] = mov2_name
                elif mov2_name:
                    for l in learned_moves:
                        if l.startswith(mov2_name):
                            suggestion_mov2.append(l)

                if mov3_name in learned_moves:
                    pkm_moves["mov3"] = mov3_name
                elif mov3_name:
                    for l in learned_moves:
                        if l.startswith(mov3_name):
                            suggestion_mov3.append(l)

                if mov4_name in learned_moves:
                    pkm_moves["mov4"] = mov4_name
                elif mov4_name:
                    for l in learned_moves:
                        if l.startswith(mov4_name):
                            suggestion_mov4.append(l)

                if suggestion_mov1 or suggestion_mov2 or suggestion_mov3 or suggestion_mov4:
                    return JsonResponse({
                        "suggestion_mov1": suggestion_mov1,
                        "suggestion_mov2": suggestion_mov2,
                        "suggestion_mov3": suggestion_mov3,
                        "suggestion_mov4": suggestion_mov4
                    }, status=200)

                for requested_move in pkm_moves.values():
                    if requested_move:
                            try:
                                move_obj = Moves.objects.get(name=requested_move)
                                pkm_move=PkmMoves.objects.filter(pokemon=team_member.pokemon, move=move_obj).first()
                                if pkm_move:
                                    pkm_move.pokemon=team_member.pokemon
                                    pkm_move.move=move_obj
                                    pkm_move.save()
                                else:
                                    PkmMoves.objects.create(pokemon=team_member.pokemon, move=move_obj)

                            except Moves.DoesNotExist:
                                return JsonResponse({"error": f"The movement {requested_move} does not exist in BD"},status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Connection error"}, status=500)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team no does not exist or this slot dont have pkm"}, status=400)
    return JsonResponse({"OK": "Moves created"},status=201)


@csrf_exempt
def delete_team(request, team_id):
    if request.method!="DELETE":
        return JsonResponse({"error":"HTPP method unsupportable"}, status=405)
    auth_user=__get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error":"Invalid token"}, status=401)
    try:
        team_obj=Team.objects.get(id=team_id , user=auth_user)
        team_obj.delete()
    except Team.DoesNotExist:
        return JsonResponse({"error": "The team you want to delete does not exist"}, status=404)
    return JsonResponse({"ok":"Team deleted successfully"}, status=200)