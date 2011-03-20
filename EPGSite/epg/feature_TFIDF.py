# -*- coding: utf-8 -*-
# TF-IDF特征提取，权重与特征项在文档中出现的频率成正比，与在整个语料中出现该特征项的文档数成反比
# 公式 W(i,j) = tf(i,j) * log(N/(nt + 0.01)) 
# W(i,j)是特征项i在文本j中的权重 ---------------- 分词后去除停用词每个词（每个维度）的归一化权重
# tf(i,j)是特征项i在训练文本j中出现的频度 -------- 词i在用户收视历史中出现的次数
# N是训练集中总的文档数 ------------------------ 用户收视历史条数
# nt是训练集中出现特征项t的文档数 --------------- 词t在几个用户收视历史中出现过

import math
from operator import itemgetter
from smallseg import SEG

seg = SEG()

# wlist = seg.cut(info)

def freq(word, document):
    # return document.split(None).count(word)
    cnt = 0
    wlist = seg.cut(document)
    for eachword in wlist:
        if word == eachword:
            cnt += 1
    return cnt
    
def wordCount(document):
    # return len(document.split(None))
    return len(seg.cut(document))

def numDocsContaining(word,documentList):
    count = 0
    for document in documentList:
        if freq(word,document) > 0:
            count += 1
    return count

def tf(word, document):
    return (freq(word,document) / float(wordCount(document)))

def idf(word, documentList):
    # return math.log(len(documentList) / numDocsContaining(word,documentList))
    return math.log(len(documentList) / (0.01 + numDocsContaining(word,documentList)))

def tfidf(word, document, documentList):
    return (tf(word,document) * idf(word,documentList))

if __name__ == '__main__':
    documentList = []
    documentList.append("""《焦点访谈》是中央电视台新闻评论部1994年4月1日开办的一个以深度报道为主的电视新闻评论性栏目，每期13分钟，每天19点38分在中央电视台第一套节目播出，次日8点22分在这套节目中重播。""")
    documentList.append("""节目于1978年1月1日启播，现于中央电视台综合频道（CCTV-1）、中央电视台新闻频道（CCTV-新闻）、全国各省级电视台卫星频道或第一卫星频道、部分上星城市电视台卫星频道、各城市电视台主要频道、各地方、县级电视台频道于19:00并机现场直播；中央电视台综合频道（CCTV-1）00:30、中央电视台新闻频道（CCTV-新闻）21:00、中央电视台中文国际频道（CCTV-4）02:00重播。（北京时间）""")
    documentList.append("""《共同关注》是中央电视台新闻频道惟一的一档以关注民生为宗旨的深度报道新闻专题栏目。栏目紧紧围绕“倾听民声、体察民情、反映民意”这12个字，对新近发生的与民生关系密切的热点新闻事件和热点新闻现象进行深度报道和解读。""")
    words = {}
    documentNumber = 0
    # for word in documentList[documentNumber].split(None):
    for word in seg.cut(documentList[documentNumber]):
        words[word] = tfidf(word,documentList[documentNumber],documentList)
    for item in sorted(words.items(), key=itemgetter(1), reverse=True):
        print "%f <= %s" % (item[1], item[0])
     
