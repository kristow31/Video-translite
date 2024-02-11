import os, re, requests
import subprocess
from loguru import logger


# https://www.youtube.com/playlist?list=AAAAAA
# https://rt.pornhub.com/view_video.php?viewkey=BBBBBBBBBB


def parseURL(url):
    dom = requests.get(url).content
    result = re.search('"quality":"480"},{"defaultQuality":true,"format":"hls","videoUrl":"(.*?)","quality":"720"},', dom.decode("utf-8"))
    result2 = re.search('<span class="inlineFree">(.*?)</span>', dom.decode("utf-8"))
    return [str(result.group(1).replace('\\', '')), str(result2.group(1).replace('\\', '').replace('&quot;', ''))]


def translite_video(video_url):

    if 'pornhub.com' in video_url:
        import youtube_dl
        url, title = parseURL(video_url)
        video_id = video_url.split('viewkey=')[1]
        logger.info("TITLE = {} >> ID = {}", title, video_id)

        ydl_opts_start = {
            'format': 'best',
            'playliststart:': 1,
            'playlistend': 4,
            'outtmpl': f"{path}/{title}.mp4",
            'nooverwrites': True,
            'no_warnings': False,
            'ignoreerrors': True,
        }
        if not os.path.exists(f"{path}/{title}.mp4"):
            with youtube_dl.YoutubeDL(ydl_opts_start) as ydl:
                ydl.download([url])

    else:
        from pytube import YouTube
        video = YouTube(video_url)
        title = video.title
        video_id = video.video_id
        logger.info("TITLE = {} >> ID = {}", title, video_id)
        if not os.path.exists(f"{path}/{title}.mp4"):
            try:
                logger.debug('SAVE')
                video.streams.filter(res="720p", file_extension='mp4').first().download(filename=f"{path}/{title}.mp4")
            except:
                pass
        else:
            logger.debug('copy')

    if os.path.exists(f"{path}/{title}.mp4"):
        mp3 = None
        for f in os.listdir(f"{path}/"):
            if f.startswith(video_id):  # .endswith('.mp3'):
                logger.debug("MP3 >> {}", f)
                mp3 = f
                break

        if not mp3 and not os.path.exists(f"{path}/RUS_{title}.mp4"):
            logger.info("CREATE MP3 >> {}", video_id)
            status_output = subprocess.getstatusoutput(
                fr'vot-cli --proxy "{proxy}" --output="{path}/" ' + video_url)
            logger.success("STATUS 1 >> {}", status_output)
            for f in os.listdir(f"{path}/"):
                if f.startswith(video_id):  # .endswith('.mp3'):
                    logger.debug("MP3 >> {}", f)
                    mp3 = f
                    break

        if not os.path.exists(f"{path}/RUS_{title}.mp4"):
            logger.info("CREATE VIDEO RUS >> {}", title)
            status_output = subprocess.getstatusoutput(
                fr'.\ffmpeg.exe -i "{path}/{title}.mp4" -i "{path}/{mp3}" -map 0 -map 1:a -c:v copy -shortest "{path}/RUS_{title}.mp4"')
            logger.success("STATUS 2 >> {}", status_output[0])
            os.remove(f"{path}/{mp3}")

    return True


if __name__ == '__main__':

    path = os.path.dirname(os.path.realpath(__file__)) + '/video'
    logger.info("path = {}", path)
    if not os.path.exists(path):
        os.makedirs(path)
    proxy = "https://login:pass:ip:port"

    url = input("Можно playList YouTube\nМожно видео pornhub\nВведите URL к видео (или ссылку playlist) : ")
    logger.info(url)

    if 'playlist' in url:
        from pytube import Playlist
        playlist = Playlist(url)
        logger.info('Number of videos in playlist: {}',  len(playlist.video_urls))
        for video_url in playlist.video_urls:
            translite_video(video_url)
    else:
        translite_video(url)
