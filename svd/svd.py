# coding=utf-8
from numpy import *
from numpy import linalg as la
import pymysql as mdb
import sys

con = mdb.connect('localhost', 'root', 'waitfor95', 'menu_score');  # 连接mysql，使用menu_score数据库
with con:
    cur = con.cursor()  # 第一步要获取连接的cursor对象，用于执行查询
    cur.execute("SELECT * FROM pre_score")  # 利用python中的执行查询函数execute，导入数据库中pre_score表中的原始评分矩阵
    rows = cur.fetchall()  # 使用fetchall函数，将结果集（多维元组）存入rows里面
    n = 11  # 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示
    m = 11
    matrix = [[0] * m for i in range(n)]
    print ("*****原始评分表")
    print ("(每一行代表一个用户，每一列代表一种菜品,数据从menu_score数据库的pre_score表格导出)")
    for j in range(0, 11):
        for i in range(1, 12):
            matrix[j][i - 1] = rows[j][i]
    for m in matrix:
        print (m)


def loadExData():
    return mat(matrix)


def exeUpdate(con, cur, sql):  # 向数据库插入数据
    sta = cur.execute(sql);
    con.commit();
    return (sta);

    # [[0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 5],                           #原始评分矩阵
    # [0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 3],
    # [0, 0, 0, 0, 4, 0, 0, 1, 0, 4, 0],
    # [3, 3, 4, 0, 0, 0, 0, 2, 2, 0, 0],
    # [5, 4, 5, 0, 0, 0, 0, 5, 5, 0, 0],
    # [0, 0, 0, 0, 5, 0, 1, 0, 0, 5, 0],
    # [4, 3, 4, 0, 0, 0, 0, 5, 5, 0, 1],
    # [0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 4],
    # [0, 0, 0, 2, 0, 2, 5, 0, 0, 1, 2],
    # [0, 0, 0, 0, 5, 0, 0, 0, 0, 4, 0],
    # [1, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0]]


'''以下是三种计算相似度的算法，分别是欧式距离、皮尔逊相关系数和余弦相似度,
注意三种计算方式的参数inA和inB都是列向量'''


def ecludSim(inA, inB):
    return 1.0 / (1.0 + la.norm(inA - inB))  # 范数的计算方法linalg.norm()，这里的1/(1+距离)表示将相似度的范围放在0与1之间


def pearsSim(inA, inB):
    if len(inA) < 3: return 1.0
    return 0.5 + 0.5 * corrcoef(inA, inB, rowvar=0)[0][
        1]  # 皮尔逊相关系数的计算方法corrcoef()，参数rowvar=0表示对列求相似度，这里的0.5+0.5*corrcoef()是为了将范围归一化放到0和1之间


def cosSim(inA, inB):
    num = float(inA.T * inB)
    denom = la.norm(inA) * la.norm(inB)
    return 0.5 + 0.5 * (num / denom)  # 将相似度归一到0与1之间


'''按照前k个奇异值的平方和占总奇异值的平方和的百分比percentage来确定k的值,
后续计算SVD时需要将原始矩阵转换到k维空间'''


def sigmaPct(sigma, percentage):
    sigma2 = sigma ** 2  # 对sigma求平方
    sumsgm2 = sum(sigma2)  # 求所有奇异值sigma的平方和
    sumsgm3 = 0  # sumsgm3是前k个奇异值的平方和
    k = 0
    for i in sigma:
        sumsgm3 += i ** 2
        k += 1
        if sumsgm3 >= sumsgm2 * percentage:
            return k


'''函数svdEst()的参数包含：数据矩阵、用户编号、物品编号和奇异值占比的阈值，
数据矩阵的行对应用户，列对应物品，函数的作用是基于item的相似性对用户未评过分的物品进行预测评分'''


def svdEst(dataMat, user, simMeas, item, percentage):
    n = shape(dataMat)[1]
    simTotal = 0.0;
    ratSimTotal = 0.0
    u, sigma, vt = la.svd(dataMat)
    k = sigmaPct(sigma, percentage)  # 确定k的值
    sigmaK = mat(eye(k) * sigma[:k])  # 构建对角矩阵
    xformedItems = dataMat.T * u[:, :k] * sigmaK.I  # 根据k的值将原始数据转换到k维空间(低维),xformedItems表示物品(item)在k维空间转换后的值
    for j in range(n):
        userRating = dataMat[user, j]
        if userRating == 0 or j == item: continue
        similarity = simMeas(xformedItems[item, :].T, xformedItems[j, :].T)  # 计算物品item与物品j之间的相似度
        simTotal += similarity  # 对所有相似度求和
        ratSimTotal += similarity * userRating  # 用"物品item和物品j的相似度"乘以"用户对物品j的评分"，并求和
    if simTotal == 0:
        return 0
    else:
        return ratSimTotal / simTotal  # 得到对物品item的预测评分


'''函数recommend()产生预测评分最高的N个推荐结果，默认返回3个；
参数包括：数据矩阵、用户编号、相似度衡量的方法、预测评分的方法、以及奇异值占比的阈值；
数据矩阵的行对应用户，列对应物品，函数的作用是基于item的相似性对用户未评过分的物品进行预测评分；
相似度衡量的方法默认用余弦相似度'''


def recommend(dataMat, user, N=3, simMeas=cosSim, estMethod=svdEst, percentage=0.9):
    unratedItems = nonzero(dataMat[user, :].A == 0)[1]  # 建立一个用户未评分item的列表
    if len(unratedItems) == 0: return 'you rated everything'  # 如果都已经评过分，则退出
    itemScores = []
    for item in unratedItems:  # 对于每个未评分的item，都计算其预测评分
        estimatedScore = estMethod(dataMat, user, simMeas, item, percentage)
        itemScores.append((item, estimatedScore))
    itemScores = sorted(itemScores, key=lambda x: x[1], reverse=True)  # 按照item的得分进行从大到小排序
    # print (itemScores)
    return itemScores[:N]  # 返回前N大评分值的item名，及其预测评分值


testdata = loadExData()

for i in range(0, 11):
    print (recommend(testdata, i))

for i in range(0, 11):
    for d in recommend(testdata, i):  # 对每个用户推荐评分较高的3件商品，并将其写入数据库guess_score表中
        sql = "insert into guess_score values(" + str(i + 1) + "," + str(d[0]) + "," + str(d[1]) + ");"
        exeUpdate(con, cur, sql);


