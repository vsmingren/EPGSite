# -*- coding: utf-8 -*-
from svmutil import *

if __name__ == "__main__":

    # 用收视历史数据建模,得到SVM模型
    y, x = svm_read_problem(r'history.txt')
    m = svm_train(y, x, '-c 4')
 
    y, x = svm_read_problem(r'feature.txt')
    p_label, p_acc, p_val = svm_predict(y, x, m)
    print p_label
    print p_acc
    # print p_val

    # 输出判定为喜欢(+1)的节目列表
    i = 1
    for lable in p_label:
        if lable == 1.0:
            i = i + 1
            print i, lable
    
    
