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
TRANSITION_DURATION=5
PHOTO_DURATION=5
#batch_num=0
import yaml
from  datetime import date

chrome_path='/media/xiaolong/datapool/data/chromedriver'
baidu_download='/media/xiaolong/datapool/toolbox/video_audio_tool/'

import autosubtitle_chinese
import autosubtitle_chinese_baidu
import time
import ops
from gtts import gTTS#
import shutil
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
def photo_calculation(audio_video_path,audio_result_file,article_title):

    #audio = MP3(audio_result_file)
    #audio_length_second=60#audio.info.length
    #generate mp4 video files
    img_files=images_statis_fun(audio_video_path)
    #shuffle(img_files)
    total_n_im_now=len(img_files)
    number_limit=6
    if total_n_im_now<number_limit:
        img_files.extend(img_files[0:number_limit-total_n_im_now])
    time_per_photo=TRANSITION_DURATION+PHOTO_DURATION
    #num_photos_needed=int(audio_length_second/time_per_photo)+1
    audio_video_main.image_filter_function(audio_video_path)
    img_files=images_statis_fun(audio_video_path)
    num_photos_needed=len(img_files)

    return img_files #one_min_photos,num_video,num_photos_needed

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
         ops.combine_audio_video_cmd(audio_result_file, result_mp4_file, video_audio_dir)


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

def add_watermark_to_video(input_mp4,watermark_file='/media/xiaolong/datapool/banana_video_new.png'):
    output_mp4=input_mp4.replace('_audio_txt.mp4','-banana_channel.mp4')
    if not os.path.exists(output_mp4):
        #watermark_file='/media/xiaolong/datapool/landmark_fun_video.png'
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -filter_complex "overlay=10:10" '+output_mp4)
    else:
        #base_path=output_mp4.split(output_mp4.split('/')[-1])[0]
        #new_path=''
        dst=output_mp4.replace('-banana_channel.mp4','.mp4').replace('/video/','/release_video/')
        shutil.copyfile(output_mp4,dst)



def generate_text_fun(data,result_txt_file):

    article=data['text_article'].split('版权所有')[0].split('吕东垠')[0].split('（SIPA')[0].split('视觉中国')[0]
    text_data=article.split('。')
    batch_size=25
    batch_num=len(article)/batch_size

    if os.path.exists(result_txt_file):
        return batch_num

    with open(result_txt_file,'w+')  as f:
        for i in range(0,batch_num):
            if i<batch_num-1:
                text=article[i*batch_size:(i+1)*batch_size]
            else:
                text=article[i*batch_size:]
            f.write(text+'\n')
    return batch_num


def generate_video_text_fun(input_video,output_video,text_file,batch_num):
    font_txt_path='/media/xiaolong/datapool/toolbox/video_audio_tool/font/simsun.ttc'
    font_setting_str='drawtext=fontsize=30:fontcolor=Blue:box=1:boxcolor=white@0.6'
    number_str=str(batch_num*35)
    #drawbox_str='drawbox=y=ih/PHI:color=black@0.4:width=iw:height=48:t=fill,'
    #input_video=result_mp4_file.replace('.mp4','_audio.mp4')
    #output_video=result_mp4_file.replace('.mp4','_text.mp4')
    ffmpeg_str='ffmpeg -i '+input_video+' -vf '+'[in]'+font_setting_str+':fontfile='+font_txt_path+':textfile='+text_file+':x=50:y=h-'+number_str+' -y '+output_video
    os.system(ffmpeg_str)




def generate_news_video_function(pickle_file_path,lan='chinese'):
    #pickle_file_path='/media/xiaolong/datapool/data/youtube/news/mitbbs/news_database/31918997.p'
    with open(pickle_file_path, 'rb') as fp:
        data = pickle.load(fp)
    #audio_video_path=data['images_set']
    folder_base_path=data['images_set']
    #import IPython
    #IPython.embed()

    news_audio_video_path=folder_base_path.split('image')[0]+'video/'
    news_img_path=folder_base_path#+'images/'
    if not os.path.exists(news_audio_video_path):
        os.makedirs(news_audio_video_path)
    release_video_path=folder_base_path.split('image')[0]+'release_video/'

    if not os.path.exists(release_video_path):
        os.makedirs(release_video_path)

    if not os.path.exists(news_img_path):
        os.makedirs(news_img_path)

    article_title=data['title']

    result_mp4_file=news_audio_video_path+article_title.replace(' ','_')+'.mp4'
    v_a_file=result_mp4_file.replace('.mp4','_audio.mp4')
    v_a_txt_file=result_mp4_file.replace('.mp4','_audio_txt.mp4')

    audio_result_file='/media/xiaolong/datapool/data/youtube/news/sina_news/bana_news.mp3'

    text_on_video=data['text_article']
    #generate_mp3_function(news_str,audio_result_file)
    subtitle_file_path=result_mp4_file.replace('.mp4','.txt')

    batch_num=generate_text_fun(data,result_txt_file=subtitle_file_path)

    #img_files,one_min_photos,num_video,num_photos_needed=photo_calculation(news_img_path,audio_result_file,article_title)
    img_files=photo_calculation(news_img_path,audio_result_file,article_title)

    if not os.path.exists(result_mp4_file):
        generate_sub_video_shell(img_files,result_mp4_file)
    
    if not os.path.exists(v_a_file):
        ops.combine_audio_video_cmd(audio_result_file, result_mp4_file, v_a_file)
    
    #import IPython
    #IPython.embed()
    if not os.path.exists(v_a_txt_file):
        generate_video_text_fun(input_video=v_a_file,output_video=v_a_txt_file,text_file=subtitle_file_path, batch_num=batch_num)

    #return 

    mp4_new_name=result_mp4_file.replace('video',data['title'].decode('utf-8'))
    #shutil.copyfile(result_mp4_file, mp4_new_name.encode('utf-8') )
    #if not os.path.exists(mp4_new_name):    
    #    os.makedirs(mp4_new_name)
    add_watermark_to_video(v_a_txt_file)


def move_final_video_set():
    databe_path='/media/xiaolong/datapool/data/youtube/news/sina_news/2019-03-16/video/'
    video_list=glob.glob(databe_path+'*haha.mp4')
    for video_path in video_list:
        upload_automatic_video(video_path)


def upload_automatic_video(video_path):
    #title_str=''.decode('utf-8','ignore')
    base_path='/media/xiaolong/datapool/data/youtube/news/sina_news/2019-03-16/video/'
    yaml_file_path=base_path+'upload_result.yaml'


    title_str=video_path.split('_audio')[0].split(base_path)[-1].decode('utf-8','ignore')
    credential_path='/media/xiaolong/datapool/banana_news.json'.decode('utf-8','ignore')
    playlist_name='1分钟新闻'.decode('utf-8','ignore')#.encode("ascii","ignore")
    #video_path='/media/xiaolong/datapool/data/downloads/test/result_stocking16_audio.mp4'.decode('utf-8','ignore')
    description_str='香蕉频道，最新最热的新闻，欢迎订阅,谢谢支持'.decode('utf-8','ignore')#.encode("ascii","ignore")
    # import IPython
    # IPython.embed()
    with open(yaml_file_path, 'r') as stream:
        all_dic=yaml.load(stream)
    if title_str in all_dic:
        print('youtube already exists')
        return

    cmd=upload_video_youtube(title_str,playlist_name,video_path,description_str,'娱乐新闻',credential_path)
    try:
        os.system(cmd)

    except:
        print('upload errors')
        return 
    with open(yaml_file_path, 'a') as yaml_file:
        yaml_file.write("{}:{} \n".format(title_str, 1))# , default_flow_style=False)

def upload_video_youtube(title_str,playlist_name,video_path,description_str,tag_str,credential_path):
    cmd='youtube-upload --title='+title_str+' \
  --playlist='+playlist_name+' \
  --tags='+tag_str+' \
  --description='+description_str+' \
  --client-secrets='+credential_path+' \
  --embeddable=True'+' '+video_path
    return cmd


def generate_tv_broad():
    base_path='/media/xiaolong/datapool/data/cut/original/'
    release_path='/media/xiaolong/datapool/data/cut/cut_code/'
    mp4_files=glob.glob(base_path+'*.mp4')
    for mp4_file in mp4_files:
        input_file=mp4_file
        output_file=input_file.replace(base_path,release_path).replace('.mp4','_cut.mp4')
        if not os.path.exists(output_file):
            #cmd='ffmpeg -i '+input_file+' -max_muxing_queue_size 400 -ss 00:00:00 -to 00:01:59  -c:v libx264 -c:a libfaac -c copy '+output_file
            cmd='ffmpeg -i '+input_file+'  -copyinkf -ss 00:02:00 -to 00:02:37 '+output_file
          #-vcodec copy -acodec
        #import IPython
        #IPython.embed()
            os.system(cmd)
        if os.path.exists(output_file):
            output_mp4=input_file.replace(base_path,release_path)
            add_watermark_to_tv_video(output_file,output_mp4)

def add_watermark_to_tv_video(input_mp4,output_mp4,watermark_file='/media/xiaolong/datapool/landmark_fun_video_new.png'):
    if not os.path.exists(output_mp4):
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -max_muxing_queue_size 400 -filter_complex "overlay=10:10" '+output_mp4)

def change_logo():
    input_mp4='/media/xiaolong/datapool/data/cut/original/story.mkv'
    output_mp4=input_mp4.replace('.mkv','_logo.mkv')
    add_watermark_to_tv_video_v1(input_mp4,output_mp4,\
        watermark_file='/media/xiaolong/datapool/landmark_fun_video_middle.png')

def add_watermark_to_tv_video_v1(input_mp4,output_mp4,watermark_file='/media/xiaolong/datapool/landmark_fun_video_new.png'):
    if not os.path.exists(output_mp4):
        os.system('ffmpeg -i '+ input_mp4+' -i '+watermark_file+' -max_muxing_queue_size 400 -filter_complex "overlay=10:10" '+output_mp4)


def generate_news_video_set():
    databe_path='/media/xiaolong/datapool/data/youtube/news/sina_news/'+str(date.today())+'/json/'
    databe_path='/media/xiaolong/datapool/data/youtube/news/sina_news/2019-03-18/json/'

    #'/media/xiaolong/datapool/data/youtube/news/mitbbs/news_database/'
    pickle_files=glob.glob(databe_path+'*.p')
    for pickle_file_path in pickle_files:
        generate_news_video_function(pickle_file_path,lan='chinese')

if __name__ == '__main__':

    #generate_news_video_set()
    #generate_tv_broad()
    change_logo()
    #move_final_video_set()
    #ffmpeg -i input.mp3 -ss 00:00:01 -to 00:02:00 -c copy bana_news.mp3
    #ffmpeg -i output3.mkv -t 00:04:20 -c:v libx264 -c:a libfaac output-cut.mkv
#     font_txt_path='/media/xiaolong/datapool/toolbox/video_audio_tool/font/simsun.ttc'
#     text_file='/media/xiaolong/datapool/data/youtube/news/sina_news/2019-03-16/video/article.txt'
#     font_setting_str='drawtext=fontsize=30:fontcolor=White'
#     input_video=result_mp4_file.replace('.mp4','_audio.mp4')
#     output_video=result_mp4_file.replace('.mp4','_text.mp4')
#     ffmpeg_str='ffmpeg -i '+input_video+' -vf '+'[in]'+font_setting_str+':fontfile='+font_txt_path+':textfile='+text_file+':x=0:y=h-100'+' -y '+output_video
#     text_file.replace('.txt','_v1.txt')
#     text_data=data['text_article'].split('。')


#     with open(text_file,'rw+')  as f:
#         for text in text_data:
#             f.write(text+'\n')


#     # ffmpeg_str='ffmpeg -i '+input_video+' -vf '+'[in]'+font_setting_str+':fontfile='+font_txt_path+':text=onLine1:x=0:y=(h)/2,'+' -y '+output_video
#     #     +font_setting_str+':fontfile='+font_txt_path+':text=onLine2:x=(w)/2:y=((h)/2)+2,' \
#     #     +font_setting_str+':fontfile='+font_txt_path+':text=onLine3:x=(w)/2:y=((h)/2)+50,' \
#     #         +' -y '+output_video
#     os.system(ffmpeg_str)

# ffmpeg -i test_in.avi -vf "[in]drawtext=fontsize=20:fontcolor=White:fontfile='/Windows/Fonts/arial.ttf':text='onLine1':x=(w)/2:y=(h)/2, \
#     drawtext=fontsize=20:fontcolor=White:fontfile='/Windows/Fonts/arial.ttf':text='onLine2':x=(w)/2:y=((h)/2)+25, \
#         drawtext=fontsize=20:fontcolor=White:fontfile='/Windows/Fonts/arial.ttf':text='onLine3':x=(w)/2:y=((h)/2)+50[out]" -y test_out.avi

    #ffmpeg -i input -filter_complex "drawtext=text='Summer Video':enable='between(t,15,20)',fade=t=in:start_time=15:d=0.5:alpha=1,fade=t=out:start_time=19.5:d=0.5:alpha=1[fg];[0][fg]overlay=format=auto,format=yuv420p" -c:a copy output.mp4