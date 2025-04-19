#1.程序开头添加：  from gooey import Gooey, GooeyParser               版本：20250419
#2.在主函数前面添加：  @Gooey 
#3.在主函数中，把  argparse.ArgumentParser() 替换为  GooeyParser()


# ....................................................
# 示例:
from gooey import Gooey, GooeyParser

# 主函数
@Gooey 
def main():
    # parser = argparse.ArgumentParser(description="我能干什么？") # 原来代码
    parser = GooeyParser(description="我能干什么？")   # 替换为GooeyParser
    parser.add_argument('must_have', default='有字就行',type=str, help='必须有的参数')    #没有“--”
    parser.add_argument('--name', default='张三',type=str, help='你叫什么名字？')
    parser.add_argument('--yes_no', action='store_true', default=False, help='是否将信息写入指定文件？')
    parser.add_argument('--instrument', choices=['钢琴', '古筝'],
                         default='钢琴', help='选择音色')
    parser.add_argument('--file', widget='FileChooser', default='默认文件夹/默认文件.txt', help='选择文件')
    
# ..........................................................



    args = parser.parse_args()
    if not args.must_have:
        print("必须输入参数！")
        exit()  
    else:
        print("您输入的必填参数为：" + args.must_have)

    if args.name:
        print("你好，" + args.name + "！")
    else:
        print("你好,你没有输入名字！")

    if args.instrument == '钢琴':
       print("你选择的是钢琴")
    elif args.instrument == '古筝':
        print("你选择的是古筝")


    if args.yes_no:       # 增加判断是否写入文件
        if args.file:    
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write("姓名：" + args.name + "\n",)
                f.write("音色：" + args.instrument + "\n")
                f.write("是否写入文件：" + str(args.yes_no))
            print("信息写入指定文件成功！")
        else:
            print("请选择写入文件的路径！")
       
    else:
        print("信息没有写入指定文件！")



    
    print("                程序结束")

if __name__ == '__main__':
    main()