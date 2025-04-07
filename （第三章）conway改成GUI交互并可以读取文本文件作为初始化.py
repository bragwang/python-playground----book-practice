'''
conway改成GUI交互，并可以读取文本文件作为初始化
注意文本文件需要在工作目录下，或者指定绝对路径

b站：
https://space.bilibili.com/153882862/lists/5107622?type=season

GitHub：
https://github.com/bragwang/python-playground----book-practice  

'''

import sys, argparse
import numpy as np
import matplotlib.pyplot as plt
from gooey import Gooey, GooeyParser
import matplotlib.animation as animation

grid = np.zeros(10*10).reshape(10, 10)  #建立一个10*10的二维数组，初始化为0

def random_grid(N):
    """
    随机地填充网格
    """ 
    print("随机地填充网格:")
    print(np.random.choice([255, 0], N*N, p=[0.2, 0.8]).reshape(N, N))
    return np.random.choice([255, 0], N*N, p=[0.2, 0.8]).reshape(N, N)

def add_glider(i, j, grid):    
    """ 在(i, j)处添加滑翔机"""
    glider = np.array([[0, 0, 255], 
                       [255, 0, 255], 
                       [0, 255, 255]])
    
    grid[i:i+3, j:j+3] = glider

def addGosperGun(i, j, grid):
    """在(i, j)处添加戈斯珀滑翔机枪，其左上角单元格位于(i, j)"""
    gun = np.zeros(11*38).reshape(11, 38)

    gun[5][1] = gun[5][2] = 255
    gun[6][1] = gun[6][2] = 255

    gun[3][13] = gun[3][14] = 255
    gun[4][12] = gun[4][16] = 255
    gun[5][11] = gun[5][17] = 255
    gun[6][11] = gun[6][15] = 255
    gun[6][17] = gun[6][18] = 255
    gun[7][11] = gun[7][17] = 255
    gun[8][12] = gun[8][16] = 255
    gun[9][13] = gun[9][14] = 255

    gun[1][25] = 255
    gun[2][23] = gun[2][25] = 255
    gun[3][21] = gun[3][22] = 255
    gun[4][21] = gun[4][22] = 255

    gun[5][21] = gun[5][22] = 255
    gun[6][23] = gun[6][25] = 255
    gun[7][25] = 255

    gun[3][35] = gun[3][36] = 255
    gun[4][35] = gun[4][36] = 255

    grid[i:i+11, j:j+38] = gun

def readPattern(filename):     #从文件中读取初始状态   输入是：文件名   输出是：二维数组
    """
    从txt文件中读取生命游戏的初始状态, 0表示空白，255表示活着
    """
     # 打开文件并读取内容
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 初始化二维矩阵
    matrix = []

    # 遍历每一行
    for line in lines:
        # 去掉行尾的换行符，并按空格分割
        row = line.strip().split()
        # 检查每一行的长度是否一致
        if matrix and len(row) != len(matrix[0]):
            raise ValueError("每一行的数据长度不一致，请检查文件格式（也不能有空行）！")
        # 将每一行转换为整数并添加到矩阵中
        matrix.append([int(value) for value in row])

    grid = np.array(matrix   )# 使用 numpy 将列表转换为二维数组
    return grid

def update(frameNum, im, grid, N):
    
    """
    更新动画
    """
    new_grid = grid.copy()
    for i in range(N):
        for j in range(N):
            total = int((grid[i, (j-1)%N] + grid[i, (j+1 )%N] +
                        grid[(i-1)%N, j] + grid[(i+ 1)%N, j] +
                        grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+ 1)%N] +
                        grid[(i+ 1)%N, (j-1)%N] + grid[(i+ 1)%N, (j+1 )%N])/ 255)
            if grid[i, j] == 255:
                    if (total < 2) or (total > 3):
                        new_grid[i, j] = 0
            else:
                if total == 3:
                    new_grid[i, j] = 255
    im.set_data(new_grid)
    grid[:] = new_grid[:]
    return im

@Gooey   #想用GUI交互，就显示这行（想用命令行参数，就注释掉这行）
def main():
    parser = GooeyParser(description='Conway康威生命游戏')                #想用GUI交互，就显示这行（想用命令行交互，就注释掉这行）
    # parser = argparse.ArgumentParser(description='Conway康威生命游戏')    #想用GUI交互，就注释掉这行（想用命令行交互，就显示这行）
                #命令行实例：python （第三章）conway改成GUI交互并可以读取文本文件作为初始化.py --N 30
    parser.add_argument('--N', type=int, default=20, help='Size of the grid（网格大小）')

    parser.add_argument('--interval', dest='interval',default=100, type=int, 
                        help='Interval between generations（世代之间的间隔,毫秒）', required=False)
    parser.add_argument('--glider', action='store_true', 
                        help='Add a glider to the grid（添加滑翔机到网格）', required=False)
    parser.add_argument('--gosper', action='store_true', 
                        help='Add a Gosper Gun to the grid（添加戈斯珀机炮到网格）', required=False)
    parser.add_argument('--yes_no', action='store_true', help='是否从文件中读取初始状态', required=False)

    parser.add_argument('--pattern', type=str, default='conway的文本文件.txt', 
                        help='Read initial state from file（从指定文件中读取初始状态）', required=False)    
    args = parser.parse_args()

  
    N = 40  # 默认网格大小
    # grid = np.array([])  
    grid = np.zeros(N*N).reshape(N, N)  # 初始化为全 0 网格

    #读取初始状态
    if args.glider:
        grid = np.zeros(N*N).reshape(N, N)  #建立一个N*N的二维数组，初始化为0
        add_glider(1, 1, grid)  #在(1,1)位置添加滑翔机
    elif args.gosper:
        grid = np.zeros(N*N).reshape(N, N)  #建立一个N*N的二维数组，初始化为0
        addGosperGun(1, 1, grid)  #在(1,1)位置添加戈斯珀机枪

    elif args.yes_no:
        #从文件中读取初始状态
        grid = readPattern(args.pattern)        
    else:
        #如果指定了N，且它是有效的，就使用N
        if args.N and args.N > 8:
            N = int(args.N)
        #随机地填充网格
        grid = random_grid(N)

    #设置动画
    fig, ax = plt.subplots()
    im = ax.imshow(grid, interpolation='nearest')    #显示网格
    print("显示了网格")
    ani = animation.FuncAnimation(fig, update, fargs=(im, grid, N),
                                  frames=100,        # 设置动画帧数
                                  interval=args.interval if args.interval else 100,)
    print("演化")
    plt.show()

if __name__ == '__main__':
    main()







