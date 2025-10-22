import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 创建一个简单的预览图像
width, height = 760, 1200
image = Image.new('RGB', (width, height), color=(135, 206, 235))  # 天空蓝

# 创建绘图对象
draw = ImageDraw.Draw(image)

# 绘制天空中的云朵
for i in range(3):
    x = 100 + i * 200
    y = 100 + i * 50
    draw.ellipse([x, y, x+80, y+40], fill=(255, 255, 255))
    draw.ellipse([x+30, y-20, x+110, y+20], fill=(255, 255, 255))

# 绘制太阳
draw.ellipse([width-150, 80, width-50, 180], fill=(255, 255, 0))

# 绘制草地
draw.rectangle([0, height*0.6, width, height], fill=(34, 139, 34))

# 绘制野餐毯
draw.rectangle([width//2-150, height*0.65, width//2+150, height*0.75], fill=(210, 105, 30))
# 绘制毯子上的图案
for i in range(5):
    for j in range(3):
        if (i+j) % 2 == 0:
            draw.rectangle([width//2-150+i*60, height*0.65+j*30, width//2-150+(i+1)*60, height*0.65+(j+1)*30], fill=(200, 90, 20))

# 绘制野餐篮
draw.rectangle([width//2-20, height*0.75-40, width//2+20, height*0.75], fill=(101, 67, 33))
draw.rectangle([width//2-25, height*0.75-60, width//2+25, height*0.75-40], fill=(101, 67, 33))

# 绘制食物
draw.ellipse([width//2-100, height*0.7-20, width//2-60, height*0.7], fill=(255, 0, 0))  # 苹果
draw.ellipse([width//2+60, height*0.7-15, width//2+90, height*0.7], fill=(255, 255, 0))  # 柠檬

# 绘制饮料瓶
draw.rectangle([width//2-10, height*0.7-30, width//2+10, height*0.7], fill=(200, 200, 255))

# 绘制朋友的轮廓（坐在毯子上）
# 身体
draw.rectangle([width//2-100, height*0.65-60, width//2-70, height*0.65], fill=(70, 130, 180))
# 头部
draw.ellipse([width//2-110, height*0.65-90, width//2-60, height*0.65-60], fill=(255, 220, 177))

# 绘制另一个朋友
# 身体
draw.rectangle([width//2+70, height*0.65-60, width//2+100, height*0.65], fill=(180, 130, 70))
# 头部
draw.ellipse([width//2+60, height*0.65-90, width//2+110, height*0.65-60], fill=(255, 220, 177))

# 绘制标题
try:
    # 尝试使用默认字体
    font = ImageFont.load_default()
    draw.text((width//2-80, 50), "户外野餐", fill=(50, 50, 50), font=font)
except:
    # 如果默认字体不可用，直接绘制文本
    draw.text((width//2-80, 50), "户外野餐", fill=(50, 50, 50))

# 保存图像
image.save("户外野餐.png")
print("预览图像已生成: 户外野餐.png")