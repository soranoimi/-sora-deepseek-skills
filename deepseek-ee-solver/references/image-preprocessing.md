# 图片预处理流程 / Image Preprocessing

拍照题目（作业/题库）常见问题：侧拍、倒拍、扩展名与真实格式不符、模糊。
Photos of problems are often rotated, mislabeled, or blurry. Preprocess before reading.

## 流程 / Workflow

1. **识别真实格式**：读文件头魔数（不要信扩展名）。
   - JPEG: `FF D8 FF`；PNG: `89 50 4E 47`；WebP: `52 49 46 46 … 57 45 42 50`；GIF: `47 49 46`；BMP: `42 4D`
   - 用 PowerShell 读前 16 字节：
     ```powershell
     $fs=[System.IO.File]::OpenRead($p); $b=New-Object byte[] 16; $n=$fs.Read($b,0,16); $fs.Close();
     ($b[0..($n-1)] | ForEach-Object { $_.ToString('X2') }) -join ' '
     ```
2. **转正**：按需 rotate(−90/90/180, expand=True)；有 EXIF Orientation 时 Pillow 的
   `ImageOps.exif_transpose()` 可自动纠正。
3. **复制到工作区**（换成正确扩展名），再放大裁切关键区域阅读：
   ```python
   from PIL import Image, ImageOps, ImageEnhance
   im = Image.open(src).convert("L")
   im = ImageOps.exif_transpose(im)
   c = im.crop((x0, y0, x1, y1))                 # 关键区域
   c = c.resize((c.width*4, c.height*4), Image.LANCZOS)
   c = ImageOps.autocontrast(c, cutoff=1)       # 增强对比
   c = ImageEnhance.Sharpness(c).enhance(1.5)   # 锐化
   c.save("zoom.png")
   ```
4. **读题转写**：把读到的量按 `notation.md` 规范转写（含单位、下标、相量符号），
   在回复中先贴出“转写题面”，再求解——写错读错的量用户能立刻发现。
5. 读数存疑时（如 100 与 10 难以分辨）：优先用**比值**推导，并在结果中注明该存疑点。

## 注意 / Notes

- 侧拍的题：先 rotate 再裁切，顺序不要反。
- 分辨率不足时：对单个数字/符号区域放大 5–8 倍 + autocontrast，比整图增强有效。
- 修改后图片统一放工作区，命名 `problem-<题号>.jpg`、`zoom-<区域>.png`。
