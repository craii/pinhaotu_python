# pinhaotu_python
抖音拼好图的拆图、拼图的python实现， Pythonista_IOS 文件夹内的py文件可通过 IOS app: pythonista 实现与相册交互，直接在苹果ios相册内完成**拆图、拼图** 操作

# Pythonista_IOS
其中的 py 文件因使用了pythonista 提供的 appex 库，只能在 pythonista 中运行。使用时，建议请在 pythonista中为对应文件配置相应的 share extension menu

## 分割图片
![IMG_1554](https://github.com/user-attachments/assets/37a4a8cf-27d9-48fa-8217-967632410426)
在相册中选择1张需要分割的图片，点击分享按钮后选择 Run Pythonista Script , 然后选择你配置好的分割图片脚本菜单，等待运行即可看到分割结果。然后长按图片将分割图片保存到相册即可
注意：
1. **分割的图片数量**：默认是 10 ，如果你想分割更多，需要实现在 `Pythonista_IOS/splite_image_appex.py` 中 275 行 中修改分割数量 `num_pieces`;
2. **背景色和反转色** ：背景色 `bg_color` 默认是**黑色**，可修改为 `white/transparent`; 反转色 **invert_colors** 默认是 `True` 可修改为 `False`;

## 合并/拼接图片
![IMG_1555](https://github.com/user-attachments/assets/a06589d8-fe30-48c1-9d69-a0097637724f)
在相册中选择多张需要合并的图片，点击分享按钮后选择 Run Pythonista Script 根据背景颜色选择，你配置好的白底配色合并脚本或黑底配色脚本。运行后即可看到拼好后的图片

# pure_python
可在电脑端或其它环境中运行
