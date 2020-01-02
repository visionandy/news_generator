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
TRANSITION_DURATION=10
PHOTO_DURATION=5



chrome_path='/media/xiaolong/datapool/data/chromedriver'
baidu_download='/media/xiaolong/datapool/toolbox/video_audio_tool/'

import autosubtitle_chinese_baidu as autosubtitle_chinese
import ops
from gtts import gTTS#

from random import randint
try:
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle

def generate_mp3_function(news_str,audio_result_file,lan='chinese'):
    #text_to_speech.chinese_txt_to_speech_gtts(news_str,audio_result_file)
    tts = gTTS(text=news_str, lang='zh-cn')
    tts.save(audio_result_file)


def download_google_image(key_word='beauty',output_path='/media/xiaolong/datapool/data/downloads/'):
    from google_images_download import google_images_download   #importing the library
    response = google_images_download.googleimagesdownload()   #class instantiation
    arguments = {"keywords":key_word,"output_directory":output_path,\
            'size':'>640*480',\
            "limit":1000000,"chromedriver":chrome_path,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    print(paths)   #printing absolute paths of the downloaded images


def generate_subtitle(news_str,audio_result_file,subtitle_path):
    subtitle_path=subtitle_path.split('audio')[0]

    if 1:#not os.path.exists(subtitle_path):
        wave_file=audio_result_file.replace('.mp3','.wav')
        os.system('ffmpeg -i '+audio_result_file+' -ar 16000 '+wave_file)
        autosubtitle_chinese.generate_subtitle(wave_file,news_str,subtitle_path,language='zh')

def images_statis_fun(audio_video_path):
    img_files1=glob.glob(audio_video_path+'*.jpeg')
    img_files2=glob.glob(audio_video_path+'*.jpg')
    img_files3=glob.glob(audio_video_path+'*.pngs')
    img_files=img_files1+img_files2+img_files3
    img_files = sorted(img_files,key=lambda x: int(os.path.splitext(x.split('/')[-1])[0]))
    return img_files
def photo_calculation(audio_video_path,audio_result_file,article_title):

    audio = MP3(audio_result_file)
    audio_length_second=audio.info.length
    time_per_photo=TRANSITION_DURATION+PHOTO_DURATION

    num_photos_needed=int(audio_length_second/time_per_photo)+1

    #generate mp4 video files
    img_files=images_statis_fun(audio_video_path)

    #shuffle(img_files)
    total_n_im_now=len(img_files)
    if total_n_im_now<num_photos_needed:
        #download_google_image(key_word=article_title.encode('ascii', 'ignore').decode('ascii'),output_path=audio_video_path)
        #audio_video_main.download_google_image(key_word=article_title,output_path=audio_video_path)
        os.system('python3 '+baidu_download+'baidu_image_download.py --key_word '+article_title.encode('utf-8')+' --image_save_path ' +audio_video_path)
    audio_video_main.image_filter_function(audio_video_path)
    img_files=images_statis_fun(audio_video_path)

    one_min_photos=60/time_per_photo
    num_video=num_photos_needed/one_min_photos
    return img_files,one_min_photos,num_video,num_photos_needed

def sub_video_creation_fun(img_files,num_video,result_mp4_file,one_min_photos,num_photos_needed):
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
    return sub_video_name_str

def sub_video_concatenation_fun(sub_video_name_str,result_mp4_file):
    file_names=''    
    for mp4_name in sub_video_name_str:
        if file_names=='':
            file_names=' -i '+mp4_name
        else:
            file_names+=' -i '+mp4_name
    if not os.path.exists(result_mp4_file):
        cmd_str='ffmpeg'+file_names
        os.system(cmd_str+' -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[slideshow]" -map "[slideshow]" ' +result_mp4_file)


def video_add_audio_sub_title_fun(audio_result_file,result_mp4_file,subtitle_path):
    sub_title_video=result_mp4_file.replace('.mp4','_title.mp4')
    video_audio_dir=result_mp4_file.replace('.mp4','_audio.mp4')


    if not os.path.exists(sub_title_video):
        os.system('ffmpeg -i '+result_mp4_file+' -vf ass='+subtitle_path+' '+sub_title_video)

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
    os.environ["TRANSITION_DURATION"] = TRANSITION_DURATION
    os.environ["PHOTO_DURATION"] = PHOTO_DURATION

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

def add_watermark_to_video(input_mp4,watermark_file='/media/xiaolong/datapool/landmark_fun_video.png'):
    output_mp4=input_mp4.replace('.mp4','_yy.mp4')
    if not os.path.exists(output_mp4):
        #watermark_file='/media/xiaolong/datapool/landmark_fun_video.png'
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -filter_complex "overlay=10:10" '+output_mp4)



def generate_news_video_function(lan='chinese'):
    pickle_file_path='/media/xiaolong/datapool/data/youtube/news/mitbbs/news_database/31919397.p'
    with open(pickle_file_path, 'rb') as fp:
        data = pickle.load(fp)
    #audio_video_path=data['images_set']
    folder_base_path=data['images_set']

    news_audio_video_path=folder_base_path+'video/'
    news_img_path=folder_base_path+'images/'
    if not os.path.exists(news_audio_video_path):
        os.makedirs(news_audio_video_path)
        
    if not os.path.exists(news_img_path):
        os.makedirs(news_img_path)


    result_mp4_file=news_audio_video_path+'video.mp4'
    audio_result_file=news_audio_video_path+'audio.mp3'
    subtitle_path=folder_base_path+'subtitle/audio.ass'

    news_str=data['text_article']
    generate_mp3_function(news_str,audio_result_file)

    generate_subtitle(news_str,audio_result_file,subtitle_path)

    article_title=data['title']
    img_files,one_min_photos,num_video,num_photos_needed=photo_calculation(news_img_path,audio_result_file,article_title)
    sub_video_name_str=sub_video_creation_fun(img_files,num_video,result_mp4_file,one_min_photos,num_photos_needed)

    sub_video_concatenation_fun(sub_video_name_str,result_mp4_file)
    video_add_audio_sub_title_fun(audio_result_file,result_mp4_file,subtitle_path)
    #import IPython
    #IPython.embed()
    mp4_new_name=result_mp4_file.replace('video',data['title'].decode('utf-8'))
    #shutil.copyfile(result_mp4_file, mp4_new_name.encode('utf-8') )
    os.makedirs(mp4_new_name)
    add_watermark_to_video(result_mp4_file.replace('.mp4','_audio.mp4'))

if __name__ == '__main__':

    generate_news_video_function()