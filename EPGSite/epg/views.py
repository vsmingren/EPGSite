# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from datetime import datetime
from util import *

def showlist(request):
    if 'time' in request.POST and request.POST['time']:
        time = datetime.strptime(request.POST['time'], "%m/%d/%y %H:%M:%S")
        orderItems = GetAllPrograms(time)
        suggestItems = GetSuggestPrograms(orderItems)
        return render_to_response('index.html', locals())
    else:
        return render_to_response('index.html')

def inforAction(request,id):
    program = GetProgram(id)
    content = program.description
    title = program.title
    return render_to_response('infor.html',locals());

def playAction(request,id):
    return render_to_response('play.html',locals());
