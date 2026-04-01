from django.contrib import admin

# Register your models here.
from .models import User, PkmMoves, PkmStats, Pokemon, Moves , Battle, Team

admin.site.register(Team)
admin.site.register(User)
admin.site.register(PkmStats)
admin.site.register(PkmMoves)
admin.site.register(Pokemon)
admin.site.register(Moves)
admin.site.register(Battle)