# -*- coding: utf-8 -*-
import os
from django.db.models import Q
from datetime import datetime
from EPGSite.epg.models import Program, History
from svmutil import *
from smallseg import SEG
from feature_TFIDF import *

seg = SEG()

def GetHistory():
    '返回所有历史'
    return History.objects.all()

def GetProgram(pid):
    '返回指定ID的节目'
    return Program.objects.get(id=pid)

def GetAllPrograms(time):
    '返回指定时间点所有节目'
    AllPrograms = Program.objects.filter(Q(starttime__lte=time)&Q(stoptime__gt=time))
    return AllPrograms

def WriteHistory(pid, prefer):
    History.objects.create(programid_id = pid, like = prefer)
    
def GetSuggestPrograms(Programs, BUILD = 1):
    '从所有节目列表中选取推荐节目，BUILD是否需要重新生成历史模型(TF-IDF + SVM)'
    # 加载汉语词典，确定词的ID作为维度
    Dictionary = {}    
    fileDictionary = open(os.path.join(os.path.dirname(__file__),'Dictionary').replace('\\','/'), 'r')
    listDictionary = fileDictionary.readlines()
    idx = 1
    for eachline in listDictionary:
        eachline = eachline.rstrip()
        # print eachline
        Dictionary[eachline] = idx
        idx += 1
    fileDictionary.close()
    print >> sys.stderr,"Dictionary Loaded."
    
    # 加载用户历史
    documentList = []
    listhistory = GetHistory()
    
    for eachhistory in listhistory: 
        if eachhistory.like == 1: # 如果是喜欢的加到documentList
            #eachhistoryinfo = seg.cut(eachhistory.programid.title + ' ' + eachhistory.programid.description) # 现用节目名称和描述的文本作为节目特征文本
            eachhistoryinfo = seg.cut(eachhistory.programid.title) # 现用节目名称作为节目特征文本
            documentList.append(eachhistoryinfo)
    print >> sys.stderr, "HistoryList Builded."
    
    if BUILD == 1: 
        # 将用户历史写入到特征文件
        filehistoryfeature = open(os.path.join(os.path.dirname(__file__),'history.feature').replace('\\','/'),'w')
        for eachhistory in listhistory: 
            # eachhistoryinfo = seg.cut(eachhistory.programid.title + ' ' + eachhistory.programid.description) # 现用节目名称和描述的文本作为节目特征文本
            eachhistoryinfo = seg.cut(eachhistory.programid.title) # 现用节目名称作为节目特征文本
            eachhistoryvector = tfidf(eachhistoryinfo, documentList)
            feature = ''
            for item in eachhistoryvector.items():
                key = str(item[0])
                if Dictionary.has_key(key):
                    id = Dictionary[key]
                    value = str(item[1])
                    feature += u'%s:%s ' % (id, value)
            if eachhistory.like == 1:
                feature = u'+1 ' + feature + '\n'
            else:
                feature = u'-1 ' + feature + '\n'   
            filehistoryfeature.write(feature)
        filehistoryfeature.close()
        print >> sys.stderr, "HistoryFeaturefile Created."
            
        # 将用户历史特征文件变成SVM模型
        y, x = svm_read_problem(os.path.join(os.path.dirname(__file__),'history.feature').replace('\\','/'))
        m = svm_train(y, x, '-c 4')
        
        # 保存SVM模型
        svm_save_model(os.path.join(os.path.dirname(__file__),'history.model').replace('\\','/'), m)
        print >> sys.stderr,"HistoryModel Builded."
    # endif
    
    # 打开保存当前节目特征的文件
    fileprogramfeature = open(os.path.join(os.path.dirname(__file__),'programs.feature').replace('\\','/'), 'w')
    
    # 对于每个节目：
    for eachprogram in Programs:
        # 选择特征文本
        # eachprograminfo = seg.cut(eachprogram.title + ' ' + eachprogram.description) # 现用节目名称和描述的文本作为节目特征文本
        eachprograminfo = seg.cut(eachprogram.title) # 现用节目名称作为节目特征文本
        # 将特征文本变成特征向量
        eachprogramvector = tfidf(eachprograminfo, documentList) # 现在用TF-IDF方法计算特征权重
        # 构造特征项及其权重
        feature = ''
        for item in eachprogramvector.items():
            key = str(item[0])
            if Dictionary.has_key(key):
                id = Dictionary[key]
                value = str(item[1])
                feature += u'%s:%s ' % (id, value)
        feature = u'0 ' + feature + '\n'
        # print feature
        # 写入到特征文件中
        fileprogramfeature.write(feature)
    # 关闭保存当前节目特征的文件
    fileprogramfeature.close()
    print >> sys.stderr, "ProgramFeature Loaded."
    
    # 加载已有用户模型
    m = svm_load_model(os.path.join(os.path.dirname(__file__),'history.model').replace('\\','/'))

    print >> sys.stderr, "HistoryModel Loaded."
    # 代入SVM
    try:
        y, x = svm_read_problem(os.path.join(os.path.dirname(__file__),'programs.feature').replace('\\','/'))
        p_label, p_acc, p_val = svm_predict(y, x, m)
    except ValueError:
        print >> sys.stderr, u'SVM Exception here!!!'
    print p_label
    print >> sys.stderr, "SVM Worked."
    
    # 得到结果
    result = []
    idx = 0
    for eachlabel in p_label:
        if eachlabel == 1.0:
            result.append(Programs[idx])
            idx = idx + 1
    
    # 构造结果列表
    SuggestPrograms = []
    for eachprogram in result:
        SuggestPrograms.append(GetProgram(eachprogram.id))
            
    # 返回推荐列表
    return SuggestPrograms

def test1():
    time = datetime(2011,3,16,8,15,0)
    p = GetAllPrograms(time)
    #print p
    print GetSuggestPrograms(p)

def test2():
    preferlist = [13, 27, 95, 167, 179, 205, 438, 564, 571, 573, 975, 1216, 1366, 1400, 1480, 1512,
                  1580, 1623, 1669, 1864, 1905, 2077, 2215, 2225, 2381] 
    notpreferlist = [118, 122, 158, 294, 440, 607, 854, 921, 943, 994, 1683, 1703, 1923, 3546, 3695,
                     1779, 1930, 1934, 3670]
    for item in preferlist:
        WriteHistory(item, 1)
    for item in notpreferlist:
        WriteHistory(item, -1)

if __name__ == "__main__":
    #print AbstractFeature(GetProgram(785))
    #historylist = GetHistory()
    #for ll in historylist:
    #    print ll
    test1()
    pass
