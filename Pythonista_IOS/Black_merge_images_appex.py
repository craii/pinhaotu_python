import os

from typing import List, Optional
from PIL import Image


def open_images(input_dir: str) -> List[Optional[Image.Image]]:
    # 获取输入目录中的所有图片文件
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if len(image_files) == 0: 
        return list()
    return [Image.open(os.path.join(input_dir, image_file)) for image_file in image_files]


def merge_images(*images: Image.Image, colour: tuple=(255, 255, 255)) -> None:

    # 读取第一张图片来获取尺寸
    W, H = images[0].size
    
    # 创建新图片,初始化为完全透明
    new_pic = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    
    # 遍历每张图片

    for current_img in images:
        print(f"打开第 {images.index(current_img)} 图片")        
        # 确保图片是RGBA模式
        if current_img.mode != 'RGBA':
            current_img = current_img.convert('RGBA')
        
        # 获取像素数据
        img_data = current_img.load()
        new_data = new_pic.load()
        
        # 遍历每个像素
        for x in range(W):
            for y in range(H):
                pixel = img_data[x, y]
                # 如果像素不是透明的且不是指定颜色,则写入新图片
                if pixel[3] != 0 and pixel[:3] != colour:
                    new_data[x, y] = pixel
    
    # 保存结果
    new_pic.show()
    print(f"合并完成")
    return new_pic
    
    
def img_revert(img: Image.Image) -> Image.Image:
    """
    将输入图片的颜色进行反转
    Args:
        img: PIL Image对象
    Returns:
        反转颜色后的图片
    """
    # 确保图片是RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 获取图片尺寸和像素数据
    width, height = img.size
    img_data = img.load()
    
    # 创建新图片用于存储反转结果
    reverted_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    reverted_data = reverted_img.load()
    
    # 遍历每个像素进行颜色反转
    for x in range(width):
        for y in range(height):
            r, g, b, a = img_data[x, y]
            # 保持透明度不变,反转RGB值
            reverted_data[x, y] = (255 - r, 255 - g, 255 - b, a)
    
    reverted_img.show()
    return reverted_img


if __name__ in "__main__":
    import appex
    # input_directory = r"c:\Users\Elias\Desktop\pic_integrity\imgs"
    # imgs = open_images(input_directory)
    imgs = appex.get_images()
    #merged_img = merge_images(*imgs, colour=(255,255,255))  # 使用默认的白色作为过滤颜色
    merged_img = merge_images(*imgs, colour=(0,0,0))  # 使用默认的白色作为过滤颜色
    img_revert(merged_img)
