# -*- coding: utf-8 -*-
#dddd
import os
from django.db.models import Q
from datetime import datetime
from EPGSite.epg.models import Program, History
from svmutil import *
from smallseg import SEG
from feature_TFIDF import *
from cosdistance import *
import re

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

'''
从节目库中搜索电视节目
1.分词
2.遍历所有的关键词，然后将所有搜索结果取交集
    当结果集为零时，尽量取前面关键词的交集，然后与后面交集取并集(一般靠前的关键词为用户优先选择的)
    如此迭代直到结果集不在为空
3.取前十条结果
'''    
def Search(keywords):
#1
    words = seg.cut(keywords)
    #words = [u"新闻",u"足球"]
#2
    result = []
    for word in words:
        print word
        result.append(set(Program.objects.filter(description__contains=word)))   #模糊匹配

    if result == None:
        return None;
    
    unionResult = result[0]
    for i in range(1,len(result)):
        if( len(result[i]) == 0 ):
            continue
        tmp = unionResult&result[i]
        if len(tmp) == 0:
            break
        else:
            unionResult = tmp
#3
    unionResult = list(unionResult)
    if len(unionResult) > 10:
        return unionResult[0:10]
    else:
        return unionResult
    
def GetSuggestProgramsSVM(Programs, BUILD = 1):
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

#def cosine_distance(u, v):
#    return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))

def GetSuggestPrograms(Programs, BUILD = 1):
    '从所有节目列表中选取推荐节目，BUILD是否需要重新生成历史模型(TF-IDF + VSM)'
    # 加载汉语词典，确定词的ID作为维度
    dictMain = {}    
    fileDictionary = open(os.path.join(os.path.dirname(__file__),'Dictionary').replace('\\','/'), 'r')
    listDictionaryLines = fileDictionary.readlines()
    idx = 1
    for eachline in listDictionaryLines:
        eachline = eachline.rstrip()
        # print eachline
        dictMain[eachline] = idx
        idx += 1
    fileDictionary.close()
    print >> sys.stderr,"AllWords: Dictionary Loaded."
    
    # 加载用户历史
    documentList = []
    listAllHistory = GetHistory()
    # print listAllHistory
    for eachHistory in listAllHistory: 
        if eachHistory.like == 1: # 如果是喜欢的加到documentList
            #eachHistoryInfo = seg.cut(eachHistory.programid.title + ' ' + eachHistory.programid.description) # 现用节目名称和描述的文本作为节目特征文本
            eachHistoryInfo = seg.cut(eachHistory.programid.title) # 现用节目名称作为节目特征文本
            documentList.append(eachHistoryInfo)
    print >> sys.stderr, "VSM：HistoryList Builded."
    
    if BUILD == 1: 
        # 将用户历史写入到特征文件
        fileHistoryFeature = open(os.path.join(os.path.dirname(__file__),'history.feature').replace('\\','/'),'w')
        for eachHistory in listAllHistory: 
            if eachHistory.like == 1:
                #eachHistoryInfo = seg.cut(eachHistory.programid.title + ' ' + eachHistory.programid.description) # 现用节目名称和描述的文本作为节目特征文本
                eachHistoryInfo = seg.cut(eachHistory.programid.title) # 现用节目名称作为节目特征文本
                eachHistoryVector = tfidf(eachHistoryInfo, documentList)
                feature = ''
                for item in eachHistoryVector.items():
                    key = str(item[0])
                    if dictMain.has_key(key):
                        id = dictMain[key]
                        value = str(item[1])
                        feature += u'%s:%s ' % (id, value)
                if len(feature) == 0:
                    continue
                feature += '\n'
            fileHistoryFeature.write(feature)
        fileHistoryFeature.close()
        print >> sys.stderr, "VSM：HistoryFeaturefile Created."
    # endif
    
    # 加载历史文件
    fileHistoryFeature = open(os.path.join(os.path.dirname(__file__),'history.feature').replace('\\','/'),'r')
    listFeatureLines = fileHistoryFeature.readlines()
    fileHistoryFeature.close()
    print >> sys.stderr, "VSM：HistoryFeaturefile Loaded."

    # 对于每个节目：
    print >> sys.stderr, "VSM：Calculating features and cosine distances..."
    dictDistances = {}
    for eachProgram in Programs:
        # 选择特征文本
        #eachProgramInfo = seg.cut(eachProgram.title + ' ' + eachProgram.description) # 现用节目名称和描述的文本作为节目特征文本
        eachProgramInfo = seg.cut(eachProgram.title) # 现用节目名称作为节目特征文本
        # 将特征文本变成特征向量
        eachProgramVector = tfidf(eachProgramInfo, documentList) # 现在用TF-IDF方法计算特征权重
        # 构造特征项及其权重
        dictFeature = {}
        for item in eachProgramVector.items():
            key = str(item[0])
            if dictMain.has_key(key):
                id = dictMain[key]
                value = str(item[1])
                dictFeature[int(id)] = float(value)
        if len(dictFeature) == 0:
            continue
        # print dictfeature
        
        dictEachHistory = {}
        dis = 0.0
        for eachline in listFeatureLines:
            eachline = eachline.rstrip()[:-1]
            if len(eachline) == 0:
                continue;
            items = eachline.split(' ')
            for t in items:
                key = int(t.split(':')[0])
                value = float(t.split(':')[1])
                dictEachHistory[key] = value
            dis += consine_distance(dictEachHistory, dictFeature)
        dictDistances[eachProgram.id] = dis
    print >> sys.stderr, "VSM：Features and Distance ready."    
    
    SuggestPrograms = []
    listTemp = sorted(dictDistances.items(),key = lambda d:d[1], reverse = True)
    for eachitem in listTemp:
        if eachitem[1] <= 0.0:
            continue
        program = GetProgram(int(eachitem[0]))
        SuggestPrograms.append(program)
        print "%s\t->\t%f" % (program.title, eachitem[1])
    print >> sys.stderr, "VSM: Return SuggestPrograms."    
    
    # 返回推荐列表
    return SuggestPrograms


def test1():
    time = datetime(2011,3,16,8,15,0)
    GetSuggestPrograms(GetAllPrograms(time))

def test2():
    preferlist = [13, 27, 95, 167, 179, 205, 438, 564, 571, 573, 975, 1216, 1366, 1400, 1480, 1512,
                  1580, 1623, 1669, 1864, 1905, 2077, 2215, 2225, 2381, 118, 122, 158, 294, 440, 607, 854, 921, 943, 994, 1683, 1703, 1923, 3546, 3695,
                     1779, 1930, 1934, 3670]
    for item in preferlist:
        WriteHistory(item, 1)

if __name__ == "__main__":
    test1()
    pass
