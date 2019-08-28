from django.shortcuts import render
import random
#import database table
from dbdb.models import NbaPlayersData, DateData, PlayerPercentage, BestData
#paginator
from db_connection.config import pagination
#search bar
from django.db.models import Q



def main_page(request):
    template = 'homepage.html'
    ## show all players
    try:
        lg = NbaPlayersData.objects.all()
    except Exception:
        error = "cannot read it!"
    try:
        time = DateData.objects.get(today="today")
    except:
        pass
    ## paginator
    items = pagination(request, lg, 10)

    ## search
    ran = random.randint(0,len(NbaPlayersData.objects.all()))
    random_guy = NbaPlayersData.objects.all()[ran-1]

    # use search to filter some nba players
    query = request.GET.get('q')

    # if there are a search command

    # init meanlist
    meanlist = PlayerPercentage.objects.all()[3]
    lines = 'No one'
    if query:
        lines = str(query)

        # find it
        try:
            meanlist = PlayerPercentage.objects.filter(Q(name=query) & Q(time_length=1)).first()
            meanlist_base = PlayerPercentage.objects.filter(Q(name='all')).first()
        # Cannot find it
        except:
            meanlist = None
            meanlist_base = None
            lines = 'Cannot find this player in Database!'
    else:
        meanlist = None
        meanlist_base = None
    ## show what time is this!
    try:
        time = DateData.objects.get(today="today")
    except:
        pass

    ## time lapse data
    try:
        tld = NbaPlayersData.objects.filter(Q(name=query) & Q(year=2019))
    except:
        tld = None

    ## league average
    lg_mean = PlayerPercentage.objects.filter(Q(name='all')).first()
    if lg_mean:
        lg_error = ''
    else:
        lg_error = 'cannot find data!'

    # line plot
    lineplot1 = None
    lineplot2 = None
    lineplot3 = None
    lineplot4 = None
    lineplot5 = None
    try:
        lineplot1 = NbaPlayersData.objects.filter(Q(name=query)).order_by('id')[0]
    except:
        pass
    try:
        lineplot2 = NbaPlayersData.objects.filter(Q(name=query)).order_by('id')[1]
    except:
        pass
    try:
        lineplot3 = NbaPlayersData.objects.filter(Q(name=query)).order_by('id')[2]
    except:
        pass
    try:
        lineplot4 = NbaPlayersData.objects.filter(Q(name=query)).order_by('id')[3]
    except:
        pass
    try:
        lineplot5 = NbaPlayersData.objects.filter(Q(name=query)).order_by('id')[4]
    except:
        pass

    ## Best Record
    pts_best = BestData.objects.get(best='PTS')
    ast_best = BestData.objects.get(best='AST')
    blk_best = BestData.objects.get(best='BLK')
    tov_best = BestData.objects.get(best='TOV')
    eff_best = BestData.objects.get(best='EFF')
    per_best = BestData.objects.get(best='PER')


    #output
    context = {
        'lg': lg,
        'time': time,
        'items': items,
        'random_guy': random_guy,
        'lines': lines,
        'meanlist': meanlist,
        'meanlist_base': meanlist_base,
        'lg_mean': lg_mean,
        'lg_error': lg_error,
        'pts_best': pts_best,
        'ast_best': ast_best,
        'blk_best': blk_best,
        'tov_best': tov_best,
        'eff_best': eff_best,
        'per_best': per_best,
        'tld': tld,
        'lineplot1': lineplot1,
        'lineplot2': lineplot2,
        'lineplot3': lineplot3,
        'lineplot4': lineplot4,
        'lineplot5': lineplot5,
    }
    return render(request, template, context)

