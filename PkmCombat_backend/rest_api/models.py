from django.db import models


class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    encrypted_pass = models.CharField(max_length=300)
    online = models.BooleanField(default=False)
    token_sesion = models.CharField(default=150)


class Moves(models.Model):
    CATEGORY_CHOICES = [('physical', 'Físico'),('special', 'Especial'),('status', 'Estado'),]
    name = models.CharField(max_length=150, unique=True)
    desc = models.TextField(max_length=5000, null=True, blank=True)
    type = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    power = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(default=0)  #+1 , +2
    effect_type = models.CharField(max_length=50) #poisoned
    effect_chance = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class PkmStats(models.Model):
    hp = models.IntegerField(null=True, blank=True)
    def_esp = models.IntegerField(null=True, blank=True)
    def_fis = models.IntegerField(null=True, blank=True)
    att_esp = models.IntegerField(null=True, blank=True)
    att_fis = models.IntegerField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)


class Pokemon(models.Model):
    name = models.CharField(max_length=150)
    sound =  models.URLField(blank=True, null=True)
    front_sprite = models.URLField(blank=True, null=True)
    back_sprite = models.URLField(blank=True, null=True)
    lvl = models.IntegerField(default=1)
    first_type = models.CharField(max_length=150)
    second_type = models.CharField(max_length=150, blank=True, null=True)
    pkm_stats = models.ForeignKey('PkmStats', on_delete=models.CASCADE)


class PkmMoves(models.Model):
    pokemon = models.ForeignKey('Pokemon', on_delete=models.CASCADE)
    move = models.ForeignKey('Moves', on_delete=models.CASCADE)


class Team(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    slot = models.IntegerField()
    pokemon = models.ForeignKey('Pokemon', null=True, blank=True, on_delete=models.SET_NULL)

class Battle(models.Model):
    STATUS_CHOICES = [('waiting', 'Esperando'), ('in_progress', 'En progreso'), ('finished', 'Finalizada')]
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='battles_started')
    opponent = models.ForeignKey('User', on_delete=models.CASCADE, related_name='battles_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    winner = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    user_team = models.JSONField(default=dict)
    opponent_team = models.JSONField(default=dict)


class TurnBattle(models.Model):
    ACTIONS_CHOICES = [('attack', 'Attack'), ('change_pkm', 'Change Pokemon'),('not_selected', 'Not selected')]
    current_turn=models.IntegerField()
    user_act=models.CharField(max_length=20, choices=ACTIONS_CHOICES, default='not_selected')
    opponent_act=models.CharField(max_length=20, choices=ACTIONS_CHOICES, default='not_selected')
    user_act_value = models.CharField(max_length=50, null=True, blank=True) # attack->"ice-punch"
    opp_act_value = models.CharField(max_length=50, null=True, blank=True) #  slot->"3"
    battle=models.ForeignKey('Battle', on_delete=models.CASCADE)
    resolve=models.BooleanField(default=False)