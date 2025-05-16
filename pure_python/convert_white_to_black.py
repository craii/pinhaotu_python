from PIL import Image
import os

def convert_white_to_black(input_dir):
    # 获取输入目录中的所有图片文件
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("未找到图片文件")
        return
    
    # 遍历所有图片
    for image_file in image_files:
        # 构建输入输出路径
        img_path = os.path.join(input_dir, image_file)
        filename, ext = os.path.splitext(image_file)
        
        # 对于JPEG格式的输出，我们使用PNG格式来保存以支持透明度
        output_ext = '.png'
        output_path = os.path.join(input_dir, f"{filename}_b{output_ext}")
        
        # 打开图片
        img = Image.open(img_path)
        
        # 确保图片是RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 获取像素数据
        img_data = img.load()
        width, height = img.size
        
        # 遍历每个像素
        for x in range(width):
            for y in range(height):
                pixel = img_data[x, y]
                # 如果像素是白色（RGB都是255），则将其转换为黑色
                if pixel[:3] == (0, 0, 0):
                    # 保持原始的alpha通道值
                    img_data[x, y] = (0, 0, 0, pixel[3])
        
        # 保存处理后的图片（统一使用PNG格式）
        img.save(output_path, 'PNG')
        print(f"已处理图片: {image_file} -> {os.path.basename(output_path)}")

# 执行转换操作
input_directory = r"c:\Users\Elias\Desktop\pic_integrity\imgs"
input_directory = r"c:\Users\Elias\Desktop\pic_integrity\imgs_b"
convert_white_to_black(input_directory)