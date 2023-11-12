"""
文件名: layout.py
生成.gy文件来获取节点位置信息
命令: dot in.gv -Txdot -o out.gv
根据节点位置放置元件，随后使用自定义算法进行连线
"""

import os
import random
import time
import graphviz
import pickle
import shutil
from collections import defaultdict

component_path = ""
gv_path=""


def set_path(componentpath, outputpath):
    global component_path, gv_path
    component_path = componentpath + "\\"
    gv_path = outputpath


# 节点信息：nodeInfo[元件名]: [右上x坐标，右上y坐标，左上x坐标，左上y坐标，左下x坐标，左下y坐标，右下x坐标，右下y坐标
#                             中心点x坐标，中心点y坐标，左中x坐标，左中y坐标，右中x坐标，右中y坐标，节点标签]
nodeInfo = defaultdict(list)

""" 
节点对齐，每个节点只能被对齐一次
key (str): 节点名称
value (bool): true: 节点已经被对齐过，位置不能再更改
              false: 节点还没有被对齐过，可以更改位置
"""
nodeAlign = dict()

"""
保存source右侧连接target左侧的边
list中每个元素为list，保存一对source和target，类型都是str
[[sourceName1:sourcePort1, targetName1:targetPort1], [sourceName2:sourcePort2, targetName2:targetPort2], ...]
"""
eastToWestEdge = []
westToEastEdge = []  # 保存source左侧连接target右侧的边

boundingBox = []  # 保存画布尺寸 [width, height]，类型为float

ratio = 72  # 坐标转换比例，.gv文件中坐标的单位为像素，绘制时使用的坐标单位为英寸，要进行单位转换
blank_num = 1  # 隐形节点标签，用于绘制折线，每个隐形节点标签唯一




def saveNodeInfo(file, line, nodeLabel):
    """保存读取的节点信息

    Args:
        file (FILE): .gv文件的标识符
        line (list(str)): 当前文件读取到的这一行的信息，按照空格split，用list保存
        nodeLabel (int): 节点标签，用于绘制节点时区分各个节点，每个节点的标签唯一
    """

    nodeName = line[0]

    # 初始化nodeAlign
    nodeAlign[nodeName] = False
    xBias=random.uniform(-15,15)
    yBias = random.uniform(-15, 15)

    for i in range(6, 14):
        # 保存四个角坐标信息，顺序：右上，左上，左下，右下
        if(i%2==0):
            nodeInfo[nodeName].append(float(line[i])+xBias)
        else:
            nodeInfo[nodeName].append(float(line[i])+yBias)
    width = float(line[17])
    height = float(line[18])

    # 中心点
    for i in range(5):
        line = file.readline()
    line = line.lstrip()
    p = line[5:-3]
    pos = p.split(',')
    nodeInfo[nodeName].append(float(pos[0])+xBias)
    nodeInfo[nodeName].append(float(pos[1])+yBias)

    # 左侧中点，右侧中点
    nodeInfo[nodeName].append(float(pos[0]) - width / 2+xBias)
    nodeInfo[nodeName].append(float(pos[1])+yBias)
    nodeInfo[nodeName].append(float(pos[0]) + width / 2+xBias)
    nodeInfo[nodeName].append(float(pos[1])+yBias)

    # 节点标签
    nodeInfo[nodeName].append(str(nodeLabel))


def readFile(filename):
    """读取通过dot命令生成的.gv文件，记录文件中的各种信息
       包括画布尺寸，节点坐标信息，边的信息等

    Args:
        filename (str): 通过dot命令生成的.gv文件名
    """

    file = open(filename, 'r')


    # 获取画板尺寸
    line = file.readline()
    line = file.readline()
    line = line.lstrip()
    line = line.split()
    boundingBox.append(float(line[13]))
    boundingBox.append(float(line[14]))

    nodeLabel = 1

    while 1:
        line = file.readline()
        if not line:
            break

        line = line.lstrip()
        line = line.split()

        if len(line) >= 2:
            # 读取source，即开头I元件
            if line[1] == 'head':
                for i in range(5):
                    line = file.readline()
                line = line.lstrip()
                line = line.split()
                saveNodeInfo(file, line, nodeLabel)
                nodeLabel += 1

            # 读取sink，即结尾O元件，可能有多个结尾B元件
            elif line[1] == 'tail':
                for i in range(5):
                    line = file.readline()

                while 1:
                    line = line.lstrip()
                    line = line.split()
                    saveNodeInfo(file, line, nodeLabel)
                    nodeLabel += 1

                    for i in range(3):
                        line = file.readline()
                    line = line.lstrip()
                    if line[0] == '}':
                        break

            # 读取普通节点
            elif len(line[0]) == 2 and line[0][0].isalpha() and line[0][1].isdigit():
                saveNodeInfo(file, line, nodeLabel)
                nodeLabel += 1

            # 读取边
            elif line[1] == '->':
                edge = []
                e1 = line[0]
                e2 = line[2]
                # if e1[0] == 'C' or e1[0] == 'T':
                #     e1 = e1.replace('s', '')
                # if e2[0] == 'C' or e2[0] == 'T':
                #     e2 = e2.replace('s', '')

                e1_name = line[0].split(':')[0]
                e2_name = line[2].split(':')[0]

                if nodeInfo[e1_name][8] < nodeInfo[e2_name][8]:
                    edge.append(e1)
                    edge.append(e2)
                    eastToWestEdge.append(edge)
                else:
                    edge.append(e2)
                    edge.append(e1)
                    westToEastEdge.append(edge)

    file.close()


def calCoordinate(x, y, ratio):
    """坐标单位转换

    Args:
        x (float): .gv文件中的x坐标
        y (float): .gv文件中的y坐标
        ratio (int): 转换比例

    Returns:
        str: 绘制时使用的坐标，在坐标最后添加 '!' 固定节点位置
    """
    return str(x / ratio) + ',' + str(y / ratio) + '!'


# 顺序：右上，左上，左下，右下，中心点，左侧中点，右侧中点
def getNodeInfo(node):
    """获取节点信息

    Args:
        node (list(str)): 节点，包含名称和连接位置：[name, corner]

    Returns:
        list(str): [节点标签，节点名称，连接位置，连接位置的x坐标，连接位置的y坐标，连线颜色]
    """

    name = node[0]
    corner = node[1]
    label = nodeInfo[name][-1]

    if corner == 'nw':
        return [label, name, corner, nodeInfo[name][2], nodeInfo[name][3], 'blue']

    elif corner == 'w':
        if name[0] == 'P' or name[0] == 'G' or name[0] == 'C' or name[0] == 'T':
            color = 'black'
        else:
            color = 'blue'
        return [label, name, corner, nodeInfo[name][10], nodeInfo[name][11], color]

    elif corner == 'sw':
        if name[0] == 'M' or name[0] == 'E':
            color = 'blue'
        else:
            color = 'black'
        return [label, name, corner, nodeInfo[name][4], nodeInfo[name][5], color]

    elif corner == 'ne':
        return [label, name, corner, nodeInfo[name][0], nodeInfo[name][1], 'blue']

    elif corner == 'e':
        if name[0] == 'P' or name[0] == 'G' or name[0] == 'C' or name[0] == 'T':
            color = 'black'
        else:
            color = 'blue'
        return [label, name, corner, nodeInfo[name][12], nodeInfo[name][13], color]

    elif corner == 'se':
        if name[0] == 'S' or name[0] == 'E':
            color = 'blue'
        else:
            color = 'black'
        return [label, name, corner, nodeInfo[name][6], nodeInfo[name][7], color]


def drawGrid(body, width, height):
    """在图上画方格

    Args:
        body (graphvizObject): graphviz库创建的graph对象
        width (int): 方格的宽
        height (int): 方格的高
    """

    boundWidth = boundingBox[0]
    boundHeight = boundingBox[1]

    gridNum = 1

    x = 0
    while x <= boundWidth:
        y = 0
        while y <= boundHeight:
            gridName = 'grid_' + str(gridNum)
            body.node(gridName, label='', pos=calCoordinate(x, y, ratio), shape='point',
                      width='0.01', height='0.01', fixedsize='true', color='green')

            gridNum += 1
            y += height

        x += width

    return


def drawNode(body, node, nodePath, nodeLabel):
    """绘制节点

    Args:
        body (graphvizObject): graphviz库创建的graph对象
        node (str): 节点名称
        nodePath (str): 节点图片的路径
        nodeLabel ([type]): 节点标签
    """

    nodeName = node[0]
    label=node
    if nodeName[0].isdigit():
        if nodeName == '1':
            nodeName = 'I'
            label='I'
        else:
            nodeName = 'O'
            label='O'+str(eval(node)-1)

    x_pos = nodeInfo[node][8]
    y_pos = nodeInfo[node][9]
    url = component_path +'\\'+ nodeName + '.png'
    body.node(str(nodeLabel), label='', pos=calCoordinate(x_pos, y_pos, ratio), width='0', height='0',
              shape='box', color='white', image=url)
    body.node(str(nodeLabel)+'Label',label=label,pos=calCoordinate(x_pos, y_pos, ratio), width=str(16/ratio), height=str(16/ratio),fixedsize='true',
              shape='box', color='white',style='filled')


def drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor):
    """绘制折一次的折线

    Args:
        body (graphvizObeject): graphviz库创建的graph对象
        dir (str): 折线的方向，left或者right
                   right: ------ 或者 |
                          |           ------
                    left: ------ 或者      |
                               |      ------

        sLabel (str): source节点标签
        s_x (float): source的x坐标
        s_y (float): source的y坐标
        tLabel (str): target节点标签
        t_x (float): target的x坐标
        t_y (float): target的y坐标
        lineColor (str): 折线颜色
    """

    global blank_num

    if dir == 'right':
        blank_x = s_x
        blank_y = t_y

    elif dir == 'left':
        blank_x = t_x
        blank_y = s_y

    # 绘制拐点节点，随后绘制折线
    blankNode = 'blankNode' + str(blank_num)
    body.node(blankNode, label='', pos=calCoordinate(blank_x, blank_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.edge(sLabel, blankNode, color=lineColor)
    body.edge(blankNode, tLabel, color=lineColor)

    blank_num += 1


def drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor):
    """绘制折两次的折线

    Args:
        body (graphvizObeject): graphviz库创建的graph对象
        dir (str): 折线的方向，x或者y
                   x: ------
                           |
                           ------
                   y: |       或  ------   或  |    |
                      ------      |    |       ------
                           |

        tmp (float): 辅助坐标，用于绘制折线的拐点，可能是x轴坐标也可能是y轴坐标，取决于参数dir
        sLabel (str): source节点标签
        s_x (float): source的x坐标
        s_y (float): source的y坐标
        tLabel (str): target节点标签
        t_x (float): target的x坐标
        t_y (float): target的y坐标
        lineColor (str): 折线颜色
    """

    global blank_num

    if dir == 'x':
        tmp_x1 = tmp
        tmp_y1 = s_y
        tmp_x2 = tmp
        tmp_y2 = t_y

    elif dir == 'y':
        tmp_x1 = s_x
        tmp_y1 = tmp
        tmp_x2 = t_x
        tmp_y2 = tmp

    blankNode1 = 'blankNode' + str(blank_num)
    body.node(blankNode1, label='', pos=calCoordinate(tmp_x1, tmp_y1, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    blank_num += 1

    blankNode2 = 'blankNode' + str(blank_num)
    blank_num += 1
    body.node(blankNode2, label='', pos=calCoordinate(tmp_x2, tmp_y2, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)

    body.edge(sLabel, blankNode1, color=lineColor)
    body.edge(blankNode1, blankNode2, color=lineColor)
    body.edge(blankNode2, tLabel, color=lineColor)


def modifyNode(nodeName, corner, x, y):
    """调整连接位置，消除连线与引脚间的错位空隙

    Args:
        nodeName (str): 元件名
        corner (str): 连接位置
        x (float): 连接点x坐标
        y (float): 连接点y坐标

    Returns:
        list(float)): 新的连接点x，y坐标 [new_x, new_y]
    """

    # 以下元件需要调整连接位置
    needModify = ['E','M','S']
    new_x = x
    new_y = y
    if (nodeName[0] in needModify)or (nodeName[0].isdigit()):
        if(nodeName[0]=='E'):
            if corner=='nw':
                new_x +=2.5
                new_y -=9
            elif corner=='ne':
                new_x -=2.5
                new_y -=9
            elif corner == 'sw':
                new_x +=2.5
                new_y +=8.5
            else:
                new_x -=2.5
                new_y +=8.5
        elif(nodeName[0]=='M'):
            if corner=='nw':
                new_x += 2.5
                new_y -= 7
            elif corner=='sw':
                new_x += 2.5
                new_y += 7
            else:
                new_x-=2.5
        elif(nodeName[0]=='S'):
            if corner=='ne':
                new_x -= 2.5
                new_y -= 8
            elif corner=='se':
                new_x -= 2.5
                new_y += 6
            else:
                new_x+=2.5
        elif(nodeName[0]=='1'):
            new_x-=2.5
        else:
            new_x+=2.5
    else:
        if corner.find('e') != -1:
              new_x -=2.5
        if corner.find('w') != -1:
             new_x += 2.5
        if corner.find('s') != -1:
             new_y += 2.5
        if corner.find('n') != -1:
             new_y -= 2.5
    return [new_x, new_y]


def drawEastToWest(body, source, target):
    """绘制source右侧连接target左侧的连线

    Args:
        body (graphvizObject): graphviz库创建的graph对象
        source (list(str)): source节点, 包含名称和连接位置: [name, corner]
        target (list(str)): target节点, 包含名称和连接位置: [name, corner]
    """

    # 获取节点信息
    sLabel, sName, sCorner, s_x, s_y, lineColor = getNodeInfo(source)
    try:
        tLabel, tName, tCorner, t_x, t_y, lineColor = getNodeInfo(target)
    except:
        target[-1] = target[-1].split(';')[0]
        tLabel, tName, tCorner, t_x, t_y, lineColor = getNodeInfo(target)

    # 调整连接位置
    s_x, s_y = modifyNode(sName, sCorner, s_x, s_y)
    t_x, t_y = modifyNode(tName, tCorner, t_x, t_y)

    # 当连接位置y坐标相差小于阈值，且元件没有被对齐过，进行对齐
    threshold = 3
    if s_y != t_y and abs(s_y - t_y) <= threshold:
        if nodeAlign[tName] == False:
            diff = s_y - t_y
            t_y = s_y
            body.node(tLabel, pos=calCoordinate(nodeInfo[tName][8], nodeInfo[tName][9] + diff, ratio))
            nodeAlign[tName] = True

    sLabel = sName + '_' + sCorner
    ssLabel= sName+'s_'+sCorner
    tLabel = tName + '_' + tCorner
    ttLabel=tName+'t_'+tCorner
    bias1=random.uniform(3,12)
    bias2 = random.uniform(3, 12)
    count = 0
    while bias1 + bias2 >= t_x - s_x:
        bias1 = random.uniform(3, 15)
        bias2 = random.uniform(3, 15)
        count += 1
        if (count == 10):
            bias1 = 3
            bias2 = 3
            break
    # 在对应引脚坐标处绘制突出小线段 并 更新 grids
    body.node(sLabel, label='', pos=calCoordinate(s_x, s_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.node(ssLabel, label='', pos=calCoordinate(s_x+bias1, s_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.edge(sLabel,ssLabel,color=lineColor)
    body.node(tLabel, label='', pos=calCoordinate(t_x, t_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.node(ttLabel, label='', pos=calCoordinate(t_x-bias2, t_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.edge(tLabel,ttLabel,color=lineColor)


    # 在对应引脚突出小线段处绘制节点准备进行折线连线 并 更新 grids
    s_x+=bias1
    t_x-=bias2
    sLabel=ssLabel
    tLabel=ttLabel

    if s_y == t_y:
        body.edge(ssLabel + ":" + sCorner, ttLabel + ":" + tCorner, color=lineColor)

    # 右上连左
    if sCorner == 'ne':
        if s_y < t_y:
            if tCorner == 'nw':
                dir = 'right'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'w' or tCorner == 'sw':
                if t_y < boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y >= boundingBox[1] * 0.5:
                    dir = 'right'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif s_y >= t_y:
            if tCorner == 'nw' or tCorner == 'w':
                dir = 'left'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'sw':
                dir = 'x'
                tmp = (t_x + s_x) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

    # 右中连左
    elif sCorner == 'e':
        if s_y < t_y:
            if tCorner == 'nw':
                dir = 'right'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'w':
                if t_y < boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y >= boundingBox[1] * 0.5:
                    if sName[0] == 'C' or sName[0] == 'T':
                        dir = 'left'
                        drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                    else:
                        dir = 'right'
                        drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'sw':
                if t_y < boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y >= boundingBox[1] * 0.5:
                    dir = 'right'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif s_y >= t_y:
            if tCorner == 'nw':
                if t_y < boundingBox[1] * 0.5:
                    dir = 'right'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y > boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'w':

                if t_y < boundingBox[1] * 0.5:
                    if sName[0] == 'C' or sName[0] == 'T':
                        dir = 'left'
                        drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                    else:
                        dir = 'right'
                        drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y >= boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'sw':
                dir = 'right'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

    # 右下连左
    elif sCorner == 'se':
        if s_y < t_y:
            if tCorner == 'nw':
                dir = 'x'
                tmp = (t_x + s_x) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'sw' or tCorner == 'w':
                dir = 'left'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif s_y >= t_y:
            if tCorner == 'nw' or tCorner == 'w':
                if t_y < boundingBox[1] * 0.5:
                    dir = 'right'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
                elif t_y >= boundingBox[1] * 0.5:
                    dir = 'left'
                    drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            elif tCorner == 'sw':
                dir = 'right'
                drawOrtho(body, dir, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)


def drawWestToEest(body, source, target):
    """绘制source左侧连接target右侧的连线

    Args:
        body (graphvizObject): graphviz库创建的graph对象
        source (list(str)): source节点, 包含名称和连接位置: [name, corner]
        target (list(str)): target节点, 包含名称和连接位置: [name, corner]
    """

    # 获取节点信息
    sLabel, sName, sCorner, s_x, s_y, lineColor = getNodeInfo(source)
    tLabel, tName, tCorner, t_x, t_y, lineColor = getNodeInfo(target)

    # 调整连接位置
    s_x, s_y = modifyNode(sName, sCorner, s_x, s_y)
    t_x, t_y = modifyNode(tName, tCorner, t_x, t_y)

    sLabel = sName + '_' + sCorner
    ssLabel = sName + 's_' + sCorner
    tLabel = tName + '_' + tCorner
    ttLabel = tName + 't_' + tCorner
    bias1=random.uniform(3,12)
    bias2 = random.uniform(3, 12)
    count = 0
    while bias1 + bias2 >= t_x - s_x:
        bias1 = random.uniform(3, 15)
        bias2 = random.uniform(3, 15)
        count += 1
        if (count == 10):
            bias1 = 3
            bias2 = 3
            break
    ## 在对应引脚坐标处绘制突出小线段 并 更新 grids
    body.node(sLabel, label='', pos=calCoordinate(s_x, s_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.node(ssLabel, label='', pos=calCoordinate(s_x-bias1, s_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.edge(sLabel,ssLabel,color=lineColor)

    body.node(tLabel, label='', pos=calCoordinate(t_x, t_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.node(ttLabel, label='', pos=calCoordinate(t_x+bias2, t_y, ratio), shape='point',
              width='0.01', height='0.01', fixedsize='true', color=lineColor)
    body.edge(tLabel,ttLabel,color=lineColor)


    # 在对应引脚突出小线段处绘制节点准备进行折线连线 并 更新 grids
    s_x-=bias1
    t_x+=bias2
    sLabel=ssLabel
    tLabel=ttLabel

    # 左上连右
    if sCorner == 'nw':
        if tCorner == 'ne':
            dir = 'y'
            tmp = max(s_y, t_y) + 10+random.uniform(-10,10)
            drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'e':
            if s_y < t_y and abs(s_y - t_y) >= 20:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                dir = 'y'
                tmp = max(s_y, t_y) + 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'se':
            if s_y < t_y and abs(s_y - t_y) >= 20:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                # 需要绘制三段折线，还没有写对应函数
                dir = 'y'
                tmp = max(s_y, t_y) + 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

    # 左中连右
    elif sCorner == 'w':
        if tCorner == 'ne':

            if s_y > t_y and abs(s_y - t_y) >= 25:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                dir = 'y'
                tmp = max(s_y, t_y) + 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'e':
            if sName[0] == 'C' or sName[0] == 'T':
                dir = 'y'
                tmp = min(s_y, t_y) - 20+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                if abs(s_y - t_y) >= 25:
                    dir = 'y'
                    tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                    drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

                elif s_y < t_y and abs(s_y - t_y) < 25:
                    dir = 'y'
                    tmp = t_y + 20+random.uniform(-10,10)
                    drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

                elif s_y >= t_y and abs(s_y - t_y) < 25:
                    dir = 'y'
                    tmp = t_y - 20+random.uniform(-10,10)
                    drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'se':
            if s_y < t_y and abs(s_y - t_y) >= 25:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                dir = 'y'
                tmp = min(s_y, t_y) - 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

    # 左下连右
    elif sCorner == 'sw':
        if tCorner == 'ne':
            if s_y > t_y and abs(s_y - t_y) >= 20:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                # 需要绘制三段折线，还没有写对应函数
                dir = 'y'
                tmp = max(s_y, t_y) + 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'e':
            if s_y > t_y and abs(s_y - t_y) >= 20:
                dir = 'y'
                tmp = (t_y + s_y) / 2+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

            else:
                dir = 'y'
                tmp = min(s_y, t_y) - 15+random.uniform(-10,10)
                drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)

        elif tCorner == 'se':
            dir = 'y'
            tmp = min(s_y, t_y) - 10+random.uniform(-10,10)
            drawDoubleOrtho(body, dir, tmp, sLabel, s_x, s_y, tLabel, t_x, t_y, lineColor)
def read_mo(file):
    mo_file = open(file, 'r')
    lines = mo_file.readlines()
    content='{'
    countLine=0
    xMax=0
    for line in lines[2:-1]:
        if line[0:8]=='equation':
            break
        if line.find('(') != -1:
            content+=str(line.strip()[2:-2]).replace('(',':  ')+'|'
            xMax=max(xMax,len(line.strip()[2:-2]))
            countLine+=1
    content=content[0:len(content)-1]
    content+="}"
    return content,countLine,xMax

def run_layout_all(input_path,output_path,pk_path):
    startTime = time.time()

    if os.path.exists(output_path+'\\graph'):
        shutil.rmtree(output_path+'\\graph')
    
    if os.path.exists(output_path+'\\gv'):
        shutil.rmtree(output_path+'\\gv')
    
    # os.makedirs(output_path)
    os.makedirs(output_path + '\\graph')
    os.makedirs(output_path + '\\gv')
    files_list = []
    originPath = gv_path+'\\graph_curve\\'
    for root, dirs, files in os.walk(originPath):
        for f in files:
            files_list.append(f)
    # 使用graphviz库生成的布局的.gv文件路径
    for file in files_list:
        filename = file.split('.gv')[0].split('\\')[-1].split('graph_curve_')[-1]
        print(filename)
        # 运行dot命令生成包含各种信息的.gv文件，包括画布尺寸，元件坐标，边信息等
        # dot in.gv -Txdot -o out.gv
        cmd = 'dot ' + originPath + 'graph_curve_' + filename + '.gv' + ' -Txdot -o ' + output_path+'\\gv\\' + filename + '.gv'
        print(cmd)
        os.system(cmd)
        # 生成的.gv路径及文件名
        filename_gv = output_path+'\\gv\\' + filename + '.gv'
        readFile(filename_gv)

        graphname = filename
        print(graphname + '.png')
        body = graphviz.Graph(graphname, format='png')

        # 隐形节点，固定画板尺寸
        body.node('sizeNode1', label='', pos='0,0!', shape='point', width='0.01', height='0.01', fixedsize='true',
                  color='white')
        body.node('sizeNode2', label='', pos=calCoordinate(boundingBox[0], boundingBox[1], ratio),
                  shape='point', width='0.01', height='0.01', fixedsize='true', color='white')
        content, linesNum, xMax = read_mo(input_path + '\\' + filename + '.mo')

        body.node('configuration', label=content,
                  pos=calCoordinate(boundingBox[0] + 6 * xMax, boundingBox[1] / 2, ratio), shape='record',
                  width=str(8 * xMax / ratio), height=str(16 * linesNum / ratio), fixedsize='true',
                  color='black')

        with open(pk_path+"\\"+filename+'.pk', 'rb') as f:
            Objs = pickle.load(f)
        
        body.node('obj', label="Obj : [{0}, {1}]".format(Objs[5][0], Objs[5][1]),
                  pos=calCoordinate(boundingBox[0] + 6 * xMax, boundingBox[1] / 2+(16 * linesNum+16 )/2, ratio), shape='box',
                  width=str(8 * xMax / ratio), height=str(16 / ratio), fixedsize='true',fontcolor='red',
                  color='black')

        
        body.attr('graph', layout='neato', overlap='true')

        # 画格子
        # gridWidth = 2.5
        # gridHeight = 2.5
        # drawGrid(body, gridWidth, gridHeight)

        # 画元件
        nodePath = component_path
        index = 1
        for node in nodeInfo:
            drawNode(body, node, nodePath, index)
            index += 1

        # 画线，先画source右连target左，同时进行对齐操作
        for edge in eastToWestEdge:
            source = edge[0].split(':')
            target = edge[1].split(':')
            drawEastToWest(body, source, target)

        for edge in westToEastEdge:
            source = edge[0].split(':')
            target = edge[1].split(':')
            drawWestToEest(body, source, target)

        # 导出
        body.render(directory=output_path+'\\graph\\', view=False)

        nodeInfo.clear()
        eastToWestEdge.clear()
        westToEastEdge.clear()
        boundingBox.clear()
        nodeAlign.clear()

    endTime = time.time()

    print('总用时: {:.2f}s'.format(endTime - startTime))

def run_layout(file,  output_path, pk_path):

    #grids 几乎所有参数都要 除以 2.5  记得检查
    # 线段的grids更新有误差值，但是可接受
    startTime = time.time()

    if os.path.exists(output_path+'\\graph'):
        shutil.rmtree(output_path+'\\graph')
    
    if os.path.exists(output_path+'\\gv'):
        shutil.rmtree(output_path+'\\gv')

    # os.makedirs(output_path)
    os.makedirs(output_path + '\\graph')
    os.makedirs(output_path + '\\gv')

    # 使用graphviz库生成的布局的.gv文件路径
    # originPath = '.\\graph_curve\\'
    originPath = gv_path + "\\graph_curve\\"
    filename = file.split('.mo')[0].split('\\')[-1]
    # 运行dot命令生成包含各种信息的.gv文件，包括画布尺寸，元件坐标，边信息等
    # dot in.gv -Txdot -o out.gv
    cmd = 'dot ' + originPath + 'graph_curve_' + filename + '.gv' + ' -Txdot -o ' + output_path+'\\gv\\' + filename + '.gv'
    print(cmd)
    os.system(cmd)
    # 生成的.gv路径及文件名
    filename_gv = output_path+'\\gv\\' + filename + '.gv'
    readFile(filename_gv)

    graphname = filename
    print(graphname + '.png')
    body = graphviz.Graph(graphname, format='png')

    # 隐形节点，固定画板尺寸
    body.node('sizeNode1', label='', pos='0,0!', shape='point', width='0.01', height='0.01', fixedsize='true',
              color='white')
    body.node('sizeNode2', label='', pos=calCoordinate(boundingBox[0], boundingBox[1], ratio),
              shape='point', width='0.01', height='0.01', fixedsize='true', color='white')

    content, linesNum, xMax = read_mo(file)
    
    with open(pk_path, 'rb') as f:
            Objs = pickle.load(f)
        
    body.node('obj', label="Obj : [{0}, {1}]".format(Objs[5][0], Objs[5][1]),
                pos=calCoordinate(boundingBox[0] + 6 * xMax, boundingBox[1] / 2+(16 * linesNum+16 )/2, ratio), shape='box',
                width=str(8 * xMax / ratio), height=str(16 / ratio), fixedsize='true',fontcolor='red',
                color='black')

    body.node('configuration', label=content, pos=calCoordinate(boundingBox[0] + 6 * xMax, boundingBox[1] / 2, ratio),
              shape='record', width=str(8 * xMax / ratio), height=str(16 * linesNum / ratio), fixedsize='true',
              color='black')

    body.attr('graph', layout='neato', overlap='true')

    # 画格子
    # gridWidth = 2.5
    # gridHeight = 2.5
    # drawGrid(body, gridWidth, gridHeight)

    # 画元件
    nodePath = component_path
    print(nodePath)
    index = 1
    for node in nodeInfo:
        drawNode(body, node, nodePath, index)
        index += 1

    # 画线，先画source右连target左，同时进行对齐操作
    for edge in eastToWestEdge:
        source = edge[0].split(':')
        target = edge[1].split(':')
        drawEastToWest(body, source, target)

    for edge in westToEastEdge:
        source = edge[0].split(':')
        target = edge[1].split(':')
        drawWestToEest(body, source, target)

    # 导出
    body.render(directory=output_path+'\\graph\\', view=False)

    nodeInfo.clear()
    eastToWestEdge.clear()
    westToEastEdge.clear()
    boundingBox.clear()
    nodeAlign.clear()

    endTime = time.time()

    print('总用时: {:.2f}s'.format(endTime - startTime))
