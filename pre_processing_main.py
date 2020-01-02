# -*- coding: utf-8 -*-
import os, cv2
import imghdr
import sys
sys.path.append('/media/xiaolong/datapool/toolbox/video_audio_tool/')
sys.path.append('/media/xiaolong/datapool/toolbox/google-images-download/')


#import make_video_main #import *
import ops
from gtts import gTTS
import text_to_speech
import glob
from os import listdir
import shutil
chrome_path='/media/xiaolong/datapool/data/chromedriver'
#/media/xiaolong/datapool/data$ ./chromedriver
def image_filter_function(path='/media/xiaolong/datapool/data/downloads/黑丝美女/'):
    all_files=listdir(path)
    for filei in all_files:
        source_path=path+filei
        img_category=imghdr.what(source_path)
        current_category=filei.split('.')[-1]
        if img_category==None:
                os.remove(source_path)
        elif img_category!=current_category:
                file_prefix=filei.split(current_category)[0]
                shutil.move(source_path,path+file_prefix+str(img_category))

def image_re_arrange_function(path='/media/xiaolong/datapool/data/downloads/丝袜美女/'):
    all_files=listdir(path)
    destinate_path='/media/xiaolong/datapool/data/downloads/siwameinv/'
    count=len(glob.glob(destinate_path+'*'))+1
    for filei in all_files:
        source_path=path+filei
        img_category=imghdr.what(source_path)
        current_category=filei.split('.')[-1]
        if img_category==None:
                os.remove(source_path)
                continue
        elif img_category!=current_category:
                file_prefix=filei.split(current_category)[0]
                shutil.move(source_path,path+file_prefix+str(img_category))
        shutil.copyfile(source_path,destinate_path+str(count)+'.'+str(img_category))
        count=count+1



def generate_mp3_file(txt_string='hello',mp3_output_path='hello.mp3'):
    tts = gTTS(txt_string)
    tts.save(mp3_output_path)

def generate_video_main(audio_file_path,video_file_path):
    video_audio_dir=video_file_path.replace('.mp4','_v.mp4')
    ops.combine_audio_video_cmd(audio_file_path, video_file_path, video_audio_dir)

    #if not os.path.exists(video_result_path_name) and not os.path.exists(video_audio_dir):
    #    make_video_main.save_avi(img_frames_save_path, video_result_path_name, audio_duration=audio_duration, audio_dir=audio_file_path, img_h=512, img_w=452)

def generate_video_path(audio_file_path,video_file_path):
    #file_path='/media/xiaolong/datapool/media_data/slideshow/ffmpeg-video-slideshow-scripts/'
    #audio_file_path=file_path+'lady_gaga.mp3'
    #video_file_path=file_path+'lady_gaga.mp4'
    generate_video_main(audio_file_path,video_file_path)


def download_google_test_image(key_word='健身美女',output_path='/media/xiaolong/datapool/data/downloads/'):
    from google_images_download import google_images_download   #importing the library
    response = google_images_download.googleimagesdownload()   #class instantiation
    arguments = {"keywords":key_word,"output_directory":output_path,"limit":1000000,"chromedriver":chrome_path,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    print(paths)   #printing absolute paths of the downloaded images

def download_google_image(key_word='健身美女',output_path='/media/xiaolong/datapool/data/downloads/'):
    from google_images_download import google_images_download   #importing the library
    response = google_images_download.googleimagesdownload()   #class instantiation
    arguments = {"keywords":key_word,"output_directory":output_path,\
            'size':'>640*480',\
            "limit":1000000,"chromedriver":chrome_path,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    print(paths)   #printing absolute paths of the downloaded images

def generate_mp3_function(txt_file_path,audio_result_file,lan='chinese'):
    if lan=='chinese':
        text_to_speech.chinese_text_to_speech_gtts(txt_file_path,audio_result_file)
    elif lan=='english':
        text_to_speech.english_google_cloud_tts(txt_file_path,audio_result_file)

def pipeline():
    download_google_image(key_word='wangou')
    generate_mp3_function(txt_file_path,audio_file_path,lan='chinese')
    generate_video_path(audio_file_path,video_file_path)


def cut_audio(video_audio_path_name='/media/xiaolong/datapool/data/youtube_video/audio/gudian.mp3'):
    if 1:
        #video_audio_path_name=video_result_path_name.replace('.','_audio.')
        i=0
        for n in range(0,60,3):
            
            cut_video_name=video_audio_path_name.replace('.mp3','_'+str(i)+'.mp3')
            i=i+1
            time_start='00:'+str(n)+':00'
            string_time="ffmpeg -v quiet -y -i "+video_audio_path_name+ " -vcodec copy -acodec copy -ss "+ time_start+ " -t 00:03:00 -sn "+cut_video_name
            print('get fine')
        #import IPython
        #IPython.embed()
            os.system(string_time)



def cut_video(video_audio_path_name='/media/xiaolong/datapool/data/youtube_video/audio/gudian.mp3'):
    if 1:
        #video_audio_path_name=video_result_path_name.replace('.','_audio.')
        cut_video_name=video_audio_path_name.replace('.mp4','_1.mp4')
        cut_video_name=video_audio_path_name.replace('.mp3','_2.mp3')


        print('get fine')
        #import IPython
        #IPython.embed()
        string_time="ffmpeg -v quiet -y -i "+video_audio_path_name+ " -vcodec copy -acodec copy -ss 00:06:00 -t 00:03:00 -sn "+cut_video_name
        os.system(string_time)


def download_images_main():
        key_words_str=['黑丝美女','运动美女','枪械美女','丁字裤美女','情趣美女','美女搭讪','清纯美女','性感美女',\
        '街拍美女','北方美女','大胸美女','大屁股美女','长腿美女','四川美女','明星美女','桃色美女','成人美女','紧身美女',\
        'asian hot lady','sexy lady','hot girl','girl lingerie','black stocking girl','white stocking girl']
        for key_word in key_words_str:
                download_google_image(key_word=key_word)

#         filepath="/media/xiaolong/datapool/data/book/beauty_key.txt"
#         with open(filepath, 'r') as f:
#                 x = f.readlines()

#         with open(filepath, 'w') as file_handler:
#                 for item in key_words_str:
#                         file_handler.write("{}\n".format(item))

# with open('data.yml', 'w') as outfile:
#         #yaml.dump(data, outfile, default_flow_style=False)


if __name__ == '__main__':

    download_images_main()


