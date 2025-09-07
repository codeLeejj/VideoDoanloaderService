import os
import sys
import subprocess
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"AddressHandler: init")

retry_times = 5


# 检查并安装 yt-dlp
def install_yt_dlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        try:
            import pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            import yt_dlp
            return True
        except:
            return False


def get_note_of_video(_note: str):
    if _note.startswith("144p"):
        return 144
    elif _note.startswith("240p"):
        return 240
    elif _note.startswith("360p"):
        return 360
    elif _note.startswith("480p"):
        return 480
    elif _note.startswith("640p"):
        return 640
    elif _note.startswith("720p"):
        return 720
    elif _note.startswith("1080p"):
        return 1080
    elif _note.startswith("1440p"):
        return 1440
    elif _note.startswith("2160p"):
        return 2160
    else:
        return None


# 找到最高清晰度，如果超过了_max 就保留
def get_the_max_video(_list, _max):
    _max_note = 240
    for _item in _list:
        note: str = _item.get('format_note', 'N/A')
        _s_note = get_note_of_video(note)
        if _s_note:
            if _s_note >= _max:
                return _max
            if _s_note > _max_note:
                _max_note = _s_note
                continue

    return _max_note


# 找到最高清的音频
def get_the_max_audio(_list):
    # low medium
    for _item in _list:
        resolution = _item.get('resolution', 'N/A')
        # 找出音频
        if resolution != "audio only":
            continue
        note: str = _item.get('format_note', 'N/A')
        if note.count("medium"):
            return "medium"
    return "low"


# 排查不需要的格式
def is_i_want(_item: dict[str:str]):
    if ["images", "vp9"].count(_item.get('vcodec', 'none').split('.')[0]):
        return False
    elif _item.get('ext', 'N/A') == "mhtml":
        return False
    return True

    # 转换为我需要的数据结构


def covert(_item):
    if not _item:
        return None
    format_id = _item.get('format_id', 'N/A')
    resolution = _item.get('resolution', 'N/A')
    ext = _item.get('ext', 'N/A')
    file_size = _item.get('filesize', 0)
    v_codec = _item.get('vcodec', 'none').split('.')[0]  # 简化视频编码显示
    a_codec = _item.get('acodec', 'none').split('.')[0]  # 简化音频编码显示
    note: str = _item.get('format_note', 'N/A')
    # 格式化文件大小
    if file_size:
        size_str = f"{file_size / (1024 * 1024):.1f}MB"
    else:
        size_str = "未知大小"

    _item = {"id": format_id, "resolution": resolution, "ext": ext, "vcodec": v_codec, "acodec": a_codec,
             "note": note, "size_str": size_str}
    return _item

    # 下载进度钩子函数


# 下载视频函数
def download_video(_url, param, output_path):
    logger.info(f"下载:{_url}")

    def download_progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            progress_text = f"下载进度: {percent} | 速度: {speed} | 剩余时间: {eta}"
            logger.info(progress_text)
        elif d['status'] == 'finished':
            logger.info(f"下载完成！正在处理文件...")

    # 配置 yt-dlp 选项
    ydl_opts: dict[str:str] = {'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                               'progress_hooks': [download_progress_hook],
                               # 禁用控制台输出
                               'quiet': True, 'no_warnings': True,
                               }
    if param == "best":
        # "最佳质量":
        ydl_opts['format'] = 'best'
    else:
        ydl_opts['format'] = param

    # "仅音频 (MP3)":
    # ydl_opts['format'] = 'bestaudio/best'
    # ydl_opts['postprocessors'] = [{
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'mp3',
    #     'preferredquality': '192',
    # }]
    # "仅视频 (MP4)":
    # ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    return download_single(ydl_opts, _url)


def download_single(_opts, _url, times=0):
    # 在单独的线程中下载
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(_opts) as ydl:
            logger.info(f"开始下载: {_url}\n")
            result = ydl.download([_url])
            logger.info(f"下载完成: {_url}\n")
            return {"code": 0, "message": f"下载成功", "data": result}
    except Exception as e:
        logger.info("下载出错！")
        if str(e).count("timed out"):
            if times > retry_times:
                return {"code": -1, "message": f"错误: {str(e)}\n"}
            return download_single(_opts, _url, times + 1)
        else:
            return {"code": -1, "message": f"错误: {str(e)}\n"}


class AddressHandler:

    def load_video_format(self, _source, _url):
        logger.info(f"查看({_source}):{_url}")
        """列出视频所有可用格式"""
        ydl_opts = {
            'quiet': True,  # 不显示多余信息
            'no_warnings': True,  # 不显示警告
        }

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"prepare request youtube url：{_url}")
                # 获取视频信息
                info = ydl.extract_info(_url, download=False)
                # logger.info(f"got youtube formats：{info}")
                result: dict[str:str] = {"title": info.get('title', '未知title'), "id": info.get('id', '未知id')}
                formats_temp = []

                # 1.排除不要的
                for fmt in info.get('formats', []):
                    if not is_i_want(fmt):
                        continue
                    formats_temp.append(fmt)

                # 我想要的数据源
                formats = []
                # 2.过滤出高清的视频源
                max_video_note = get_the_max_video(formats_temp, 1080)
                print(f"最大视频清晰度:{max_video_note}")

                for _item in formats_temp:
                    note: str = _item.get('format_note', 'N/A')
                    _s_note = get_note_of_video(note)
                    if _s_note:
                        if _s_note >= max_video_note:
                            formats.append(covert(_item))

                # 3.过滤最高清的音频
                max_audio_note = get_the_max_audio(formats_temp)
                print(f"最大音频清晰度:{max_audio_note}")
                # low medium
                for _item in formats_temp:
                    resolution = _item.get('resolution', 'N/A')
                    # 找出音频
                    if resolution != "audio only":
                        continue
                    note: str = _item.get('format_note', 'N/A')
                    if note.count(max_audio_note):
                        formats.append(covert(_item))

                result["formats"] = formats

                print(result)
                print("格式选择建议:")
                print("1. 下载最佳视频+音频: bestvideo+bestaudio")
                print("2. 下载720p及以上: bestvideo[height>=720]+bestaudio/best[height>=720]")
                print("3. 下载1080p MP4: bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]")
                return result
        except Exception as e:
            logger.info(f"解析数据出错：{e}")
            return {"code": -1, "message": f"解析数据出错：{e}"}

    # 查询视频源
    def query(self, _url):
        logger.info(f"AddressHandler: received url: {_url}")
        if _url:
            yt_dlp_list = ["youtube", "youtubepot-webpo", "youtubetab", "generic",
                           "vikichannel", "youtubewebarchive", "gamejolt", "hotstar",
                           "instagram", "niconicochannelplus", "tiktok", "rokfinchannel",
                           "twitter", "stacommu", "wrestleuniverse", "twitch",
                           "nhkradirulive", "line", "nflplusreplay", "jiocinema",
                           "jiosaavn", "afreecatvlive", "soundcloud", "orfon",
                           "bilibili", "sonylivseries", "tver", "vimeo"]
            for item in yt_dlp_list:
                if _url.count(item):
                    return self.load_video_format(item, _url)
        logger.info(f"AddressHandler: error url:{_url}")
        return {"code": -1, "message": f"请输入YouTube视频URL:{_url}"}
