# -*- coding: utf-8 -*-
import os
import sys
import glob
from random import shuffle
from mutagen.mp3 import MP3
import re

sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/')
sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/audiolearning/src/')
sys.path.append('/media/xiaolong/datapool/toolbox/google-images-download/')
sys.path.append('/media/xiaolong/datapool/media_data/slideshow/code_make/')
import audio_video_main


chrome_path='/media/xiaolong/datapool/data/chromedriver'
baidu_download='/media/xiaolong/datapool/toolbox/video_audio_tool/'

import autosubtitle_chinese
import ops
from gtts import gTTS#

from random import randint
try:
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle


def download_google_image(key_word='beauty',output_path='/media/xiaolong/datapool/data/downloads/'):
    from google_images_download import google_images_download   #importing the library
    response = google_images_download.googleimagesdownload()   #class instantiation
    arguments = {"keywords":key_word,"output_directory":output_path,\
            'size':'>640*480',\
            "limit":1000000,"chromedriver":chrome_path,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    print(paths)   #printing absolute paths of the downloaded images





def generate_news_video_function(lan='chinese'):
    pickle_file_path='/media/xiaolong/datapool/data/youtube/news/mitbbs/31919397.p'
    with open(pickle_file_path, 'rb') as fp:
        data = pickle.load(fp)
    audio_video_path=data['images_set']
    result_mp4_file=audio_video_path+'video.mp4'
    audio_result_file=audio_video_path+'audio.mp3'
    subtitle_path=audio_video_path+'/subtitle/audio.ass'
    #generate mp3 files
    news_str=data['text_article']
    generate_mp3_function(news_str,audio_result_file)

    #import IPython
    #IPython.embed()

    if not os.path.exists(subtitle_path):
        wave_file=audio_result_file.replace('.mp3','.wav')
        os.system('ffmpeg -i '+audio_result_file+' '+wave_file)
        autosubtitle_chinese.generate_subtitle(wave_file,news_str,language='zh')
    return 



    #generate_news_video_shell(audio_video_path,result_mp4_file,style='animation')
    article_title=data['title']

    audio = MP3(audio_result_file)
    audio_length_second=audio.info.length
    num_photos_needed=int(audio_length_second/10)+1


    #generate mp4 video files
    img_files1=glob.glob(audio_video_path+'*.jpeg')
    img_files2=glob.glob(audio_video_path+'*.jpg')
    img_files3=glob.glob(audio_video_path+'*.png')
    img_files=img_files1+img_files2+img_files3

    img_files = sorted(img_files,key=lambda x: int(os.path.splitext(x.split('/')[-1])[0]))

    #shuffle(img_files)
    time_per_photo=10
    total_n_im_now=len(img_files)
    if total_n_im_now<num_photos_needed:
        #download_google_image(key_word=article_title.encode('ascii', 'ignore').decode('ascii'),output_path=audio_video_path)
        #audio_video_main.download_google_image(key_word=article_title,output_path=audio_video_path)
        os.system('python3 '+baidu_download+'baidu_image_download.py --key_word '+article_title.encode('utf-8')+' --image_save_path ' +audio_video_path)
        audio_video_main.image_filter_function(audio_video_path)

    one_min_photos=60/time_per_photo
    num_video=num_photos_needed/one_min_photos

    sub_video_name_str=[]
    for i in range(0,num_video):
        sub_result_video_path=result_mp4_file.replace('.mp4',str(i)+'.mp4')
        if not i==num_video-1:
            images_batch=img_files[i*one_min_photos:(i+1)*one_min_photos]
        else:
            images_batch=img_files[i*one_min_photos:num_photos_needed]
        if not os.path.exists(sub_result_video_path):
            generate_sub_video_shell(images_batch,sub_result_video_path)
        sub_video_name_str.append(sub_result_video_path)

    file_names=''    
    for mp4_name in sub_video_name_str:
        if file_names=='':
            file_names=' -i '+mp4_name
        else:
            file_names+=' -i '+mp4_name
    if not os.path.exists(result_mp4_file):
        cmd_str='ffmpeg'+file_names
        os.system(cmd_str+' -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[slideshow]" -map "[slideshow]" ' +result_mp4_file)


    news_subtitle=news_str.split(u'\uff0c')
    # sub_title=[]
    # for sentence_sub in news_subtitle:
    #     dot_sen=sentence_sub.split(u'\u3002')
    #     for dot_sen_sub in dot_sen:
    #         sub_title.append(dot_sen_sub)

    print(re.split('\u3002, \uff0c',news_str))

    sub_title_video=result_mp4_file.replace('.mp4','_title.mp4')
    os.system('ffmpeg -i '+result_mp4_file+' -vf ass='+subtitle_path+' '+sub_title_video)
    
    video_audio_dir=result_mp4_file.replace('.mp4','_audio.mp4')
    if not os.path.exists(video_audio_dir):
         ops.combine_audio_video_cmd(audio_result_file, sub_title_video, video_audio_dir)


def generate_sub_video_shell(img_files,result_video_path):

    photos=''
    for img_path0 in img_files:
        if photos=='':
            photos=img_path0
        else:
            photos+=' '+img_path0

    os.environ["PHOTOS"] = photos
    os.environ["FFMPEG_result_path"] = result_video_path

    cmd_str='bash ffmpeg_news.sh'
    os.system(cmd_str)




def generate_news_video_shell(img_path,result_video_path,style='transition'):

    img_files=glob.glob(img_path+'*')
    shuffle(img_files)
    photos=''
    for img_path0 in img_files:
        if not '.jpg' in img_path0:
            continue
        if photos=='':
            photos=img_path0
        else:
            photos+=' '+img_path0

    os.environ["PHOTOS"] = photos
    os.environ["FFMPEG_result_path"] = result_video_path
    if style=='transition':
        cmd_str='bash ffmpeg_news.sh'
    else:
        cmd_str='bash ffmpeg_animation_news.sh'
    os.system(cmd_str)


def generate_mp3_function(news_str,audio_result_file,lan='chinese'):
    #text_to_speech.chinese_txt_to_speech_gtts(news_str,audio_result_file)
    tts = gTTS(text=news_str, lang='zh-cn')
    tts.save(audio_result_file)



def generate_video_shell(img_path,result_video_path):

    img_files=glob.glob(img_path+'*')
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
    audio_files=glob.glob(audio_files_path+'*.mp3')
    audio_n=randint(0, len(audio_files))

    audio_file_path=audio_files[audio_n]#'/media/xiaolong/datapool/data/youtube_video/audio/'gudian_'+str(audio_n)+'.mp3''

    video_file_path=result_video_path+'result_stocking.mp4'.replace('.mp4',str(video_n)+'.mp4')
    mp4_name_str=['stocking_a.mp4','stocking_b.mp4','stocking_c.mp4']
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

def video_loop():
    for i in range(1,50,1):
        make_video_main(video_n=i)


if __name__ == '__main__':

    generate_news_video_function()