# -*- coding: utf-8 -*-
import os
import sys
import glob
from random import shuffle
sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/')
import ops
from random import randint
import datetime
import sys  
reload(sys)  
import glob
sys.setdefaultencoding('utf8')
mm_file_path='/media/xiaolong/datapool/mm131'

#all_image_files = [f for f in glob.glob(mm_file_path + "**/*.jpg")]
all_image_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(mm_file_path) for f in filenames if os.path.splitext(f)[1] == '.jpg']

def generate_video_shell(img_path,result_video_path):


    img_files=all_image_files#glob.glob(img_path+'*')
    shuffle(img_files)
    photos=''
    for img_path0 in img_files[0:30]:
        if photos=='':
            photos=img_path0
        else:
            photos+=' '+img_path0

    os.environ["PHOTOS"] = photos
    os.environ["FFMPEG_result_path"] = result_video_path

    cmd_str='bash ffmpeg_test.sh'
    os.system(cmd_str)

def generate_video_main(audio_file_path,video_file_path):
    video_audio_dir=video_file_path.replace('.mp4','_v.mp4')
    ops.combine_audio_video_cmd(audio_file_path, video_file_path, video_audio_dir)


def make_video_main(video_n=1):

    img_path='/media/xiaolong/datapool/data/downloads/nvshens/'
    result_video_path='/media/xiaolong/datapool/data/downloads/test/'
    audio_files_path='/media/xiaolong/datapool/data/youtube_video/audio/'
    release_video_path='/media/xiaolong/datapool/data/youtube_video/mm_video/'
    #audio_n=randint(0, 49)
    audio_files=glob.glob(audio_files_path+'*.mp3')
    audio_n=randint(0, len(audio_files))

    audio_file_path=audio_files_path+'beauty_leg_3_min.mp3'#audio_files[audio_n]#'/media/xiaolong/datapool/data/youtube_video/audio/'gudian_'+str(audio_n)+'.mp3''

    video_file_path=result_video_path+'result_stocking.mp4'.replace('.mp4',str(video_n)+'.mp4')
    mp4_name_str=['stocking_a.mp4','stocking_b.mp4']#,'stocking_c.mp4']
    for i in range(len(mp4_name_str)):
        mp4_name_str[i]=mp4_name_str[i].replace('.mp4',str(video_n)+'.mp4')


    for mp4_name in mp4_name_str:
        if not os.path.exists(result_video_path+mp4_name):
            generate_video_shell(img_path,result_video_path+mp4_name)
    file_names=''    
    for mp4_name in mp4_name_str:
        if file_names=='':
            file_names=' -i '+result_video_path+mp4_name
        else:
            file_names+=' -i '+result_video_path+mp4_name
    if not os.path.exists(video_file_path):
        cmd_str='ffmpeg'+file_names
        os.system(cmd_str+' -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[slideshow]" -map "[slideshow]" ' +video_file_path)

    video_audio_dir=video_file_path.replace('.mp4','_audio.mp4')
    if not os.path.exists(video_audio_dir):
        ops.combine_audio_video_cmd(audio_file_path, video_file_path, video_audio_dir)
    add_watermark_to_video(video_audio_dir,video_audio_dir.replace(result_video_path,release_video_path))

def add_watermark_to_video(input_mp4,final_release_video,watermark_file='/media/xiaolong/datapool/landmark_fv_new.png'):
    #output_mp4=input_mp4.replace('.mp4','_yy.mp4')
    if not os.path.exists(final_release_video):
        #watermark_file='/media/xiaolong/datapool/landmark_fun_video.png'
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -filter_complex "overlay=10:10" '+final_release_video)

def video_loop():
    for i in range(1,20,1):
        make_video_main(video_n=i)

def test_automatic_video():
    title_str='高清丝袜高跟美女'.decode('utf-8','ignore')
    playlist_name='高清丝袜高跟美女'.decode('utf-8','ignore')#.encode("ascii","ignore")
    video_path='/media/xiaolong/datapool/data/downloads/test/result_stocking16_audio.mp4'.decode('utf-8','ignore')
    description_str='丝袜高跟美女，希望大家喜欢，每周更新，欢迎订阅,谢谢支持'.decode('utf-8','ignore')#.encode("ascii","ignore")
    tag_str='"丝袜 高跟 美女 人体艺术 健身美女 性爱 黑丝 朦胧  \
         模特  翘臀 大奶 没胸 beautiful girls lyrics girl beautyleg world cover \
         karaoke lingerie model"'.decode('utf-8','ignore') 
    cmd=upload_video_youtube(title_str,playlist_name,video_path,description_str,tag_str)
    os.system(cmd)


def upload_video_youtube(title_str,playlist_name,video_path,description_str,tag_str):
    cmd='youtube-upload --title='+title_str+' \
  --playlist='+playlist_name+' \
  --tags='+tag_str+' \
  --description='+description_str+' \
  --embeddable=True'+' '+video_path
    return cmd

def upload_video_youtube_v1(title_str,playlist_name,video_path,description_str,tag_str):
    cmd='youtube-upload --title='+title_str+' \
  --description='+description_str+' \
  --tags='+tag_str+' \
  --recording-date='+str(datetime.datetime.now()).split(' ')[0]+' \
  --default-language="en" \
  --default-audio-language="en" \
  --playlist='+playlist_name+' \
  --embeddable=True'+' '+video_path
    return cmd


if __name__ == '__main__':

    #test_automatic_video()
    video_loop()