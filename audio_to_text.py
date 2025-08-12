import os
import torch
import whisper

from tkinter import Tk

# 格式化时间戳函数
def format_timestamp(seconds: float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

# 输入输出目录（相对路径）
input_dir = os.path.join(os.getcwd(), "audio_Input")
output_dir = os.path.join(os.getcwd(), "audio_Output")
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# 扫描目录下所有支持的音频文件
supported_exts = {".m4a", ".mp3", ".wav", ".flac", ".mp4", ".aac"}
files = [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in supported_exts]

if not files:
    print(f"输入目录 {input_dir} 中没有找到支持的音频文件。")
    exit()

print("检测到以下音频文件：")
for i, f in enumerate(files, 1):
    print(f"{i}. {f}")

choice = input("请输入要转换的文件编号: ").strip()
if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
    print("输入无效，程序退出。")
    exit()

file_name = files[int(choice) - 1]
file_path = os.path.join(input_dir, file_name)

# 检测 GPU 并询问是否启用
if torch.cuda.is_available():
    use_gpu = input("检测到 NVIDIA GPU，是否使用 GPU 加速？(y/N): ").strip().lower() == "y"
    device = "cuda" if use_gpu else "cpu"
else:
    print("未检测到 NVIDIA GPU，使用 CPU。")
    device = "cpu"

# 选择模型
model_choice = input("请选择 Whisper 模型（tiny/base/small/medium/large-v2，默认 small）: ").strip().lower()
if model_choice == "":
    model_choice = "small"

print(f"加载模型 {model_choice} 到 {device} 中，请稍候...")
model = whisper.load_model(model_choice, device=device)

# 语言选择（可留空自动检测）
lang_choice = input("请输入识别语言代码（留空自动检测，如 zh、en、ja）: ").strip().lower()
if lang_choice == "":
    lang_choice = None

# 是否生成字幕
make_sub = input("是否生成字幕文件 (.srt)？(y/N): ").strip().lower() == "y"

# 转录音频
print("[2/3] 转换音频中，请稍候...")
result = model.transcribe(file_path, language=lang_choice)

# 写文本文件
base_name = os.path.splitext(file_name)[0]
txt_name = f"{base_name}_{lang_choice or 'auto'}.txt"
with open(os.path.join(output_dir, txt_name), "w", encoding="utf-8") as f:
    f.write(result["text"])

# 写字幕文件（可选）
if make_sub:
    srt_name = f"{base_name}_{lang_choice or 'auto'}.srt"
    with open(os.path.join(output_dir, srt_name), "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], 1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"{i}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{text}\n\n")

print("[3/3] 转换完成！")
print(f"文本已保存: {os.path.join(output_dir, txt_name)}")
if make_sub:
    print(f"字幕已保存: {os.path.join(output_dir, srt_name)}")
