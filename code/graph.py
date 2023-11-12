"""
文件名: graph.py
调用graphviz库生成布局
"""
import graphviz
import time
import os
import re
import shutil


# rootPath is the path including the components folder
# rootPath='E:\\work\\code' 
component_path = ""
gv_path=""


def set_path(componentpath, outputpath):
    global component_path, gv_path
    component_path = componentpath + "\\"
    gv_path = outputpath


""" 
用来找结尾元件
key (str): 元件名
value (bool): 值为false时该元件为结尾元件
"""
componentRight = dict()

"""
存储边信息
list的元素为tuple，每个tuple保存一对source和target，类型为str
[(source1, target1), (source2, target2), ...]
"""
edges = []
tail_edges = []

def readFile(filename):
    """读取编码文件，记录元件以及元件间的相连关系

    Args:
        filename (str): 文件名
    """
    tail_edges.clear()
    file = open(filename, 'r')
    while 1:
        line = file.readline()
        if not line:
            break
        if line.find('connect') != -1:
            matchObj = re.match(r'connect\((.*)\)', line.replace(' ', ''))
            source_item = matchObj.group(1).split(',')[0]
            target_item = matchObj.group(1).split(',')[1]
            source_component = source_item.split('.')[0]
            target_port = source_item.split('.')[1]
            target_component = target_item.split('.')[0]
            target_port = target_item.split('.')[1]
            # 跳过o元件
            if target_item[0] == 'O':
                tail_edges.append(source_item)
                componentRight[source_component] = False
                continue
            if source_item[0] == 'O':
                tail_edges.append(target_item)
                componentRight[target_component] = False
                continue
            # 获取线的两个端点编码，相同元件之间的连线跳过
            if source_component != target_component:
                edges.append((source_item, target_item))


    file.close()


# 找结尾元件
def findRightmost():
    """找结尾元件，即右侧没有与任何其他元件（除了O）相连的元件

    Returns:
        list(str): 用list保存所有结尾元件
    """

    rightComp = []
    for name in componentRight:
        if componentRight[name] == False:
            rightComp.append(name)

    return rightComp


def getPort(name, corner):
    """根据元件名和引脚编号返回边和节点的连接位置，同时记录右侧与其他元件相连
       的元件，方便最后查找结尾元件

    Args:
        name (str): 元件名
        corner (str): 元件引脚编号，通常为 L1, L2, R1, R2 中的一种

    Returns:
        str: 边和节点的连接位置，共有8种位置可选: nw, n ne, e, se, s, sw, w
    """

    port = ""

    if name[0] == 'H':
        if corner == 'portA':
            port = 'w'
        elif corner == 'portB':
            port = 'e'
    elif name[0] == 'N':
        if corner == 'portA':
            port = 'w'
    elif name[0] == 'C' or name[0] == 'T':
        flag1 = 0
        flag2 = 0
        if corner == "portA":
            port = "nw"
        elif corner == "spool1":
            port = "w"
        elif corner == "portB":
            port = "ne"
            flag1 = 1
        elif corner == "spool2":
            port = "e"
            flag2 = 1

    elif name[0] == 'E':
        flag1 = 0
        flag2 = 0
        if corner == "portA":
            port = "nw"
        elif corner == "portB":
            port = "sw"
        elif corner == "portC":
            port = "ne"
            flag1 = 1
        elif corner == "portD":
            port = "se"
            flag2 = 1

    elif name[0] == 'S':
        flag1 = 0
        flag2 = 0
        if corner == 'portA':
            port = 'w'
        elif corner == "portB":
            port = "ne"
            flag1 = 1
        elif corner == "portC":
            port = "se"
            flag2 = 1
    elif name[0] == 'M':
        if corner == "portA":
            port = "nw"
        elif corner == "portB":
            port = "sw"
        elif corner == "portC":
            port = "e"

    return port


def getLineColor(name, port):
    """获取边的颜色

    Args:
        name (str): 元件名
        port (str): 连接位置

    Returns:
        str: 边的颜色，如果是蓝色引脚之间相连，则为蓝色，如果是灰色引脚
             相连，则为黑色
    """

    if name[0] == 'C' or name[0] == 'T':
        if port == 'spool1' or port == 'spool2':
            return 'black'
        else:
            return 'blue'
    else:
        return 'blue'


def run_graph(file):
    startTime = time.time()

    if os.path.exists(gv_path+'\\graph_curve\\'):
        shutil.rmtree(gv_path+'\\graph_curve\\')
    os.makedirs(gv_path+'\\graph_curve\\')

    # 编码文件名
    filename = file.split('.mo')[0].split('\\')[-1]
    readFile(file)

    graphname = 'graph_curve_' + filename
    body = graphviz.Digraph(graphname, format='png')

    # 创建graph，使用dot布局，曲线相连，布局方向为从左到右
    body.attr('graph', layout='dot', ratio='fill', splines='true', overlap='false', rankdir='LR')
    body.attr('edge', weight='2', dir='none', color='blue')

    # 创建source子图，绘制I元件
    head = graphviz.Digraph('head')
    head.attr('graph', layout='dot', rank='source', rankdir='LR')

    # 可以用图片表示节点，相对路径从.gv文件所在路径开始
    nodePath = component_path
    head.node('1', label='', width='0', height='0', shape='box', color='white', image=nodePath + 'I.png')
    body.subgraph(head)

    # 画主体部分
    lineColor = ''
    for e in edges:
        if e[1][0] == 'I':
            sourceName = '1'
            sourcePort = 'e'
            lineColor = 'blue'

        else:
            sourceName = e[1].split('.')[0]
            sourceCorner = e[1].split('.')[1]
            sourcePort = getPort(sourceName, sourceCorner)
            lineColor = getLineColor(sourceName, sourceCorner)
            body.node(sourceName, label='', width='0', height='0', shape='box', color='white', image=nodePath + sourceName[0] + '.png')

        targetName = e[0].split('.')[0]
        targetCorner = e[0].split('.')[1]
        targetPort = getPort(targetName, targetCorner)
        body.node(targetName, label='', width='0', height='0', shape='box', color='white', image=nodePath + targetName[0] + '.png')

        body.edge(sourceName + ":" + sourcePort, targetName + ":" + targetPort, color=lineColor)

    # 画结尾元件 O
    rightComp = findRightmost()
    if rightComp:

        tail = graphviz.Digraph('tail')
        tail.attr('graph', layout='dot', rank='sink', rankdir='LR')

        B_label = 2
        for item in tail_edges:
            tail.node(str(B_label), '', width='0', height='0', shape='box', color='white', image=nodePath + 'O.png')
            B_label += 1

        body.subgraph(tail)

        B_label = 2
        for item in tail_edges:
            body.edge(item.split('.')[0] + ":"+getPort(item.split('.')[0],item.split('.')[1]), str(B_label) + ":w")
            B_label += 1

    # 保存gv文件
    body.save(directory=gv_path+'\\graph_curve\\')

    # # 输出并保存图片
    # body.render(directory = './graph_curve/', view = False)

    componentRight.clear()
    edges.clear()

    endTime = time.time()

    print('总用时: {:.2f}s'.format(endTime - startTime))


def run_graph_all(file_dir):
    startTime = time.time()

    if os.path.exists(gv_path+'\\graph_curve\\'):
        shutil.rmtree(gv_path + '\\graph_curve\\')
    os.makedirs(gv_path+'\\graph_curve\\')


    # 读取文件夹下所有后缀名为.mo的文件
    files_list = []
    for root, dirs, files in os.walk(file_dir):
        for f in files:
            if f.split('.')[-1]=='mo':
                files_list.append(f)

    for file in files_list:
        readFile(file_dir+'\\'+file)
        filename = file.split('.mo')[0]
        graphname = 'graph_curve_' + filename
        body = graphviz.Digraph(graphname, format='png')

        # 创建graph，使用dot布局，曲线相连，布局方向为从左到右
        body.attr('graph', layout='dot', ratio='fill', splines='true', overlap='false', rankdir='LR')
        body.attr('edge', weight='2', dir='none', color='blue')

        # 创建source子图，绘制I元件
        head = graphviz.Digraph('head')
        head.attr('graph', layout='dot', rank='source', rankdir='LR')

        # 可以用图片表示节点，相对路径从.gv文件所在路径开始
        nodePath = component_path
        head.node('1', label='', width='0', height='0', shape='box', color='white', image=nodePath + 'I.png')
        body.subgraph(head)

        # 画主体部分
        lineColor = ''
        for e in edges:
            if e[1][0] == 'I':
                sourceName = '1'
                sourcePort = 'e'
                lineColor = 'blue'
            else:
                sourceName = e[1].split('.')[0]
                sourceCorner = e[1].split('.')[1]
                sourcePort = getPort(sourceName, sourceCorner)
                lineColor = getLineColor(sourceName, sourceCorner)
                body.node(sourceName, label='', width='0', height='0', shape='box', color='white', image=nodePath + sourceName[0] + '.png')

            targetName = e[0].split('.')[0]
            targetCorner = e[0].split('.')[1]
            targetPort = getPort(targetName, targetCorner)
            body.node(targetName, label='', width='0', height='0', shape='box', color='white', image=nodePath + targetName[0] + '.png')

            body.edge(sourceName + ":" + sourcePort, targetName + ":" + targetPort, color=lineColor)

        # 画结尾元件 O
        rightComp = findRightmost()
        if rightComp:

            tail = graphviz.Digraph('tail')
            tail.attr('graph', layout='dot', rank='sink', rankdir='LR')

            B_label = 2
            for item in tail_edges:
                tail.node(str(B_label), '', width='0', height='0', shape='box', color='white', image=nodePath + 'O.png')
                B_label += 1

            body.subgraph(tail)

            B_label = 2
            for item in tail_edges:
                body.edge(item.split('.')[0] + ":"+getPort(item.split('.')[0],item.split('.')[1]), str(B_label) + ":w")
                B_label += 1

        # 保存gv文件
        body.save(directory=gv_path+'\\graph_curve\\')

        # # 输出并保存图片
        #  body.render(directory = './graph_curve/', view = False)

        componentRight.clear()
        edges.clear()

    endTime = time.time()

    print('总用时: {:.2f}s'.format(endTime - startTime))