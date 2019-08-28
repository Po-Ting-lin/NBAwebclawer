# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BaselineOfEachPlayer(models.Model):
    name = models.CharField(db_column='Name', primary_key=True, max_length=40)  # Field name made lowercase.
    ontime = models.FloatField(blank=True, null=True)
    pts = models.FloatField(db_column='PTS', blank=True, null=True)  # Field name made lowercase.
    orb = models.FloatField(db_column='ORB', blank=True, null=True)  # Field name made lowercase.
    drb = models.FloatField(db_column='DRB', blank=True, null=True)  # Field name made lowercase.
    ast = models.FloatField(db_column='AST', blank=True, null=True)  # Field name made lowercase.
    stl = models.FloatField(db_column='STL', blank=True, null=True)  # Field name made lowercase.
    blk = models.FloatField(db_column='BLK', blank=True, null=True)  # Field name made lowercase.
    fga = models.FloatField(db_column='FGA', blank=True, null=True)  # Field name made lowercase.
    fgm = models.FloatField(db_column='FGM', blank=True, null=True)  # Field name made lowercase.
    fta = models.FloatField(db_column='FTA', blank=True, null=True)  # Field name made lowercase.
    ftm = models.FloatField(db_column='FTM', blank=True, null=True)  # Field name made lowercase.
    tpa = models.FloatField(db_column='TPA', blank=True, null=True)  # Field name made lowercase.
    tpm = models.FloatField(db_column='TPM', blank=True, null=True)  # Field name made lowercase.
    tov = models.FloatField(db_column='TOV', blank=True, null=True)  # Field name made lowercase.
    pf = models.FloatField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    plusminus = models.FloatField(blank=True, null=True)
    aper = models.FloatField(db_column='aPER', blank=True, null=True)  # Field name made lowercase.
    per = models.FloatField(db_column='PER', blank=True, null=True)  # Field name made lowercase.
    eff = models.FloatField(db_column='EFF', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Baseline_of_each_player'


class NbaPlayersData(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=40, blank=True, null=True)
    team = models.CharField(max_length=5, blank=True, null=True)
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    month = models.IntegerField(db_column='Month', blank=True, null=True)  # Field name made lowercase.
    day = models.IntegerField(db_column='Day', blank=True, null=True)  # Field name made lowercase.
    ontime = models.FloatField(blank=True, null=True)
    pts = models.FloatField(db_column='PTS', blank=True, null=True)  # Field name made lowercase.
    orb = models.FloatField(db_column='ORB', blank=True, null=True)  # Field name made lowercase.
    drb = models.FloatField(db_column='DRB', blank=True, null=True)  # Field name made lowercase.
    ast = models.FloatField(db_column='AST', blank=True, null=True)  # Field name made lowercase.
    stl = models.FloatField(db_column='STL', blank=True, null=True)  # Field name made lowercase.
    blk = models.FloatField(db_column='BLK', blank=True, null=True)  # Field name made lowercase.
    fga = models.FloatField(db_column='FGA', blank=True, null=True)  # Field name made lowercase.
    fgm = models.FloatField(db_column='FGM', blank=True, null=True)  # Field name made lowercase.
    fta = models.FloatField(db_column='FTA', blank=True, null=True)  # Field name made lowercase.
    ftm = models.FloatField(db_column='FTM', blank=True, null=True)  # Field name made lowercase.
    tpa = models.FloatField(db_column='TPA', blank=True, null=True)  # Field name made lowercase.
    tpm = models.FloatField(db_column='TPM', blank=True, null=True)  # Field name made lowercase.
    tov = models.FloatField(db_column='TOV', blank=True, null=True)  # Field name made lowercase.
    pf = models.FloatField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    plusminus = models.FloatField(blank=True, null=True)
    aper = models.FloatField(db_column='aPER', blank=True, null=True)  # Field name made lowercase.
    per = models.FloatField(db_column='PER', blank=True, null=True)  # Field name made lowercase.
    eff = models.FloatField(db_column='EFF', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Nba_players_data'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BestData(models.Model):
    best = models.CharField(primary_key=True, max_length=10)
    bestname = models.CharField(max_length=40, blank=True, null=True)
    data = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'best_data'


class DateData(models.Model):
    today = models.CharField(primary_key=True, max_length=5)
    data0 = models.CharField(max_length=5, blank=True, null=True)
    data1 = models.CharField(max_length=5, blank=True, null=True)
    data2 = models.CharField(max_length=5, blank=True, null=True)
    data3 = models.CharField(max_length=5, blank=True, null=True)
    data4 = models.CharField(max_length=5, blank=True, null=True)
    data5 = models.CharField(max_length=5, blank=True, null=True)
    data6 = models.CharField(max_length=5, blank=True, null=True)
    data7 = models.CharField(max_length=5, blank=True, null=True)
    data8 = models.CharField(max_length=5, blank=True, null=True)
    data9 = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'date_data'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class LeagueData(models.Model):
    league = models.CharField(primary_key=True, max_length=10)
    fgm_per_g = models.FloatField(blank=True, null=True)
    fga_per_g = models.FloatField(blank=True, null=True)
    ftm_per_g = models.FloatField(blank=True, null=True)
    fta_per_g = models.FloatField(blank=True, null=True)
    pts_per_g = models.FloatField(blank=True, null=True)
    ast_per_g = models.FloatField(blank=True, null=True)
    orb_per_g = models.FloatField(blank=True, null=True)
    drb_per_g = models.FloatField(blank=True, null=True)
    tov_per_g = models.FloatField(blank=True, null=True)
    pf_per_g = models.FloatField(blank=True, null=True)
    pace = models.FloatField(blank=True, null=True)
    factor = models.FloatField(blank=True, null=True)
    vop = models.FloatField(db_column='VOP', blank=True, null=True)  # Field name made lowercase.
    drbp = models.FloatField(db_column='DRBP', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'league_data'


class PlayerPercentage(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=40, blank=True, null=True)
    time_length = models.IntegerField(db_column='time length', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    pts = models.FloatField(db_column='PTS', blank=True, null=True)  # Field name made lowercase.
    ast = models.FloatField(db_column='AST', blank=True, null=True)  # Field name made lowercase.
    stl = models.FloatField(db_column='STL', blank=True, null=True)  # Field name made lowercase.
    blk = models.FloatField(db_column='BLK', blank=True, null=True)  # Field name made lowercase.
    fga = models.FloatField(db_column='FGA', blank=True, null=True)  # Field name made lowercase.
    fgm = models.FloatField(db_column='FGM', blank=True, null=True)  # Field name made lowercase.
    fta = models.FloatField(db_column='FTA', blank=True, null=True)  # Field name made lowercase.
    ftm = models.FloatField(db_column='FTM', blank=True, null=True)  # Field name made lowercase.
    tpa = models.FloatField(db_column='TPA', blank=True, null=True)  # Field name made lowercase.
    tpm = models.FloatField(db_column='TPM', blank=True, null=True)  # Field name made lowercase.
    orb = models.FloatField(db_column='ORB', blank=True, null=True)  # Field name made lowercase.
    drb = models.FloatField(db_column='DRB', blank=True, null=True)  # Field name made lowercase.
    tov = models.FloatField(db_column='TOV', blank=True, null=True)  # Field name made lowercase.
    pf = models.FloatField(db_column='PF', blank=True, null=True)  # Field name made lowercase.
    plusminus = models.FloatField(blank=True, null=True)
    aper = models.FloatField(db_column='aPER', blank=True, null=True)  # Field name made lowercase.
    per = models.FloatField(db_column='PER', blank=True, null=True)  # Field name made lowercase.
    eff = models.FloatField(db_column='EFF', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'player percentage'


class TeamData(models.Model):
    team = models.CharField(primary_key=True, max_length=7)
    mp_per_g = models.FloatField(blank=True, null=True)
    ast_per_g = models.FloatField(blank=True, null=True)
    fgm_per_g = models.FloatField(blank=True, null=True)
    fga_per_g = models.FloatField(blank=True, null=True)
    fta_per_g = models.FloatField(blank=True, null=True)
    orb_per_g = models.FloatField(blank=True, null=True)
    drb_per_g = models.FloatField(blank=True, null=True)
    tov_per_g = models.FloatField(blank=True, null=True)
    tmposs = models.FloatField(db_column='tmPOSS', blank=True, null=True)  # Field name made lowercase.
    oppposs = models.FloatField(db_column='oppPOSS', blank=True, null=True)  # Field name made lowercase.
    tmpace = models.FloatField(db_column='tmPACE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'team_data'
