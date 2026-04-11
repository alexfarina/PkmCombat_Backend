from django.db import models


class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    encrypted_pass = models.CharField(max_length=300)
    online = models.BooleanField(default=False)
    token_sesion = models.CharField(unique=True, max_length=100)


class Moves(models.Model):
    name = models.CharField(max_length=150)
    power = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=100)
    category = models.CharField(max_length=150)
    type = models.CharField(max_length=150)


class PkmStats(models.Model):
    hp = models.IntegerField(null=True, blank=True)
    def_esp = models.IntegerField(null=True, blank=True)
    def_fis = models.IntegerField(null=True, blank=True)
    att_esp = models.IntegerField(null=True, blank=True)
    att_fis = models.IntegerField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)


class Pokemon(models.Model):
    name = models.CharField(max_length=150)
    sound = models.URLField(blank=True, null=True)
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
    slot = models.IntegerField()
    pokemon = models.ForeignKey('Pokemon', on_delete=models.SET_NULL, null=True, blank=True)


class Battle(models.Model):
    STATUS_CHOICES = [('waiting', 'Esperando'), ('in_progress', 'En progreso'), ('finished', 'Finalizada')]
    TYPE_CHOICES = [('normal', 'Normal'), ('random', 'Aleatoria')]

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='battles_started')
    opponent = models.ForeignKey('User', on_delete=models.CASCADE, related_name='battles_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    battle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='normal')
    winner = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    user_team = models.JSONField(default=dict)
    opponent_team = models.JSONField(default=dict)