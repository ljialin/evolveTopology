import graph
import layout

def utils(flag, input_path, output_path, pk_path, component_path):
    # 单个.mo文件
    # 相对路径绝对路径均可
    # 例 C:/Users/Desktop/BasePool
    graph.set_path(component_path, output_path)
    layout.set_path(component_path, output_path)

    if flag == 1:
        graph.run_graph(input_path)
        layout.run_layout(input_path, output_path, pk_path)

    # input_path目录下全部.mo文件
    # 相对路径绝对路径均可
    # 例 C:/Users/Desktop/BasePool
    if flag == 2:
        graph.run_graph_all(input_path)
        layout.run_layout_all(input_path, output_path, pk_path)
