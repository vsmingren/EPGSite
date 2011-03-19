# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from datetime import datetime
from util import *


def showlist(request):
    if 'time' in request.GET and request.GET['time']:
        time = datetime.strptime(request.GET['time'], "%m/%d/%y %H:%M:%S")
        orderItems = GetAllPrograms(time)
        suggestItems = GetSuggestPrograms(orderItems)
        return render_to_response('index.html', locals())
    else:
        return render_to_response('index.html')


if __name__ == "__main__":
    #UserHistory = [1, 2, 3]
    #GetSuggestPrograms(UserHistory)
    time = datetime(2009,3,14,23,32,30)
    p = GetAllPrograms(time)
    print GetSuggestPrograms(p)
