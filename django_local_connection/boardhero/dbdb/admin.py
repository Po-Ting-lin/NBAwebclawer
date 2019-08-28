from django.contrib import admin
from dbdb.models import DateData,LeagueData,NbaPlayersData,PlayerPercentage,TeamData


# Register your models here.
admin.site.register(DateData)
admin.site.register(LeagueData)
admin.site.register(NbaPlayersData)
admin.site.register(PlayerPercentage)
admin.site.register(TeamData)
