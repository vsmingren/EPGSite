import math

def dot(v1, v2):
    n1 = len(v1)
    n2 = len(v2)
    if n1 != n2:
        print 'ERROR, Vectors diff...'
    
    ret = 0.0
    for i  in range(0, n1):
        ret += v1[i] * v2[i]
    return ret

def norm(v):
    ret = 0.0
    for x in v:
        ret += (x * x)
    if ret == 0:
        print 'Warning.. norm returned zero'
    return math.sqrt(ret)

def consine_distance(d1, d2):
    N = 6929
    v1 = []
    v2 = []
    for i in range(1, N):
        if d1.has_key(i):
            v1.append(d1[i])
        else:
            v1.append(0)
            
        if d2.has_key(i):
            v2.append(d2[i])
        else:
            v2.append(0)
    return float(dot(v1, v2) / (norm(v1) * norm(v2)))

if __name__ == "__main__":
#    v1 = [30, 20, 20, 10, 0]
    d1 = {1:30, 2:20, 3:20, 4:10}
#    v2 = [40, 0, 30, 20, 10]
    d2 = {1:40, 3:30, 4:20, 5:10}
    print consine_distance(d1, d2)

