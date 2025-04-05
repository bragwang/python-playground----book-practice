# 类＋ontimer+gooey    生成不同形状的对数螺线（Logarithmic Spiral）
import math
import random
import turtle
from gooey import Gooey, GooeyParser

class Draw_logarithmic_Spirals:
    """生成N条形状不同的对数螺线"""
    def __init__(self, N):  #初始化
        self.N = N   #设置N条螺线 
        self.Ts = []  #存储所有螺线的turtle对象的列表
        self.As = []   #存储初始半径的列表
        self.Bs = []    #指数因子的列表
        self.steps = []  # 每条螺线绘制的步数的列表(也就是角度)
        self.x = []  #每条螺线绘制的x坐标的列表
        self.y = []  #每条螺线绘制的y坐标的列表

        self.colors = []  #存储随机选择的颜色
        all_colors = ["red", "green", "blue", "yellow", "orange", "purple"]  #设置N个颜色
        self.one_spiral_complete = False  #设置当前螺线是否完成绘制的标志
        
        for i in range(N):      #创建N个turtle对象，并将其添加到列表中
            t = turtle.Turtle()  
            t.shape("turtle")     #设置turtle的形状为
            self.Ts.append(t)  

        for i in range(N):      #随机生成N个初始半径，并将其添加到列表中
            A = random.randint(5, 50)  
            self.As.append(A)  
        print("生成的初始半径列表为：", self.As)

        for i in range(N):      #随机生成N个指数因子，并将其添加到列表中
            B = random.uniform(0.05, 0.30)     #范围是0.05-0.30
            self.Bs.append(B)  
        print("生成的指数因子列表为：", self.Bs)

        for i in range(N):       #随机选择N个颜色，并将其添加到列表中
            color = random.choice(all_colors)  
            self.colors.append(color) 
        print("随机选择的颜色列表为：", self.colors)

        for i in range(N):       #随机生成N个步数，并将其添加到列表中
            step = random.randint(10, 100)   #范围是10-50
            self.steps.append(step)  
        self.max_step = max(self.steps)  #获取最大的步数
        print("生成的步数列表为：", self.steps)
        print(f"最大的步数为{self.max_step}。")   #显示最大的步数

        for i in range(N):       #初始化每条螺线的x、y坐标列表
            x = random.randint(-300, 300)
            y = random.randint(-300, 300)
            self.x.append(x)
            self.y.append(y)
            print(f"第{i+1}条螺线的初始坐标为({x}, {y})。")          

        self.step=0  #设置初始步数
        turtle.ontimer(self.update_all_spirals, 10)  #每隔10毫秒更新一次所有螺线

    def update_all_spirals(self):    #更新所有螺线的方法
        for i in range(self.N):
            self.update_spiral(i,self.step)  #根据半径索引和新的角度更新第N个螺线

        if self.step < self.max_step:
            self.step += 1  #更新角度
            if self.step % 10 == 0:  #每隔10步打印一次当前的步数
                print(f"当前的步数为{self.step}。")
            turtle.ontimer(self.update_all_spirals, 10)  #每隔10毫秒更新一次所有螺线
        else:
            print("绘制完成！")
            turtle.mainloop()  #保持画布窗口打开
           
    def update_spiral(self, i, step): #更新第i个螺线的方法 i为螺线的索引，step为新的角度
        if step == 0:
            self.Ts[i].up()  # #抬起画笔
        if step >self.steps[i]:  #如果当前步数等于预设的步数，则说明当前螺线已经完成绘制
            return  #返回，不再绘制当前螺线
        t = self.Ts[i]  #获取第i个turtle对象
        A = self.As[i]  #获取第i个初始半径
        B = self.Bs[i]  #获取第i个指数因子
        theta =step * 0.2     # 当前角度  步数*弧度  （0.1弧度）
        radius = A * math.exp(B * theta)  # 当前半径
        x = radius * math.cos(theta) + self.x[i]  # 当前x坐标
        y = radius * math.sin(theta) + self.y[i]  # 当前y坐标
        
        self.Ts[i].color(self.colors[i])  #设置turtle的具体颜色
        try:
            self.Ts[i].goto(x, y)  #移动turtle到指定坐标
        except : 
            print("程序异常，退出")
            exit(0)


        self.Ts[i].down()  #放下画笔

@Gooey
def main():
    # 创建解析器
    parser = GooeyParser(description="请输入想要 Draw_circles 绘制的圆的数量")
    # 添加参数
    parser.add_argument("number", type=int, help="请输入数字",default=3)               #没有“--”的形式，必填参数
    # 解析参数
    args = parser.parse_args()
    #实例化对象
    # draw_circles = Draw_circles(args.number)  #括号内填入需要绘制的圆的数量
    Draw_logarithmic_Spirals(args.number)  #括号内填入需要绘制的对数螺线的数量
    turtle.done()

if __name__ == '__main__':
    main()

    