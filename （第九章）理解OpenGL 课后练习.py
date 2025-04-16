"""
simpleglfw.py
一个简单的 Python OpenGL 程序，使用 PyOpenGL 和 GLFW 库来获取 OpenGL 3.2 上下文。
作者: Mahesh    https://github.com/mkvenkit/pp2e/tree/main/simplegl
修改：brag王    https://github.com/bragwang/python-playground----book-practice



前提：
1.项目文件夹下有glutils.py这个辅助函数文件，还有star.png这个图片文件。
2.下载GLFW的库：将下载后文件中glfw3.dll文件的文件路径放在名为GLFW——Library（没有的话就新建）的环境变量中
https://www.glfw.org/download.html（我从这里下载的，选择的是Windows 64-bit binaries）
https://github.com/glfw/glfw/releases/tag/3.3.2（这应该是最新版本）
3.下载PyOpenGL的库


关键修改点
顶点着色器字符串：增加uniform int uAxis并根据uAxis选择旋转矩阵。
RenderWindow类：
增加strVS和axis参数，并在初始化时传递给Scene类。
使用OpenGL.GL模块中的glViewport、glClear等函数。
Scene类：
增加strVS和axis参数，并在初始化时编译顶点着色器和设置uAxis的uniform变量。
确保在渲染时传递uAxis和uTheta的值给顶点着色器。


注意事项：
修改glutils.py文件中：  
    将  “ imgData = numpy.array(list(img.getdata()), np.int8) ”
    改为“ imgData = numpy.array(list(img.getdata()), np.uint8) ”
    原因：
    在Windows系统下，numpy.array()函数默认返回int8类型的数据，而OpenGL要求数据类型为unsigned
"""
import OpenGL 
from OpenGL.GL import *
import numpy, math, sys, os
import glutils
import glfw
from gooey import Gooey, GooeyParser

strVS = """    //定义了一个顶点着色器（Vertex Shader）
#version 410 core

//输入变量: 
//aVert 是顶点着色器的输入变量，是一个三维的向量，代表每个顶点的位置。
//layout(location = 0) 指定了这个输入变量的位置索引，方便在应用程序中设置这个变量。
layout(location = 0) in vec3 aVert;  

uniform mat4 uMVMatrix;  // 模型视图矩阵
uniform mat4 uPMatrix;   // 投影矩阵
uniform float uTheta;    // 旋转角度
uniform int uAxis;       // 新增的变量，表示旋转轴

//输出变量: 
//vTexCoord 是顶点着色器的输出变量，是一个二维向量，
//代表每个顶点的纹理坐标。这个变量会被传递到片段着色器中使用。
out vec2 vTexCoord;

void main() {
    // rotational transform  旋转变换
    mat4 rot;
    if (uAxis == 0) {  // 如果uAxis为0，则绕x轴旋转
        rot = mat4(
            vec4(1.0, 0.0, 0.0, 0.0),
            vec4(0.0, cos(uTheta), sin(uTheta), 0.0),
            vec4(0.0, -sin(uTheta), cos(uTheta), 0.0),
            vec4(0.0, 0.0, 0.0, 1.0)
        );
    } else if (uAxis == 1) {  // 如果uAxis为1，则绕y轴旋转
        rot = mat4(
            vec4(cos(uTheta), 0.0, -sin(uTheta), 0.0),
            vec4(0.0, 1.0, 0.0, 0.0),
            vec4(sin(uTheta), 0.0, cos(uTheta), 0.0),
            vec4(0.0, 0.0, 0.0, 1.0)
        );
    } else if (uAxis == 2) {  // 绕z轴旋转
        rot = mat4(
            vec4(cos(uTheta), sin(uTheta), 0.0, 0.0),
            vec4(-sin(uTheta), cos(uTheta), 0.0, 0.0),
            vec4(0.0, 0.0, 1.0, 0.0),
            vec4(0.0, 0.0, 0.0, 1.0)
        );
    }

    // transform vertex  变换顶点
    gl_Position = uPMatrix * uMVMatrix * rot * vec4(aVert, 1.0); 
    // set texture coord  设置纹理坐标
    vTexCoord = aVert.xy + vec2(0.5, 0.5);
}
"""

def circle():  # 圆形 书上的源代码
    return  """
            #version 410 core

            in vec2 vTexCoord;

            uniform sampler2D tex2D;
            uniform bool showCircle;

            out vec4 fragColor;

            void main() {
                if (showCircle) {
                    // 如果 showCircle 为真，则片段着色器会根据纹理坐标是否在圆形区域内来决定是否显示该像素的颜色。
                    if (distance(vTexCoord, vec2(0.5, 0.5)) > 0.5) {
                        discard;
                    } else {
                        fragColor = texture(tex2D, vTexCoord);
                    }
                } else {
                    fragColor = texture(tex2D, vTexCoord);
                }
            }
            """

def Concentric_circles():  # 同心圆 书上第三题
    return  """
            #version 410 core

            in vec2 vTexCoord;

            uniform sampler2D tex2D;
            uniform bool showCircle;

            out vec4 fragColor;

            void main() {
                if (showCircle) {
                    #define M_PI 3.1415926535897932384626433832795
        
                    float r = distance(vTexCoord, vec2(0.5, 0.5));
                    if (sin(16*M_PI*r) < 0.0) {
                        discard;
                    } else {
                        fragColor = texture(tex2D, vTexCoord);
                    }
                } else {
                    fragColor = texture(tex2D, vTexCoord);
                }
            }
            """

class Scene:    
    """ OpenGL 3D 场景类"""
    def __init__(self, strFS, strVS, axis=1):
        self.strFS = strFS
        self.strVS = strVS
        self.axis = axis
        self.init_gl()

    def init_gl(self):
        # 创建着色器    传入了顶点着色器（strVS）和片段着色器（strFS）的代码字符串
        self.program = glutils.loadShaders(self.strVS, self.strFS)  #loadShaders 函数会编译这两个着色器，并将它们链接到一个OpenGL着色器程序中。

        glUseProgram(self.program)  #使用刚刚创建的着色器程序来进行渲染

        # 获取Uniform变量的位置：uPMatrix（投影矩阵）、uMVMatrix（模型视图矩阵）、tex2D（纹理）、uAxis（旋转轴）、uTheta（角度）
        self.pMatrixUniform = glGetUniformLocation(self.program, b'uPMatrix')
        self.mvMatrixUniform = glGetUniformLocation(self.program, b'uMVMatrix')
        self.tex2D = glGetUniformLocation(self.program, b'tex2D')
        self.showCircleUniform = glGetUniformLocation(self.program, b'showCircle')
        self.axisUniform = glGetUniformLocation(self.program, b'uAxis')
        self.thetaUniform = glGetUniformLocation(self.program, b'uTheta')

        # 定义三角形带顶点 
        vertexData = numpy.array(
            [-0.5, -0.5, 0.0, 
              0.5, -0.5, 0.0, 
              -0.5, 0.5, 0.0,
              0.5, 0.5, 0.0], numpy.float32)

        # 设置 顶点数组对象 (VAO)     
        self.vao = glGenVertexArrays(1) #创建一个新的VAO，用于封装 VBO 的绑定状态和顶点属性指针的配置，方便快速切换顶点数据和配置
        glBindVertexArray(self.vao)   #绑定VAO，后续的操作都将影响这个VAO。

        # 设置 顶点缓冲区（VBO）
        self.vertexBuffer = glGenBuffers(1)  #生成一个VBO，VBO用于存储顶点数据。
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)  #绑定VBO，后续的操作都将影响这个VBO。

        # 设置缓冲区数据 
        glBufferData(GL_ARRAY_BUFFER, 4*len(vertexData), vertexData, 
                     GL_STATIC_DRAW)  #将顶点数据存储到VBO中，GL_STATIC_DRAW 表示这些数据不会频繁改变。
        
        # 启用顶点数组
        glEnableVertexAttribArray(0)  #启用顶点属性数组，这里只有一个顶点属性，所以索引为0。
        # 设置缓冲区数据指针，指定如何从VBO中读取顶点数据。这里表示每个顶点有3个浮点数（x, y, z），不需要归一化，数据是紧密排列的，从第0个字节开始。
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) #
        # 解绑 VAO，表示不再使用这个VAO。
        glBindVertexArray(0)

        # 时间
        self.t = 0   #初始化一个时间变量 t，用于控制场景中物体的旋转角度。

        # 纹理
        self.texId = glutils.loadTexture('star.png')  #加载纹理，并返回纹理ID。

        # 显示圆形?
        self.showCircle = True  #初始化显示圆形的标志。

    def step(self):
        # 增加角度
        self.t = (self.t + 1) % 360

    def render(self, pMatrix, mvMatrix):        
        # 使用着色器  self.program是由顶点着色器(strVS)和片段着色器(strFS)编译并链接而成的着色器程序，用于定义如何渲染图形。
        glUseProgram(self.program)
        
        # 设置投影矩阵  GL_FALSE表示矩阵是以列为主的顺序存储的（OpenGL默认）。1表示传递一个矩阵。
        glUniformMatrix4fv(self.pMatrixUniform, 1, GL_FALSE, pMatrix)

        # 设置模型视图矩阵
        glUniformMatrix4fv(self.mvMatrixUniform, 1, GL_FALSE, mvMatrix)

        # 设置着色器角度（弧度）
        glUniform1f(self.thetaUniform, 
                    math.radians(self.t))

        # 显示圆形?
        glUniform1i(self.showCircleUniform, 
                    self.showCircle)

        # 设置旋转轴
        glUniform1i(self.axisUniform, 
                    self.axis)

        # 启用纹理 
        glActiveTexture(GL_TEXTURE0)  #选择一个纹理单元（OpenGL支持多个纹理单元）。
        glBindTexture(GL_TEXTURE_2D, self.texId) #绑定一个2D纹理到当前选择的纹理单元。self.texId是纹理的唯一标识符，通过glutils.loadTexture('star.png')加载的纹理图像。
        glUniform1i(self.tex2D, 0)   #将纹理单元0的索引传递给着色器程序中的tex2D变量。这样，着色器程序知道使用哪个纹理单元来获取纹理数据。

        # 绑定 VAO
        glBindVertexArray(self.vao)
        # 绘制
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        # 解绑 VAO
        glBindVertexArray(0)

class RenderWindow:
    """GLFW 渲染窗口类"""
    def __init__(self, strFS, strVS, axis=1):
        self.strFS = strFS
        self.strVS = strVS
        self.axis = axis

        # 获取当前工作目录  （Current Working Directory）
        cwd = os.getcwd()

        # 初始化 glfw - 这会改变 cwd
        glfw.glfwInit()
        
        # 恢复工作目录  change directory
        os.chdir(cwd)

        # 版本提示 version hint
        glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR, 4)  #major version 大版本
        glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR, 1)  #minor version 小版本
        glfw.glfwWindowHint(glfw.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)  #forward-compatible 是否开启向前兼容 
        glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE, 
                            glfw.GLFW_OPENGL_CORE_PROFILE)  #Core-profile 使用核心模式  
    
        # 创建窗口
        self.width, self.height = 800, 600
        self.aspect = self.width / float(self.height)    # 宽高比  aspect ratio
        self.win = glfw.glfwCreateWindow(self.width, self.height, 
                                         b'simpleglfw')    #window title    b 前缀表示这是一个字节串 （byte string） 
        # 使新创建的窗口成为当前的OpenGL上下文
        glfw.glfwMakeContextCurrent(self.win)
        
        # 初始化 GL
        glViewport(0, 0, self.width, self.height)  #设置了OpenGL视口的大小为窗口大小。
        glEnable(GL_DEPTH_TEST)    #启用深度测试， 以便正确处理3D场景中的遮挡关系。
        glClearColor(0.5, 0.5, 0.5, 1.0)    #设置了清屏颜色为灰色。

        # 设置窗口回调
        glfw.glfwSetKeyCallback(self.win, self.onKeyboard)

        # 创建 3D 场景  实例化了一个Scene对象，该对象包含了所有需要渲染的内容。
        self.scene = Scene(self.strFS, self.strVS, self.axis)

        # 退出标志
        self.exitNow = False

    def onKeyboard(self, win, key, scancode, action, mods):
        if action == glfw.GLFW_PRESS:
            # ESC 键退出
            if key == glfw.GLFW_KEY_ESCAPE: 
                self.exitNow = True
            else:
                # 切换显示模式
                self.scene.showCircle = not self.scene.showCircle 
        
    def run(self):
        # 初始化计时器
        glfw.glfwSetTime(0)
        t = 0.0
        while not glfw.glfwWindowShouldClose(self.win) and not self.exitNow:
            # 每 x 秒更新一次
            currT = glfw.glfwGetTime()
            if currT - t > 0.01:  # 0.1秒刷新一次
                # 更新时间
                t = currT
                # 清除
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # "|" 位运算符，表示或运算
                # 等价于：glClear(GL_COLOR_BUFFER_BIT ）  +   glClear(GL_DEPTH_BUFFER_BIT ）

                # 设置视口
                self.width, self.height = glfw.glfwGetFramebufferSize(self.win)
                self.aspect = self.width / float(self.height)
                glViewport(0, 0, self.width, self.height)
                
                # 构建投影矩阵
                pMatrix = glutils.perspective(45.0, self.aspect, 0.1, 100.0)  #投影矩阵。
                
                mvMatrix = glutils.lookAt([0.0, 0.0, -2.0], [0.0, 0.0, 0.0],
                                          [0.0, 1.0, 0.0])                    #模型视图矩阵。

                # 渲染
                self.scene.render(pMatrix, mvMatrix)

                # 更新场景
                self.scene.step()

                glfw.glfwSwapBuffers(self.win)  # 交换缓冲区 swap buffer
                # 处理和事件
                glfw.glfwPollEvents()  #处理窗口的各种事件，如按键、鼠标移动等）
        # 结束，释放资源

        glfw.glfwTerminate()

@Gooey(program_name="第九章控制OpenGL的练习题（GUI控制）")
def main():
    parser = GooeyParser(description="GUI 控制OpenGL") 
    parser.add_argument('--display_what', choices=['同心圆', '圆形'],
                         default='同心圆', help='选择显示模式')
    parser.add_argument('--rotate_what', choices=['x轴', 'y轴', 'z轴'],
                         default='y轴', help='选择旋转轴')
    args = parser.parse_args()

    # 根据选择的显示模式设置 strFS
    if args.display_what == '圆形':
        strFS = circle()
        print("你选择的是圆形")

    elif args.display_what == '同心圆':
        strFS = Concentric_circles()
        print("你选择的是同心圆")

    # 选择旋转轴
    if args.rotate_what == 'x轴':
        axis = 0
        print("你选择的是x轴旋转")
    elif args.rotate_what == 'y轴':
        axis = 1
        print("你选择的是y轴旋转")
    else:
        axis = 2
        print("你选择的是z轴旋转")

    print("开始执行示例程序。"
          "按压任意键切换显示模式，按ESC键退出。")
    rw = RenderWindow(strFS, strVS, axis=axis)  # 将axis参数传递给RenderWindow
    rw.run()

if __name__ == '__main__':
    main()

