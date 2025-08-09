import os
import sys
import whisper

SUPPORTED_FORMATS = (".m4a", ".mp3", ".mp4", ".aac", ".wav", ".flac", ".ogg", ".wma", ".webm")

def list_audio_files(input_dir):
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(SUPPORTED_FORMATS)]
    return files

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "audio_Input")
    output_dir = os.path.join(base_dir, "audio_Output")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print("=== 音频转文字工具（Whisper）===")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}\n")

    files = list_audio_files(input_dir)
    if not files:
        print("输入目录中没有找到音频文件，请放入音频后重试。")
        sys.exit(1)

    print("可用音频文件：")
    for idx, filename in enumerate(files, 1):
        print(f"{idx}. {filename}")

    try:
        choice = int(input("\n请输入要处理的文件序号："))
        if choice < 1 or choice > len(files):
            raise ValueError
    except ValueError:
        print("输入无效，请输入正确的数字序号。")
        sys.exit(1)

    selected_file = files[choice - 1]
    audio_path = os.path.join(input_dir, selected_file)

    gen_srt = input("是否生成字幕文件(.srt)? [y/N]: ").strip().lower() == "y"

    print("\n[1/3] 加载 Whisper 模型")
    model = whisper.load_model("small")
    # Whisper 可选模型参数（load_model时使用），模型越大越准，但速度越慢、占用显存/内存越高
        # "tiny"       : 最快，精度最低，适合实时或低配机器（~75MB）
        # "base"       : 速度较快，精度一般（~142MB）
        # "small"      : 平衡速度与精度（~466MB）
        # "medium"     : 较高精度，速度较慢（~1.5GB）
        # "large"      : 最高精度，支持多语言（~2.9GB，需高性能GPU或耐心等待CPU）
        # "large-v2"   : large的优化版本，精度更好（推荐离线使用）

    print("[2/3] 转换音频中，请稍候...")
    result = model.transcribe(audio_path, language='zh')
    # Whisper 主流语言代码及名称（可用于指定 language 参数）
        # 'zh'   : 中文
        # 'en'   : 英语
        # 'ja'   : 日语
        # 'ko'   : 韩语
        # 'fr'   : 法语
        # 'de'   : 德语
        # 'es'   : 西班牙语
        # 'ru'   : 俄语
        # 'ar'   : 阿拉伯语
        # 'pt'   : 葡萄牙语

    detected_lang = result.get("language", "unknown").capitalize()
    base_name, _ = os.path.splitext(selected_file)
    text_filename = f"{base_name}_{detected_lang}.txt"
    text_path = os.path.join(output_dir, text_filename)

    # ==== 新增：按停顿换行输出 ====
    pause_threshold = 2  # 秒
    lines = []
    for i, seg in enumerate(result["segments"]):
        line = seg["text"].strip()
        lines.append(line)

        # 判断是否与下一个片段间隔超过阈值
        if i < len(result["segments"]) - 1:
            gap = result["segments"][i + 1]["start"] - seg["end"]
            if gap >= pause_threshold:
                lines.append("\n")  # 停顿较长则换行
            else:
                lines.append(" ")  # 否则空格分隔

    # 合并为字符串
    formatted_text = "".join(lines).strip()

    print("[3/3] 保存文字结果...")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    # 生成字幕文件（可选）
    if gen_srt:
        srt_filename = f"{base_name}_{detected_lang}.srt"
        srt_path = os.path.join(output_dir, srt_filename)
        with open(srt_path, "w", encoding="utf-8") as f:
            for seg in result["segments"]:
                start = seg["start"]
                end = seg["end"]
                text = seg["text"].strip()

                def format_time(t):
                    hours = int(t // 3600)
                    minutes = int((t % 3600) // 60)
                    seconds = int(t % 60)
                    milliseconds = int((t * 1000) % 1000)
                    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

                f.write(f"{seg['id'] + 1}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(f"{text}\n\n")

    print(f"\n转换完成！文字文件: {text_path}")
    if gen_srt:
        print(f"字幕文件: {srt_path}")

if __name__ == "__main__":
    main()
