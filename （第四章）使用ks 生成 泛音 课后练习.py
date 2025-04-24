

"""
ks 课后练习

"""
import sys, os
import time, random
import wave, argparse
import numpy as np
from collections import deque
import matplotlib
# 修复 OS X 上的图形显示问题
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import pyaudio
from gooey import Gooey, GooeyParser



# 五声音阶中的音符（小调五声音阶）
# 钢琴 C4-E(b)-F-G-B(b)-C5
pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G': 391, 'Bb': 466}

CHUNK = 1024  # 音频数据块大小

# 初始化绘图
fig, ax = plt.subplots(1)  # 创建一个绘图窗口
line, = ax.plot([], [])

# 写入 WAV 文件
def writeWAVE(fname, data):
    """将数据写入 WAV 文件。"""
    # 打开文件
    file = wave.open(fname, 'wb')
    # WAV 文件参数
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrames = 44100
    # 设置参数
    file.setparams((nChannels, sampleWidth, frameRate, nFrames,
                    'NONE', 'noncompressed'))
    file.writeframes(data)
    file.close()



# 播放 WAV 文件
class NotePlayer:
    # 构造函数
    def __init__(self):
        # 初始化 pyaudio
        self.pa = pyaudio.PyAudio()
        # 打开流
        self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True)            
        # 音符字典
        self.notes = []
    def __del__(self):
        # 析构函数
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    # 添加音符
    def add(self, fileName):
        self.notes.append(fileName)
    # 播放音符
    def play(self, fileName):
        try:
            print("正在播放 " + fileName)
            # 打开 WAV 文件
            wf = wave.open(fileName, 'rb')
            # 读取一块数据
            data = wf.readframes(CHUNK)
            # 读取剩余数据
            while data != b'':
                self.stream.write(data)
                data = wf.readframes(CHUNK)
            # 清理
            wf.close()
        except BaseException as err:
            print(f"发生异常! {err=}, {type(err)=}。\n正在退出。")
            exit(0)

    def playRandom(self):
        """播放随机音符"""
        index = random.randint(0, len(self.notes) - 1)
        note = self.notes[index]
        self.play(note)

def generateNote(freq):
    """使用 Karplus-Strong 算法生成音符。"""
    nSamples = 44100
    sampleRate = 44100
    N = int(sampleRate / freq)
    
    # if gShowPlot:  # 如果设置了图形显示标志，则初始化图形
    #     # 设置坐标轴
    #     ax.set_xlim([0, N])
        
    #     ax.set_ylim([-1.0, 1.0])
    #     line.set_xdata(np.arange(0, N))
    
    # 初始化环缓冲区
    buf = deque([random.random() - 0.5 for i in range(N)], maxlen=N)
    
    # 初始化样本缓冲区
    samples = np.array([0] * nSamples, 'float32')
    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.995 * 0.5 * (buf[0] + buf[1])
        buf.append(avg)
        # # 如果设置了图形显示标志，则绘制图形
        # if gShowPlot:
        #     if i % 1000 == 0:
        #         line.set_ydata(buf)
        #         fig.canvas.draw()
        #         fig.canvas.flush_events()
    # 将样本转换为 16 位字符串，16 位的最大值为 32767
    samples = np.array(samples * 32767, 'int16')  # 转换为 16 位整数
    # return samples.tobytes()   #注释掉，先不转化成字节格式
    return samples

def mix_notes(freq_1, freq_2): # 叠加两个音符
    """叠加两个音符"""
    samples_1 = generateNote(freq_1)
    samples_2 = generateNote(freq_2)
    
    # 打印第一个音符的频率和其对应的音频样本数据
    print(freq_1, "Hz的音频率是的数据是:")
    print(samples_1)

    # 打印第二个音符的频率和其对应的音频样本数据
    print(freq_2, "Hz的音频率是的数据是:")
    print(samples_2)

    # 叠加音频样本数据：
    # 注意：样本缓冲区的数据（即 samples_1 和 samples_2）必须在转换为字节数据之前。才能叠加数据
    mix_samples = np.array(list(map(lambda x, y: x + y, samples_1, samples_2)), 'int16')
    print("叠加后的数据是:")
    print(mix_samples)

    # 返回叠加后的音频样本数据的字节串
    return mix_samples


# 主函数
@Gooey 
def main():
    # 声明全局变量
    global gShowPlot
    parser = GooeyParser(description="使用 Karplus-Strong 算法生成声音。")
    # 添加参数

    parser.add_argument('--mix_or_not', action='store_true', default=False, help='是否要叠加音符？（课后题2')
    parser.add_argument('--mix_notes_1', action='store', required=False, widget='Dropdown', 
                        choices=list(pmNotes.keys()), default='C4', help='需要叠加的第一个音符')
    parser.add_argument('--mix_notes_2', action='store', required=False, widget='Dropdown', 
                        choices=list(pmNotes.keys()), default='G', help='需要叠加的第二个音符')
    parser.add_argument('--practice_3', action='store_true', default=False, help='课后题3')
    parser.add_argument('--read_txt_file', action='store_true', default=False, help='课后题4，读取txt文件并播放')
    parser.add_argument('--txt_file', widget='FileChooser', default='ks第4题文件.txt', help='选择文件')
    args = parser.parse_args()

    # 创建音符播放器
    nplayer = NotePlayer()

    #创建C4,Eb,F,G,Bb五个音符的wav文件
    for note in pmNotes:
        freq = pmNotes[note]
        data = generateNote(freq)
        convert_data = data.tobytes()   # 转换为字节格式
        fileName = f'{note}.wav'
        writeWAVE(fileName, convert_data)
        nplayer.add(fileName)

    if args.mix_or_not:
        # 叠加音符
        print(f"正在叠加 {args.mix_notes_1} 和 {args.mix_notes_2} 音符...")
        data=mix_notes(pmNotes[args.mix_notes_1],pmNotes[args.mix_notes_2])
        convert_data=data.tobytes()   # 转换为字节格式
        fileName = f'{args.mix_notes_1} 叠加 {args.mix_notes_2}的波形.wav'
        writeWAVE(fileName, convert_data)
        nplayer.add(fileName)
        nplayer.play(fileName)
        print(f"已生成并播放 {fileName}。")


    if args.practice_3:
        # 课后题3
        print("正在播放 C4, C4, G, Eb, F 五个音符...")
        nplayer.play('C4.wav')    # 播放 C4 音符
        nplayer.play('C4.wav')    # 播放 C4 音符
        time.sleep(1)    #等待1秒
        nplayer.play('G.wav')     # 播放 G 音符
        nplayer.play('Eb.wav')    # 播放 Eb 音符
        nplayer.play('F.wav')     # 播放 F 音符

    if args.read_txt_file:   #
        # 课后题4
        # txt中的文件是类似这样的：C42 Eb1 F2 G1 Bb2 Bb1 C42 Eb1 F2 G1  ，就一行数据，每组音符之间用空格隔开
        # 每一组音符之间用空格隔开，1和2表示时值，1表示1/4秒，2表示1/8秒，以此类推。
        #当读到C4时，播放C4.wav，当读到Eb时，播放Eb.wav，以此类推。nplayer.play(C4.wav)
        # 读取txt文件
        with open(args.txt_file, 'r') as file:
            notes_sequence = file.readline().strip().split()  # 读取一行数据，并去掉两端空格，然后以空格分割为音符序列

        # 定义时值对应的秒数
        duration_map = {
            '1': 0.5,   # 1/4拍
            '2': 0.25,  # 1/8拍
        }

        # 遍历音符序列并播放
        for note in notes_sequence:
            # 解析音符名和时值
            note_name = note[:-1]  # 获取音符名
            note_duration = note[-1]  # 获取时值
            # 打印音符信息
            print(f"正在播放 {note_name} 音符...,时值{note_duration}表示{duration_map.get(note_duration, 1)}秒")
            duration = duration_map.get(note_duration, 1)  # 获取对应的持续时间，默认为1秒

            nplayer.play(f'{note_name}.wav')  # 播放音符
            time.sleep(duration)  # 等待音符播放完毕
        print("播放完毕。")

# 调用主函数
if __name__ == '__main__':
    main()

