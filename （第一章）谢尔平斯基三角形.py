import math
import turtle

def draw_triangle(x1,y1,x2,y2,x3,y3,t):
    t.up()
    t.setpos(x1,y1)
    t.down()
    t.setpos(x2,y2)
    t.setpos(x3,y3)
    t.setpos(x1,y1)
    t.up()
    
def  draw_WS_triangle(x1,y1,x2,y2,x3,y3,t):
    side = math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
    print("side是",side)
    x4 = (x1+x2)/2.0
    y4 = (y1+y2)/2.0
    x5 = (x2+x3)/2.0
    y5 = (y2+y3)/2.0
    x6 = (x1+x3)/2.0
    y6 = (y1+y3)/2.0
    if side >30 :
        draw_WS_triangle(x1,y1,x4,y4,x6,y6,t) #146三角形
        draw_WS_triangle(x4,y4,x2,y2,x5,y5,t) #425三角形
        draw_WS_triangle(x6,y6,x5,y5,x3,y3,t) #653三角形
    else:
        draw_triangle(x1,y1,x4,y4,x6,y6,t) #146三角形
        draw_triangle(x4,y4,x2,y2,x5,y5,t) #425三角形
        draw_triangle(x6,y6,x5,y5,x3,y3,t) #653三角形
        
def main():
    t=turtle.Turtle()
    draw_WS_triangle(-100, 0, 100, 0, 0, 173.2 ,t)
    turtle.Screen().exitonclick()

if __name__ == '__main__':
    main()
