import os
import shutil
import subprocess
from whisper_wrapper import *
from srt_translate import *

to_sub_path = "/home/opc/PIKPAK/to_sub" 
subbed_path = "/home/opc/PIKPAK/subbed"
temp_folder_path = "/home/opc/DEV/temp_files"

def translate(original_file_path):
    #first_check_if_file_exists
    if not os.path.exists(original_file_path):
        raise "{file_name} does not exists"
    file_name = os.path.basename(original_file_path)

    
    # convert to wav and place it in temp folder. use ffmpeg
    wav_file_name = file_name.replace(".mp4",".wav")
    wav_file_path = os.path.join(temp_folder_path,wav_file_name)
    ffmpeg_cmd = ['ffmpeg','-i',original_file_path,'-y','-vn',wav_file_path]
    subprocess.call(ffmpeg_cmd)

    #now convert wav to japanese subs. japanese srt file will be end with .ja.whisperjav.srt and
    #will be placed in same folder as wav file

    run_whisper_wrapper(audio_path=wav_file_path)

    ja_srt_file_path = file_name.replace(".mp4",".ja.whisperjav.srt")

    #now translate the srt file. it will return the final srt target path, which will be in the temp folder
    # english srt file will end with .en.srt
    en_srt_file_path = translate_srt(ja_srt_file_path,temp_folder_path)

    #create new folder with file name in pikpak subbed folder
    new_folder_name =file_name.replace(".mp4","")
    new_folder_path = os.path.join(subbed_path,new_folder_name)
    if not os.path.exists(new_folder_path):
        os.mkdir(new_folder_path)
        
    #now move the en srt to pikpak subbed folder
    shutil.move(en_srt_file_path,new_folder_path)

    #move the original_video_file as well
    shutil.move(original_file_path,new_folder_path)

    #clean up temp folder
    for root, dirs, files in os.walk(temp_folder_path):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

    return True
