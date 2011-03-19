# -*- coding: utf-8 -*-
from django.db.models import Q
from EPGSite.epg.models import Program
from svmutil import *
from smallseg import SEG
import os

seg = SEG()
DictWF = {}

def GetProgram(pid):
    '返回指定ID的节目'
    return Program.objects.get(id=pid)

def GetAllPrograms(time):
    '返回指定时间点所有节目'
    AllPrograms = Program.objects.filter(Q(starttime__lte=time)&Q(stoptime__gt=time))
    return AllPrograms

# 特征提取，这部分需要针对策略进行替换和改写
def AbstractFeature(program):
    '返回一个节目的特征'
    info = program.title + ' ' + program.description
    print >> sys.stderr, info
    wlist = seg.cut(info)
    wdict = {}
    # TBD: slot 是针对时间段特征的 
    # wdict[DictWF[slot]] = 1
    for word in wlist:
        if word in DictWF:
            # print word, u' yes.'
            wdict[DictWF[word]] = 1
        else:
            # print word, u' no.'
            pass
        
    ret = u''
    for key in wdict.keys():
        ret += u'%s:%s ' % (key, wdict[key])
    return u'%s' % ret

# TBD:怎么把这部分移动到整个系统启动时运行
def LoadFeatureDict():
    print >> sys.stderr, u'Loading wdf.dic...'
    f = open(os.path.join(os.path.dirname(__file__),'wdf.dic').replace('\\','/'), 'r')
    allLines = f.readlines()
    f.close()
    idx = 1
    for eachLine in allLines:
        wd = eachLine.split('\t')[0].decode('utf-8')
        DictWF[wd] = idx
        idx = idx + 1
    print >> sys.stderr, u'wdf.dic ok.'
    
def GetSuggestPrograms(AllPrograms):
    '从所有节目列表中选取推荐节目'
    # 加载分词词典
    LoadFeatureDict()
    
    featurefile = open(os.path.join(os.path.dirname(__file__),'listnow.data').replace('\\','/'), 'w')
    # 对于每个节目：
    for eachprogram in AllPrograms:
        # 提取特征
        feature = AbstractFeature(eachprogram)
        strp = u'0 ' + feature + '\n'
        # 保存到特征文件中
        featurefile.write(strp)
    featurefile.close()
    
    # 加载已有用户模型
    m = svm_load_model(os.path.join(os.path.dirname(__file__),'history.model').replace('\\','/'))

    # 代入SVM
    try:
        y, x = svm_read_problem(os.path.join(os.path.dirname(__file__),'listnow.data').replace('\\','/'))
        p_label, p_acc, p_val = svm_predict(y, x, m)
    except ValueError:
        print >> sys.stderr, u'Exception here!!!'
    print p_label
    
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