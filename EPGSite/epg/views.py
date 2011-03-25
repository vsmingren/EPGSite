# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from datetime import datetime
from util import *

def showlist(request):
    if 'time' in request.POST and request.POST['time']:
        time = datetime.strptime(request.POST['time'], "%m/%d/%Y %H:%M:%S")
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


'''
本页面的功能选择喜欢、厌恶的电视节目
    1.随机产生时间，根据这个时间返回当前节目列表
'''
def showPro(request):
    time = "2011-03-18 09:00:00"    
    items = GetAllPrograms(time)    
    return render_to_response('showProgram.html',locals())

'''
存取用户挑选的喜欢和厌恶的电视节目
'''
def selFav(request):
    if 'like' in request.POST and request.POST['like']:
        like = request.REQUEST.getlist("like")
        for i in like:
            WriteHistory(i,1);
    else:
        print 'no like item'
    
    if 'hate' in request.POST and request.POST['hate']:
        hate = request.REQUEST.getlist("hate")
        for i in hate:
            WriteHistory(i,-1)
    else:
        print 'no hate item'
    
    return showPro(request)

