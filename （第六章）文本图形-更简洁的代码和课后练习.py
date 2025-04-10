"""
python极客项目 第六章 图像转换为ASCII字符画
本程序实现将图像转换为ASCII字符画，并且实现了课后练习题。
比源代码更简洁

b站：
https://space.bilibili.com/153882862/lists/5107622?type=season

GitHub：
https://github.com/bragwang/python-playground----book-practice 

author：bragwang
"""
import sys, random, argparse
import numpy as np
import math
from PIL import Image
from gooey import Gooey, GooeyParser

gscale1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
gscale2 =  '@%#*+=-:. '
gscale3 =  "@$%^'."

# 计算图像的平均亮度
def getAverageL(image):    
    """
    给定PIL图像，返回灰度值的平均值
    """
    im_arr = np.array(image)  # 将图像转换为数组
    average_l = np.mean(im_arr)# 计算平均亮度
    return average_l

def convertImageToAscii(fileName, cols, scale, moreLevels, invert, custom_chars):
    """
    给定图像和尺寸（行，列），返回一个m*n的图像字符列表
    """
    global gscale1, gscale2, gscale3   #声明全局变量   
    image = Image.open(fileName).convert('L')  # 打开图像文件并转换为灰度图像
    width, height = image.size     #获取图像的宽度和高度
    tile_width = width // cols  #计算瓦片的宽度
    tile_height = int(tile_width / scale)    #计算瓦片的高度        #scale = tile_width / tile_height
    rows = int(height / tile_height)   #计算行数 （列数是cols）
    
    print("图像文件：", fileName)
    print("图像尺寸：", width, height)
    print("瓦片尺寸：", tile_width, tile_height)
    print("行数：", rows)
    print("列数：", cols)
    
    ascii_image = []   #创建空列表    
    #遍历行
    for i in range(rows):
        #创建空字符串
        row = ""
        #遍历列
        for j in range(cols):
            #计算瓦片的左上角坐标
            x = j * tile_width
            y = i * tile_height
            #裁剪图像
            tile = image.crop((x, y, x + tile_width, y + tile_height))
            #计算瓦片的平均亮度
            average_l = getAverageL(tile)
            # print("平均亮度：", average_l)
            # print(type(average_l))

            #根据平均亮度计算字符
            if moreLevels:    #如果选择了更多的灰度级别
                if invert:    #如果选择了反转
                    char = gscale1[-int((average_l * 69) / 255)]
                else:
                    char = gscale1[int((average_l * 69) / 255)]
            else:              #使用默认的灰度级别
                if invert:
                    char = gscale2[-int((average_l * 9) / 255)]     #9
                else:
                    char = gscale2[int((average_l * 9) / 255)]

            if custom_chars:    #如果输入了自定义字符
                num = len(custom_chars)
                # print(num)
                if invert:
                    char = custom_chars[-int((average_l * (num-1)) / 255)]
                else:
                    char = custom_chars[int((average_l * (num-1)) / 255)]

            #添加字符到行字符串
            row += char
        #添加行字符串到图像列表
        ascii_image.append(row)
    
    return ascii_image

@Gooey(program_name="ASCII Art", default_size=(600, 650))
def main():
        # 创建解析器
        parser = GooeyParser(description="ASCII Art")
        # 添加参数
        parser.add_argument("image_file", widget="FileChooser", default="要上传的图像.png", help="选择要转换的图像文件")
        parser.add_argument("cols", type=int, default=80, help="设置每行的字符数")
        parser.add_argument("scale", type=float, default=0.43, help="设置缩放比例")
        parser.add_argument("--more_levels", action="store_true", help="使用更多的灰度级别")
        parser.add_argument("--invert", action="store_true", help="反转图像")
        parser.add_argument("--custom_chars", type=str, default='', help="输入指定字符(不是必填）推荐：【@$%^'.】")                   
        parser.add_argument("--output_file", widget="FileSaver", default="输出的文件.txt", help="设置输出文件名")
        # 解析参数
        args = parser.parse_args()

        # 设置输出文件名
        output_file =  args.output_file if args.output_file else args.image_file.split('.')[0] + '.txt'

        # 调用转换函数
        ascii_image = convertImageToAscii(args.image_file, args.cols, args.scale, args.more_levels, args.invert, args.custom_chars)
        
        # 打开文件
        with open(output_file, 'w') as f:
            # 遍历图像列表
            for row in ascii_image:
                f.write(row + '\n')
            print("转换完成，输出文件：", output_file)

if __name__ == '__main__':    
    main()
