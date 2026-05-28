import math
import random

import requests
from django.shortcuts import render

# Create your views here.
import json
import secrets
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_api.constants import NATURES, POKEDEX_LIST, PRIORITY_MOVES, TYPE_CHART
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

    db_user=User.objects.create(name=json_name, email= json_email, encrypted_pass=salted_and_hashed_pass, token_sesion=radom_token)

    return JsonResponse({"registered": True, "token": radom_token, "id":db_user.id}, status=201)


@csrf_exempt
def login(request):
    if request.method!="POST":
        return JsonResponse({"error":"HTTP method unsupportable"}, status=405)
    try:
        body_json=json.loads(request.body)

        json_name=body_json["name"]
        json_password=body_json["password"]
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
        return JsonResponse({"token":random_token, "user": db_user.name, "email": db_user.email, "id":db_user.id}, status=200)
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

@csrf_exempt
def update_or_create_pokemon(request, team_id, slot):
    if request.method!="POST":
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
    if lvl < 1 or lvl > 100:
        return JsonResponse({"error": "Level must be between 1 and 100"}, status=400)
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

    if any(ev > 252 for ev in [ev_hp, ev_att, ev_att_esp, ev_def, ev_def_esp, ev_speed]):
        return JsonResponse({"error": "No EV can exceed 252"}, status=400)

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
                    nature=nature,
                    first_type=first_type,
                    second_type=second_type,
                    pkm_stats=stats_obj
                )
                try:
                    team = Team.objects.get(id=team_id, user=auth_user)
                    try:
                        team_members = TeamMember.objects.get(team=team.id, slot=slot)
                        if team_members.pokemon:
                            if team_members.pokemon.pkm_stats:
                                team_members.pokemon.pkm_stats.delete()
                            team_members.pokemon.delete()
                        team_members.pokemon = bd_pkm
                        team_members.save()
                    except TeamMember.DoesNotExist:
                        TeamMember.objects.create(team=team, slot=slot, pokemon=bd_pkm)

                except Team.DoesNotExist:
                    team_created = Team.objects.create(user=auth_user)
                    TeamMember.objects.create(team=team_created, slot=slot, pokemon=bd_pkm)

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

@csrf_exempt
def update_or_create_move(request, team_id , slot):
    if request.method!="POST":
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
                    }, status=400)

                PkmMoves.objects.filter(pokemon=team_member.pokemon).delete()

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

@csrf_exempt
def delete_pkm_in_team(request, team_id, slot_id):
    if request.method!="DELETE":
        return JsonResponse({"error":"HTPP method unsupportable"}, status=405)
    auth_user=__get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error":"Invalid token"}, status=401)
    try:
        team_obj = Team.objects.get(id=team_id, user=auth_user)
        team_member=TeamMember.objects.get(team=team_obj,slot=slot_id)
        team_member.pokemon=None
        team_member.save()
        return JsonResponse({"ok": "Slot  delete successfully"}, status=200)
    except Team.DoesNotExist:
        return JsonResponse({"error": "The team does not exists"}, status=404)
    except TeamMember.DoesNotExist:
        return JsonResponse({"error": "Slot not found in this team"}, status=404)


def get_all_teams(request):
    if request.method != "GET":
        return JsonResponse({"error": "HTTP method unsupported"}, status=405)

    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)

    teams_obj = Team.objects.filter(user=auth_user)

    if not teams_obj.exists():
        return JsonResponse([], safe=False, status=200)

    team_list = []
    for team_obj in teams_obj:
        team_members = TeamMember.objects.filter(team=team_obj).select_related('pokemon').order_by('slot')

        team_members_list = []
        for team_member in team_members:
            if team_member.pokemon:
                team_members_list.append({
                    "slot": team_member.slot,
                    "front_sprite": team_member.pokemon.front_sprite
                })

        team_list.append({
            "team_id": team_obj.id,
            "members": team_members_list
        })

    return JsonResponse(team_list, safe=False, status=200)


def get_team(request, team_id):
    if request.method!="GET":
        return JsonResponse({"error": "HTTP method not supported"},status=405)
    auth_user=__get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error":"Invalid token"}, status=401)
    try:
        team_obj = Team.objects.get(id=team_id)
        team_members_obj = TeamMember.objects.filter(team=team_obj).select_related('pokemon', 'pokemon__pkm_stats').order_by('slot')
        json_team = {"id": team_obj.id,
                     "user": team_obj.user.id,
                     "members":[]}
        for team_member in team_members_obj:
            pkm_obj = None
            if team_member.pokemon:
                pkm_moves = PkmMoves.objects.filter(pokemon=team_member.pokemon).select_related("move")

                moves_list = []
                for m in pkm_moves:
                    moves_list.append({
                        "name": m.move.name,
                        "desc": m.move.desc,
                        "type": m.move.type,
                        "category":m.move.category,
                        "power": m.move.power,
                        "accuracy": m.move.accuracy,
                        "priority": m.move.priority,
                        "effect_type": m.move.effect_type,
                        "effect_chance": m.move.effect_chance
                    })

                stats_obj = {
                    "hp": team_member.pokemon.pkm_stats.hp,
                    "current_hp": team_member.pokemon.pkm_stats.hp,
                    "def_esp": team_member.pokemon.pkm_stats.def_esp,
                    "def_fis": team_member.pokemon.pkm_stats.def_fis,
                    "att_esp": team_member.pokemon.pkm_stats.att_esp,
                    "att_fis": team_member.pokemon.pkm_stats.att_fis,
                    "speed": team_member.pokemon.pkm_stats.speed,
                }
                pkm_obj = {
                    "name": team_member.pokemon.name,
                    "sound": team_member.pokemon.sound,
                    "front_sprite": team_member.pokemon.front_sprite,
                    "back_sprite": team_member.pokemon.back_sprite,
                    "lvl": team_member.pokemon.lvl,
                    "first_type": team_member.pokemon.first_type,
                    "second_type": team_member.pokemon.second_type,
                    "status": team_member.pokemon.status,
                    "nature": team_member.pokemon.nature,
                    "status_count": team_member.pokemon.status_count,
                    "volatile_status": [],
                    "pkm_stats": stats_obj,
                    "pkm_moves": moves_list
                }

            json_team.get("members").append({
                "slot": team_member.slot,
                "is_active": False,
                "pokemon": pkm_obj
            })
        return JsonResponse(json_team,status=200)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team does not exist"}, status=404)



def create_battle(request, user_team_id , opponent_id):
    if request.method!="POST":
        return JsonResponse({"error": "HTTP method not supported"}, status=405)
    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)

    res_user_team=get_team(request,user_team_id)

    user_team_data=json.loads(res_user_team.content)


    try:
        opponent=User.objects.get(id=opponent_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "The opponent does not exists"}, status=404)

    battle=Battle.objects.create(
        user=auth_user,
        opponent=opponent,
        status="waiting",
        winner=None,
        user_team=user_team_data,
        opponent_team={}
    )

    return JsonResponse({"ok":"Battle created", "battle_id": battle.id}, status=201)


def accept_challenge(request, battle_id, opponent_team_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Method not supported"}, status=405)
    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)

    res_opponent_team = get_team(request,opponent_team_id)
    opponent_team_data = json.loads(res_opponent_team.content)

    try:
        battle = Battle.objects.get(id=battle_id, opponent=auth_user)

        if battle.status != "waiting":
            return JsonResponse({"error": "Battle already started or finished"}, status=400)
        battle.opponent_team=opponent_team_data
        battle.status = "in_progress"
        battle.save()

        TurnBattle.objects.get_or_create(
            battle=battle,
            current_turn=1,
        )

        return JsonResponse({"ok": "Battle started! Good luck"}, status=200)
    except Battle.DoesNotExist:
        return JsonResponse({"error": "Challenge not found"}, status=404)
@csrf_exempt
def get_my_challenges(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not supported"}, status=405)
    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)

    challenge_list=[]
    challenges=Battle.objects.filter(opponent=auth_user, status="waiting")
    for battle in challenges:
        challenge_list.append({
            "battle_id": battle.id,
            "challenger": battle.user.id,
            "challenger_name": battle.user.name
        })

    return JsonResponse(challenge_list,safe=False,status=200)

def choose_first_pkm(request, slot, battle_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not supported"}, status=405)
    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)
    first_pkm_name = ""
    try:
        active_battle = Battle.objects.get(user=auth_user, id=battle_id, status="in_progress")
        user_team_list = active_battle.user_team.get("members", [])
        for pkm in user_team_list:
            if pkm.get("slot") ==slot:
                pkm["is_active"] = True
                first_pkm_name = pkm.get("pokemon").get("name")
            else:
                pkm["is_active"] = False
        active_battle.save()

    except Battle.DoesNotExist:
        try:
            active_battle = Battle.objects.get(opponent=auth_user, id=battle_id, status="in_progress")
            opponent_team_list = active_battle.opponent_team.get("members", [])
            for pkm in opponent_team_list:
                if pkm.get("slot") ==slot:
                    pkm["is_active"] = True
                    first_pkm_name=pkm.get("pokemon").get("name")
                else:
                    pkm["is_active"] = False
            active_battle.save()
        except Battle.DoesNotExist:
            return JsonResponse({"error": "You are not currently participating in this battle"}, status=404)

    return JsonResponse({"ok": f"You choose: {first_pkm_name}"}, status=200)

@csrf_exempt
def choose_user_action(request, battle_id,action,action_value):
    if request.method!="POST":
        return  JsonResponse({"error":"HTTP method not supported"}, status=405)
    auth_user=__get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)
    try:
        try:
            active_battle = Battle.objects.get(user=auth_user, id=battle_id, status="in_progress")
        except Battle.DoesNotExist:
            active_battle = Battle.objects.get(opponent=auth_user, id=battle_id, status="in_progress")

        current_turn_obj = TurnBattle.objects.get(battle=active_battle, resolve=False)

        if auth_user==active_battle.user:
            current_turn_obj.user_act=action
            current_turn_obj.user_act_value=action_value
        elif auth_user==active_battle.opponent:
            current_turn_obj.opponent_act = action
            current_turn_obj.opp_act_value = action_value
        current_turn_obj.save()

        if current_turn_obj.user_act!="not_selected" and  current_turn_obj.opponent_act!="not_selected":
            process_the_battle_turn(request,active_battle.id)
            return JsonResponse({"ok": "Action received, turn resolving...", "resolved": True}, status=200)
        else:
            return JsonResponse({"ok": "Waiting for opponent","resolved": False}, status=200)
    except (Battle.DoesNotExist, TurnBattle.DoesNotExist):
        return JsonResponse({"error": "Either the battle or turn doesn't exist, or you're not a participant"}, status=404)


def process_the_battle_turn(request, battle_id):
    if request.method!="POST":
        return JsonResponse({"error":"HTTP method not supported"}, status=405)
    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)
    turn_msg = []
    try:
        u_members_deaths_cont, o_members_deaths_cont = 0, 0
        active_battle=Battle.objects.get(id=battle_id)
        if active_battle.status=="waiting":
            return  JsonResponse({"ok":"The battle is on hold"}, status=200)
        elif active_battle.status=="in_progress":
            try:
                turn_battle = TurnBattle.objects.get(battle=active_battle, resolve=False)

                #change turn
                if turn_battle.user_act == "change_pkm":
                    change_pkm(auth_user, turn_battle.user_act_value, active_battle,turn_msg)
                if turn_battle.opponent_act == "change_pkm":
                    change_pkm(active_battle.opponent, turn_battle.opp_act_value, active_battle,turn_msg)

                #Calculate who attack first
                user_team=active_battle.user_team.get("members", [])
                opponent_team=active_battle.opponent_team.get("members", [])

                u_has_prio = turn_battle.user_act_value in PRIORITY_MOVES
                o_has_prio = turn_battle.opp_act_value in PRIORITY_MOVES

                u_speed = get_active_u_speed(user_team) + (1000 if u_has_prio else 0)
                o_speed = get_active_o_speed(opponent_team) + (1000 if o_has_prio else 0)

                if u_speed> o_speed:
                   if turn_battle.user_act=="attack":
                        attack(auth_user, turn_battle.user_act_value, active_battle,turn_msg)
                   if turn_battle.opponent_act=="attack" and get_active_o_hp(opponent_team)>0:
                        attack(active_battle.opponent, turn_battle.opp_act_value, active_battle,turn_msg)
                else:
                    if turn_battle.opponent_act=="attack":
                        attack(active_battle.opponent, turn_battle.opp_act_value, active_battle,turn_msg)
                    if turn_battle.user_act=="attack" and get_active_u_hp(user_team)>0:
                        attack(auth_user, turn_battle.user_act_value, active_battle,turn_msg)

                u_hp = get_active_u_hp(user_team)
                o_hp = get_active_o_hp(opponent_team)

                if u_hp > 0 and o_hp > 0:
                    next_turn_num = turn_battle.current_turn + 1
                    TurnBattle.objects.get_or_create(
                        battle=active_battle,
                        current_turn=next_turn_num
                    )
                else:
                    turn_msg.append("Waiting for the trainer to choose a new Pokémon...")

                active_battle.save()
                turn_battle.resolve=True
                turn_battle.turn_log = turn_msg
                turn_battle.save()

                u_members = active_battle.user_team.get("members", [])
                o_members = active_battle.opponent_team.get("members", [])

                for u_member in u_members:
                    u_member_stats=u_member.get("pokemon",{}).get("pkm_stats",{})
                    if u_member_stats.get("current_hp")<=0:
                        u_members_deaths_cont+=1

                for o_member in o_members:
                    o_member_stats=o_member.get("pokemon",{}).get("pkm_stats",{})
                    if o_member_stats.get("current_hp")<=0:
                        o_members_deaths_cont+=1

                if u_members_deaths_cont==6:
                    active_battle.winner=active_battle.opponent
                    active_battle.status="finished"
                    active_battle.save()
                    return JsonResponse({"ok": "You dont have  more pokemons ,  you lost the battle"}, status=200)
                if o_members_deaths_cont==6:
                    active_battle.winner=active_battle.user
                    active_battle.status = "finished"
                    active_battle.save()
                    return JsonResponse({"ok": "You defeated all your opponents' remaining Pokémon and won the battle"},status=200)

                return JsonResponse({
                    "ok": "Turn processed",
                    "status": "in_progress",
                    "user_team": active_battle.user_team,
                    "opponent_team": active_battle.opponent_team,
                    "turn_msg": turn_msg
                }, status=200)
            except TurnBattle.DoesNotExist:
                return JsonResponse({"error": "An error has occurred in the battle"}, status=404)
        elif active_battle.status == "finished":
            return JsonResponse({"ok":"The battle is finished"}, status=200)
    except Battle.DoesNotExist:
        return JsonResponse({"error":"Battle does not exist"}, status=404)


def get_active_u_speed(user_team):
    for u_member in user_team:
        if u_member.get("is_active"):
            pokemon = u_member.get("pokemon", {})
            stats = pokemon.get("pkm_stats", {})
            if stats.get("current_hp", 0) <= 0:
                return 0

            speed = stats.get("speed", 0)
            if pokemon.get("status") == "eff_par":
                speed = speed // 2
            return speed
    return 0


def get_active_o_speed(opponent_team):
    for o_member in opponent_team:
        if o_member.get("is_active"):
            pokemon = o_member.get("pokemon", {})
            stats = pokemon.get("pkm_stats", {})
            if stats.get("current_hp", 0) <= 0:
                return 0

            speed = stats.get("speed", 0)
            if pokemon.get("status") == "eff_par":
                speed = speed // 2
            return speed
    return 0

def get_active_u_hp(user_team):
    for u_member in user_team:
        if u_member.get("is_active"):
            u_pkm_hp = u_member.get("pokemon", {}).get("pkm_stats", {}).get("current_hp")
            return u_pkm_hp
    return None


def get_active_o_hp(opponent_team):
    for o_member in opponent_team:
        if o_member.get("is_active"):
            o_pkm_hp = o_member.get("pokemon", {}).get("pkm_stats", {}).get("current_hp")
            return o_pkm_hp
    return None



def change_pkm(user, value, active_battle,turn_msg):
    if active_battle.user == user:
        team_data = active_battle.user_team
    elif active_battle.opponent == user:
        team_data = active_battle.opponent_team
    else:
        return JsonResponse({"error": "You don't belong in this fight" },status=401)

    if team_data:
        members = team_data.get("members", [])

        for member in members:
            pkm_name=member.get("pokemon",{}).get("name","Unknown")
            if member.get("slot") == value:
                member["is_active"] = True
                turn_msg.append(f"You switched to {pkm_name}")
            else:
                member["is_active"] = False
        if active_battle.user == user:
            active_battle.user_team = team_data
        else:
            active_battle.opponent_team = team_data
        active_battle.save()
    return None


def attack(user, value, active_battle,turn_msg):
    try:
        move = Moves.objects.get(name=value)
        user_team = active_battle.user_team.get("members", [])
        opponent_team = active_battle.opponent_team.get("members", [])

        pkm_user, pkm_opp = None, None

        for member in user_team:
            if member.get("is_active"):
                pkm_user = member

        for member in opponent_team:
            if member.get("is_active"):
                pkm_opp = member

        if not pkm_user or not pkm_opp:
            return None

        if active_battle.user == user:
            process_attack(move, pkm_user, pkm_opp,turn_msg)
        elif active_battle.opponent == user:
            process_attack(move, pkm_opp, pkm_user,turn_msg)


        active_battle.user_team["members"] = user_team
        active_battle.opponent_team["members"] = opponent_team

        active_battle.save()

    except Moves.DoesNotExist:
        return JsonResponse(f"El movimiento {value} no existe en la base de datos.")



def process_attack(move, attacker_pkm, defender_pkm,turn_msg):
    category = move.category
    mov_name=move.name
    turn_msg.append(f"The pokemon used {mov_name}")
    defender_stats = defender_pkm.get("pokemon").get("pkm_stats", {})
    attacker_stats = attacker_pkm.get("pokemon").get("pkm_stats", {})
    variation = random.uniform(0.85, 1.0)
    damage = 0

    ignored_effects = ["unique", "trap", "two_turn", "recharge", "bide", "ohko", "fixed_hp"]

    if move.effect_type in ignored_effects:
        turn_msg.append(f"The move {move.name} is not implemented yet!")
        return

    if "flinch" in attacker_pkm.get("volatile_status", []):
        attacker_pkm["volatile_status"].remove("flinch")
        turn_msg.append(f"¡{attacker_pkm['name']} is  flinched!")
        return
    current_status = attacker_pkm.get("status")
    if current_status in ["eff_frz", "eff_slp"]:
        if attacker_pkm.get("status_count", 0) == 0:
            attacker_pkm["status_count"] = random.randint(2, 5) if current_status == "eff_frz" else random.randint(1, 3)
            msg = "is frozen solid!" if current_status == "eff_frz" else "is fast asleep!"
            turn_msg.append(f"{attacker_pkm['name']} {msg}")
            return

        attacker_pkm["status_count"] -= 1

        if attacker_pkm["status_count"] <= 0:
            attacker_pkm["status"] = "none"
            msg = "thawed out!" if current_status == "eff_frz" else "woke up!"
            turn_msg.append(f"{attacker_pkm['name']} {msg}")
        else:
            msg = "is frozen solid!" if current_status == "eff_frz" else "is fast asleep!"
            turn_msg.append(f"{attacker_pkm['name']} {msg}")
            return
    if current_status=="eff_par":
        chance=random.randint(1,100)
        if chance<=25:
            turn_msg.append(f"{attacker_pkm['name']} is paralyzed!")
            return
    if  current_status== "eff_con":
        chance = random.randint(0, 100)
        if chance<= 33:
            self_damage = int(attacker_stats["hp"] * 0.10)
            attacker_stats["current_hp"] = max(0, attacker_stats["current_hp"] - self_damage)
            turn_msg.append(f"{attacker_pkm['name']} is confused, he hurt itself in its confusion!")
            return

    match category:
        case "physical":
            current_att = attacker_stats["att_fis"]
            if attacker_pkm.get("status") == "eff_brn":
                current_att *= 0.5
            damage = ((move.power * current_att) / defender_stats["def_fis"]) * variation
            if move.effect_type=="recoil":
                self_damage = int(damage * 0.25)
                attacker_stats["current_hp"] = max(0, attacker_stats["current_hp"] - self_damage)
                turn_msg.append(f"{attacker_pkm['name']} was hit with recoil!")
        case "special":
            damage = ((move.power * attacker_stats["att_esp"]) / defender_stats["def_esp"]) * variation
        case "status":
            effect = move.effect_type
            stat_change=move.stat_change_amount
            blacklist = ["dream-eater", "sand-attack", "flash", "kinesis","double-team", "minimize", "smokescreen"]
            if mov_name in blacklist:
                turn_msg.append(f"The move {move.name} is not implemented yet!")
                return

            match effect:
                case "flinch":
                    if random.randint(1, 100) <= move.effect_chance:
                        if "flinch" not in defender_pkm.get("volatile_status", []):
                            volatile_status = defender_pkm.get("volatile_status")
                            volatile_status.append("flinch")
                case "eff_frz":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_frz"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been frozen!")
                case "eff_brn":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_brn"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been burned!")
                case "eff_slp":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_slp"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been slept!")
                case "eff_psn":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_psn"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been poisoned!")
                case "eff_con":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_con"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been confused!")
                case "eff_par":
                    if random.randint(1, 100) <= move.effect_chance:
                        if defender_pkm.get("status") == "none":
                            defender_pkm["status"] = "eff_par"
                            turn_msg.append(f"¡{defender_pkm.get('pokemon', {}).get('name')} has been paralyzed!")
                case "multi_hit":
                    if mov_name=="double-kick":
                        hits=2
                    else:
                        hits = random.randint(2, 5)

                    total_damage = 0
                    for hit in range(hits):
                        damage = ((move.power * attacker_stats["att_fis"]) / defender_stats["def_fis"]) * variation
                        total_damage+=damage

                    damage=total_damage
                    turn_msg.append(f"{attacker_pkm['name']} hit {hits} times!")
                case "healing":
                    hp = attacker_pkm.get("hp")
                    current_hp = attacker_pkm.get("current_hp")
                    heal = math.floor(hp / 2)
                    current_hp += heal
                    if current_hp > hp: current_hp = hp
                    attacker_pkm["current_hp"] = current_hp
                case "mod_atq":
                    if stat_change == 1:attacker_stats["att_fis"] = int(attacker_stats["att_fis"] * 1.5)
                    elif stat_change >= 2:attacker_stats["att_fis"] = int(attacker_stats["att_fis"] * 2.0)
                    elif stat_change == -1:defender_stats["att_fis"] = int(defender_stats["att_fis"] * 0.66)
                    elif stat_change <= -2:defender_stats["att_fis"] = int(defender_stats["att_fis"] * 0.5)
                case "mod_def":
                    if stat_change == 1:attacker_stats["def_fis"] = int(attacker_stats["def_fis"] * 1.5)
                    elif stat_change >= 2:attacker_stats["def_fis"] = int(attacker_stats["def_fis"] * 2.0)
                    elif stat_change == -1:defender_stats["def_fis"] = int(defender_stats["def_fis"] * 0.66)
                    elif stat_change <= -2:defender_stats["def_fis"] = int(defender_stats["def_fis"] * 0.5)
                case "mod_spa":
                    if stat_change == 1:attacker_stats["att_esp"] = int(attacker_stats["att_esp"] * 1.5)
                    elif stat_change >= 2:attacker_stats["att_esp"] = int(attacker_stats["att_esp"] * 2.0)
                    elif stat_change == -1:defender_stats["att_esp"] = int(defender_stats["att_esp"] * 0.66)
                    elif stat_change <= -2:defender_stats["att_esp"] = int(defender_stats["att_esp"] * 0.5)
                case "mod_spd":
                    if stat_change == 1:attacker_stats["def_esp"] = int(attacker_stats["def_esp"] * 1.5)
                    elif stat_change >= 2:attacker_stats["def_esp"] = int(attacker_stats["def_esp"] * 2.0)
                    elif stat_change == -1:defender_stats["def_esp"] = int(defender_stats["def_esp"] * 0.66)
                    elif stat_change <= -2:defender_stats["def_esp"] = int(defender_stats["def_esp"] * 0.5)
                case "mod_vel":
                    if stat_change == 1:attacker_stats["speed"] = int(attacker_stats["speed"] * 1.5)
                    elif stat_change >= 2:attacker_stats["speed"] = int(attacker_stats["speed"] * 2.0)
                    elif stat_change == -1:defender_stats["speed"] = int(defender_stats["speed"] * 0.66)
                    elif stat_change <= -2:defender_stats["speed"] = int(defender_stats["speed"] * 0.5)

    if  attacker_pkm.get("status")== "eff_brn":
        burn_damage = int(attacker_stats["hp"] // 16)
        attacker_stats["current_hp"] = max(0, attacker_stats["current_hp"] - max(1, burn_damage))

    if attacker_pkm.get("status") == "eff_psn":
        attacker_pkm["status_count"] = attacker_pkm.get("status_count", 0) + 1
        poison_dmg = (attacker_stats["hp"] // 16) * attacker_pkm["status_count"]
        poison_dmg = max(1, poison_dmg)
        attacker_stats["current_hp"] = max(0, attacker_stats["current_hp"] - poison_dmg)
        turn_msg.append(f"{attacker_pkm['name']} is hurt by poison!")

    if damage > 0:
        move_type = move.type
        types = [defender_pkm.get("first_type"), defender_pkm.get("second_type")]

        effectiveness = 1.0
        for t in types:
            if t and t != "none":
                mult = TYPE_CHART.get(move_type, {}).get(t, 1.0)
                effectiveness *= mult

        attacker_types = [attacker_pkm.get("first_type"), attacker_pkm.get("second_type")]
        stab = 1.5 if move_type in attacker_types else 1.0

        damage = int(damage * effectiveness* stab)
        current_hp = defender_stats.get("current_hp", 0)
        defender_stats["current_hp"] = max(0, current_hp - damage)

def get_turn_status(request, battle_id):
    if request.method != "GET":
        return JsonResponse({"error": "HTTP method unsupported"}, status=405)
    # Check the current turn
    # If “resolve” is already True, it means the second player has already moved
    # and the server has already processed the battle.
    turno = TurnBattle.objects.filter(battle_id=battle_id,resolve=True).order_by('-current_turn').first()

    if turno.resolve:
        return JsonResponse({
            "turn_resolved": True,
            "turn_msg": turno.turn_log,
            "user_team": turno.battle.user_team,
            "opponent_team": turno.battle.opponent_team
        })
    else:
        return JsonResponse({"turn_resolved": False})

def get_users(request):
    if request.method != "GET":
        return JsonResponse({"error": "HTTP method unsupported"}, status=405)

    auth_user = __get_request_user(request)
    if auth_user is None:
        return JsonResponse({"error": "Invalid token"}, status=401)

    users = User.objects.all().order_by("-id")[:6]

    if not users:
        return JsonResponse({"error": "No users are available"}, status=404)

    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.name,
            "status": user.online
        })

    return JsonResponse(users_list, safe=False, status=200)
