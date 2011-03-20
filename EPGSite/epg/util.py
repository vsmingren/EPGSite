# -*- coding: utf-8 -*-
import os
from django.db.models import Q
from datetime import datetime
from EPGSite.epg.models import Program, History
from svmutil import *
from smallseg import SEG
from feature_TFIDF import *

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
    
def GetSuggestPrograms(AllPrograms):
    '从所有节目列表中选取推荐节目'
    
    # 加载汉语词典，确定词的ID作为维度
    Dictionary = {}    
    dictfile = open(os.path.join(os.path.dirname(__file__),'Dictionary').replace('\\','/'), 'r')
    list_of_all_the_lines = dictfile.readlines()
    idx = 1
    for eachline in list_of_all_the_lines:
        eachline = eachline.rstrip()
        # print eachline
        Dictionary[eachline] = idx
        idx += 1
    dictfile.close()
    
    # 加载收视历史
    documentList = []
    hlist = GetHistory()
    for item in hlist:  # 这一步只需要加载喜欢的节目
        if item.like == 1:
            documentList.append(item.programid.title + ' ' + item.programid.description) # 现用节目名称和描述的文本作为节目特征文本
    
    # 打开保存当前节目特征的文件
    featurefile = open(os.path.join(os.path.dirname(__file__),'programs.feature').replace('\\','/'), 'w')
    
    # 对于每个节目：
    for eachprogram in AllPrograms:
        
        # 初始化特征项
        words = {}
        
        # 选择特征文本
        programinfo = eachprogram.title + ' ' + eachprogram.description # 现用节目名称和描述的文本作为节目特征文本
        
        # 将特征文本进行分词
        for word in seg.cut(programinfo):
            # 计算特征权重
            words[word] = tfidf(word, programinfo, documentList) # 现在用TF-IDF方法计算特征权重
        
        # 将特征项及其权重写入
        feature = ''
        for item in words.items():
            key = str(item[0])
            if Dictionary.has_key(key):
                id = Dictionary[key]
                value = str(item[1])
                feature += u'%s:%s ' % (id, value)
            else:
                # print '%s not found in Dictionary' % item[0]
                pass
        strp = u'0 ' + feature + '\n'
        
        # 保存到特征文件中
        featurefile.write(strp)
    
    # 关闭保存当前节目特征的文件
    featurefile.close()
    
    # 加载已有用户模型
    m = svm_load_model(os.path.join(os.path.dirname(__file__),'history.model').replace('\\','/'))

    # 代入SVM
    try:
        y, x = svm_read_problem(os.path.join(os.path.dirname(__file__),'programs.feature').replace('\\','/'))
        p_label, p_acc, p_val = svm_predict(y, x, m)
    except ValueError:
        print >> sys.stderr, u'Exception here!!!'
    # print p_label
    
    # 得到结果
    result = []
    idx = 0
    for eachlabel in p_label:
        if eachlabel == 1.0:
            result.append(AllPrograms[idx])
            idx = idx + 1
    
    # 构造结果列表
    SuggestPrograms = []
    for eachprogram in result:
        SuggestPrograms.append(GetProgram(eachprogram.id))
            
    # 返回推荐列表
    return SuggestPrograms

# TBD:什么时候触发这个函数？怎么迭代？ 
def GenerateHistoryModel():
    '生成用户模型'
    # 从数据库中读出最近50条收视历史数据
    # 转换成libsvm可读的文本文件
    # y, x = svm_read_problem('../heart_scale')
    # 调整SVM参数，具体还需要看书
    # param = svm_parameter('-s 3 -c 5 -h 0')
    # 用读出的数据训练模型
    # m = svm_train(prob, param)
    # 将模型写到文件
    # svm_save_model('model_file', m)
    pass

if __name__ == "__main__":
    time = datetime(2010,8,8,8,8,8)
    p = GetAllPrograms(time)
    print GetSuggestPrograms(p)
    #print AbstractFeature(GetProgram(785))
    #historylist = GetHistory()
    #for ll in historylist:
    #    print ll
    pass
