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
    
def numDocsContaining(word,documentList):
    count = 0
    for document in documentList:
        if word in document:
            count += 1
    return count

def idf(word, documentList):
    return math.log(len(documentList) / (0.01 + numDocsContaining(word,documentList)))

def tfidf(document, documentList):
    retdict = {}
    for word in document:
        retdict[word] = document.count(word) / float(len(document)) * idf(word,documentList)
    return retdict
        

if __name__ == '__main__':
    seg = SEG()
    documentList = []
    documentList.append(seg.cut("""新华网布鲁塞尔3月24日电 (记者张伟)北约秘书长拉斯穆森24日晚宣布，北约成员国当天决定在利比亚设立禁飞区，北约将在数天内从美国手中接管对利比亚军事行动指挥权。
　　当天，北约28个成员国大使在布鲁塞尔举行会议，拉斯穆森在会后发表声明宣布了上述决定。
　　声明说，北约所采取的行动是“广泛国际行动的一部分”，旨在保护利比亚平民的安全。声明还说，北约成员国均致力于履行联合国安理会决议所规定的义务，“这也是北约决定承担禁飞区责任的原因”。
　　本月17日，联合国安理会通过第1973号决议，同意在利比亚设立禁飞区。从19日开始，法国、美国和英国等国对利比亚展开军事行动。目前，这一行动由美国指挥，但美方已明确表示希望在本周末把指挥权移交出去。
　　拉斯穆森24日晚在接受美国有线电视新闻网采访时说，北约已做好必要的准备，将在“未来数天内”从美国手中接管禁飞区的行动指挥权，行动将统归北约最高军事长官、欧洲盟军最高司令詹姆斯·斯塔夫里迪斯指挥。
　　拉斯穆森解释说，北约成员国目前只是决定执行设立禁飞区的任务，并正在考虑承担“更为广泛的责任”，但目前尚未做出决定。
　　北约22日决定对利比亚实施武器禁运，来自北约7个成员国的16艘海军舰艇参与这一行动。此前，土耳其、法国和德国一直反对北约在利比亚设立禁飞区，谈判一度陷入僵局。"""))
    words = {}
    for document in documentList:
        words = tfidf(document,documentList)
    for item in sorted(words.items(), key=itemgetter(1)):
        print "%s : %f" % (item[0], item[1])
     
