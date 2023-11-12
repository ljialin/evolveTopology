import sys,os

# 将visualization.py, graph.py, layout.py 放置在一个文件夹中，将该文件夹的地址加入到路劲中
pwd = os.getcwd()
sys.path.append(pwd+"\\code")
import visualization


# PlayFlag: 1 -> 单个文件; 2 -> 文件夹内所有
# input:  拓扑结构信息mo文件（夹）地址
# output: 生成的中间文件以及最后的图片文件位置。图片位置：output_path/graph
# pk_path: 拓扑结构适应度值所在的pickle文件（夹）地址
# component_path：元件图片所在位置

if __name__ == '__main__':
    PlayFlag = 1

    if PlayFlag == 1:
        input= pwd + '\\data\\sample1.mo'
        output= pwd + '\\output'
        pk_path= pwd + '\\data\\sample1.pk'
        component_path = pwd + "\\component"

    if PlayFlag == 2:
        input= pwd + '\\data'
        output= pwd + '\\output'
        pk_path= pwd + '\\data'
        component_path = pwd + "\\component"

    visualization.utils(PlayFlag,input,output,pk_path,component_path)