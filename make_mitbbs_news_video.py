# -*- coding: utf-8 -*-
import os
import sys
import glob
from random import shuffle
from mutagen.mp3 import MP3
import re
import shutil
sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/')
sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/audiolearning/src/')
sys.path.append('/media/xiaolong/datapool/toolbox/google-images-download/')
sys.path.append('/media/xiaolong/datapool/media_data/slideshow/code_make/')
import audio_video_main
TRANSITION_DURATION=15
PHOTO_DURATION=15
from  datetime import date



chrome_path='/media/xiaolong/datapool/data/chromedriver'
baidu_download='/media/xiaolong/datapool/toolbox/video_audio_tool/'

import autosubtitle_chinese
import autosubtitle_chinese_baidu
import time
import ops
from gtts import gTTS#

from random import randint
try:
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle

def generate_mp3_function(news_str,audio_result_file,lan='chinese'):
    #text_to_speech.chinese_txt_to_speech_gtts(news_str,audio_result_file)
    if not os.path.exists(audio_result_file):
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
#    os.system('ffmpeg -i '+wavepath+' -ar 16000 '+wavepath)


def generate_subtitle(news_str,audio_result_file,subtitle_file_path):
    subtitle_path=subtitle_file_path.split('audio')[0]
    #import IPython
    #IPython.embed()

    if not os.path.exists(subtitle_file_path):
        wave_file=audio_result_file.replace('.mp3','.wav')
        if not os.path.exists(wave_file):
            os.system('ffmpeg -i '+audio_result_file+' -ar 16000 '+wave_file)
        autosubtitle_chinese_baidu.generate_subtitle(wave_file,news_str,subtitle_path,language='zh') #wavepath,news_str,subtitle_path,language='zh'

def images_statis_fun(audio_video_path):
    img_files1=glob.glob(audio_video_path+'*.jpeg')
    img_files2=glob.glob(audio_video_path+'*.jpg')
    img_files3=glob.glob(audio_video_path+'*.pngs')
    img_files=img_files1+img_files2+img_files3
    img_files = sorted(img_files,key=lambda x: int(os.path.splitext(x.split('/')[-1])[0]))
    return img_files
def photo_calculation(news_img_path,audio_result_file,article_title):

    audio = MP3(audio_result_file)
    audio_length_second=audio.info.length
    time_per_photo=TRANSITION_DURATION+PHOTO_DURATION

    num_photos_needed=int(audio_length_second/time_per_photo)+1

    #generate mp4 video files
    audio_video_main.image_filter_function(news_img_path)
    img_files=images_statis_fun(news_img_path)
    article_title_search=article_title.replace(' ','\ ')
    #shuffle(img_files)
    total_n_im_now=len(img_files)
    if total_n_im_now<num_photos_needed:
        #import IPython
        #IPython.embed()
        #download_google_image(key_word=article_title.encode('ascii', 'ignore').decode('ascii'),output_path=audio_video_path)
        #audio_video_main.download_google_image(key_word=article_title,output_path=audio_video_path)
        try:
            os.system('python3 '+baidu_download+'baidu_image_download.py --key_word '+article_title_search.replace('，','_').encode('utf-8')+' --image_save_path ' +news_img_path)
        except:
            import IPython
            IPython.embed()
        audio_video_main.image_filter_function(news_img_path)
        img_files=images_statis_fun(news_img_path)

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
    if len(sub_video_name_str)==1:
        shutil.copyfile(sub_video_name_str[0], result_mp4_file)
        return 
    txt_file=result_mp4_file.replace('.mp4','.txt')
    try:
        with open(txt_file,"w+") as f:
            for name0 in sub_video_name_str:
                f.write('file '+name0+'\n')
    except:
        import IPython
        IPython.embed()
    cmd_str='ffmpeg -f concat -safe 0 -i  '+txt_file+' -c copy '+result_mp4_file
    os.system(cmd_str)
    # for mp4_name in sub_video_name_str:
    #     if file_names=='':
    #         file_names=' -i '+mp4_name
    #     else:
    #         file_names+=' -i '+mp4_name
    # if not os.path.exists(result_mp4_file):
    #     cmd_str='ffmpeg'+file_names
        
    #     os.system(cmd_str+' -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[slideshow]" -map "[slideshow]" ' +result_mp4_file)


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
    os.environ["TRANSITION_DURATION"] = str(TRANSITION_DURATION)
    os.environ["PHOTO_DURATION"] =str(PHOTO_DURATION)

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

def add_watermark_to_video(input_mp4,final_release_video,watermark_file='/media/xiaolong/datapool/landmark_fv_new.png'):
    #output_mp4=input_mp4.replace('.mp4','_yy.mp4')
    if not os.path.exists(final_release_video):
        #watermark_file='/media/xiaolong/datapool/landmark_fun_video.png'
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -filter_complex "overlay=10:10" '+final_release_video)



def generate_news_video_function(pickle_file_path,lan='chinese'):
    #pickle_file_path='/media/xiaolong/datapool/data/youtube/news/mitbbs/news_database/31918997.p'
    with open(pickle_file_path, 'rb') as fp:
        data = pickle.load(fp)
    #audio_video_path=data['images_set']
    folder_base_path=data['images_set']

    news_audio_video_path=folder_base_path.split('image')[0]+'video/'
    news_img_path=folder_base_path#+'images/'
    if not os.path.exists(news_audio_video_path):
        os.makedirs(news_audio_video_path)
    release_video_path=folder_base_path.split('image')[0]+'release_video/'
    

    mp3_file_path=folder_base_path.split('image')[0]+'mp3/'
    subtitle_root_path=folder_base_path.split('image')[0]+'subtitle/'

    if not os.path.exists(subtitle_root_path):
        os.makedirs(subtitle_root_path)

    if not os.path.exists(mp3_file_path):
        os.makedirs(mp3_file_path)

    if not os.path.exists(release_video_path):
        os.makedirs(release_video_path)

    if not os.path.exists(news_img_path):
        os.makedirs(news_img_path)


    article_title=data['title'].replace('&','')

    if 0:#article_title=='韩国女明星张紫妍为何自杀，10年后找到了真相，网友：好可怕！':
        import IPython
        IPython.embed()



    result_mp4_file=news_audio_video_path+article_title.replace(' ','_')+'.mp4'
    audio_result_file=mp3_file_path+article_title.replace(' ','_')+'.mp3'
    v_a_txt_file=result_mp4_file.replace('.mp4','_audio_txt.mp4')
    final_release_video=release_video_path+article_title.replace(' ','_')+'.mp4'


    #result_mp4_file=news_audio_video_path+'video.mp4'
    #audio_result_file=news_audio_video_path+'audio.mp3'
    subtitle_file_path=subtitle_root_path+article_title.replace(' ','_')+'.ass' #'subtitle/audio.ass'

    news_str=data['text_article']

    print('hold on')
    #import IPython
    #IPython.embed()

    generate_mp3_function(news_str,audio_result_file)
    
    try:
        generate_subtitle(news_str,audio_result_file,subtitle_file_path)
    except:
        #import IPython
        #IPython.embed()
        time.sleep(30)
        generate_subtitle(news_str,audio_result_file,subtitle_file_path)
        #import IPython
        #IPython.embed()
    #return 
    img_files,one_min_photos,num_video,num_photos_needed=photo_calculation(news_img_path,audio_result_file,article_title)
    sub_video_name_str=sub_video_creation_fun(img_files,num_video,result_mp4_file,one_min_photos,num_photos_needed)

    if not os.path.exists(result_mp4_file):    
        sub_video_concatenation_fun(sub_video_name_str,result_mp4_file)

    if not os.path.exists(result_mp4_file.replace('.mp4','_audio.mp4')):    
        video_add_audio_sub_title_fun(audio_result_file,result_mp4_file,subtitle_path=subtitle_file_path)
    #import IPython
    #IPython.embed()
    mp4_new_name=result_mp4_file.replace('video',data['title'].decode('utf-8'))
    #shutil.copyfile(result_mp4_file, mp4_new_name.encode('utf-8') )
    #if not os.path.exists(mp4_new_name):    
    #    os.makedirs(mp4_new_name)
    add_watermark_to_video(result_mp4_file.replace('.mp4','_audio.mp4'),final_release_video)

def generate_news_video_set():
    databe_path='/media/xiaolong/datapool/data/youtube/news/mitbbs_news/'+str(date.today())+'/json/'
    databe_path='/media/xiaolong/datapool/data/youtube/news/mitbbs_news/2019-04-24/json/'
    #'/media/xiaolong/datapool/data/youtube/news/mitbbs/news_database/'
    pickle_files=glob.glob(databe_path+'*.p')
    for pickle_file_path in pickle_files:
        generate_news_video_function(pickle_file_path,lan='chinese')

if __name__ == '__main__':

    generate_news_video_set()
    #ffmpeg -i audio.mp3 -ss 00:00:14 -to 00:02:49 -c copy audio1.mp3
    #ffmpeg -i output3.mkv -t 00:04:20 -c:v libx264 -c:a libfaac output-cut.mkv