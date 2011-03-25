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


def freq(word, document):
    #return document.split(None).count(word)
    return document.count(word)
    #cnt = 0
    #wlist = seg.cut(document)
    #for eachword in wlist:
    #    if word == eachword:
    #        cnt += 1
    #return cnt
    
def wordCount(document):
    #return len(document.split(None))
    #return len(seg.cut(document))
    return len(document)
    
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

def tfidf(document, documentList):
    retdict = {}
    for word in document:
        retdict[word] = (tf(word,document) * idf(word,documentList))
    return retdict
        

if __name__ == '__main__':
    seg = SEG()
    documentList = []
    documentList.append(seg.cut("""《焦点访谈》是中央电视台新闻评论部1994年4月1日开办的一个以深度报道为主的电视新闻评论性栏目，每期13分钟，每天19点38分在中央电视台第一套节目播出，次日8点22分在这套节目中重播。"""))
    words = {}
    # for word in documentList[documentNumber].split(None):
    for document in documentList:
        words = tfidf(document,documentList)
    for item in sorted(words.items(), key=itemgetter(1), reverse=True):
        print "%f <= %s" % (item[1], item[0])
     
