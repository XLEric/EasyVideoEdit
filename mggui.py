import os
import tkinter
from time import sleep
import time
from itertools import count
# import pyaudio
from moviepy.editor import *
from threading import Thread
from multiprocessing import Pool
from tkinter.filedialog import askopenfilename
from PIL import Image,ImageTk
from multiprocessing import Manager
import cv2
import copy
import json
root = tkinter.Tk()
root.title('EasyVideoEdit')
root.geometry('860x640+200+100')

isplaying = False
global_image_start_id = 0
global_image_end_id = 0

global_image_start_time = 0
global_image_end_time = 0

global_play = False

global_start_time = 0.
global_end_time = 0.

global_seg_idx = 0

lbVideo = tkinter.Label(root,bg = 'white')
lbVideo.pack(fill = tkinter.BOTH, expand = tkinter.YES)

s_step = 1
flag_choose_segment = False

def close_clip(vidya_clip):
    # noinspection PyBroadException
    try:
        vidya_clip.reader.close()
        del vidya_clip.reader
        if vidya_clip.audio is not None:
            vidya_clip.audio.reader.close_proc()
            del vidya_clip.audio
        del vidya_clip
    except Exception:
        # sys.exc_clear()
        pass

def play_video(video,frame_count):

    global global_image_start_id
    global global_start_time
    global global_end_time

    vw = video.w
    vh = video.h

    w = root.winfo_width()
    h = root.winfo_height()

    ratio = min(w/vw,h,vh)
    size = (int(vw*ratio),int(vh*ratio))
    duration = video.duration

    print('frame_count : ',frame_count)
    print('duration : ',duration)
    fps_wait_time = duration/frame_count
    print('fps_wait_time : ',fps_wait_time)
    st = time.time()
    idx = 0
    flag_cnt = 0
    for frame in video.iter_frames(fps=video.fps):

        str = time.time()
        flag_cnt += 1
        if not isplaying:
            break

        frame = Image.fromarray(frame).resize(size)
        frame = ImageTk.PhotoImage(frame)
        lbVideo['image'] = frame
        lbVideo.image = frame
        lbVideo.update()

        # idx += 1
        # nt = time.time()
        # no_wait = True
        # etr = (time.time()-str)
        # if (frame_count-idx)>=1:
        #     r_t = ((duration)-((nt-st)))/(frame_count-idx)
        #
        #     if etr < r_t:
        #         if r_t>0:
        #             no_wait = False
        #             fps_wait_time = r_t-etr
        #     # print('id {}/{}  :   r_t {} etr {} fps_wait_time {}'.format(frame_count-idx,frame_count,r_t,etr,fps_wait_time))
        #     # print('last ~',(duration)-(nt-st))
        #
        #
        # if no_wait == False and flag_cnt >30:
        #     sleep(fps_wait_time)
        # else:
        #     print('no wait')
        #     pass
    et = time.time()
    print('video cost time : ',(et-st))
#
# def play_audio(audio):
#     p = pyaudio.PyAudio()
#
#     stream = p.open(format = pyaudio.paFloat32,
#                     channels=2,
#                     rate=44100,
#                     output=True)
#     idx = 0
#     st = time.time()
#     for chunk in audio.iter_frames():
#         if not isplaying:
#             break
#         stream.write(chunk.astype('float32').tostring())
#     et = time.time()
#     print('audio cost time : ',(et-st))
#     p.terminate()


def video_param(video):
    dict = {}
    dict['fps'] = int(video.get(cv2.CAP_PROP_FPS))
    dict['size'] = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    dict['frame_count'] = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    return dict
def print_video_param(dict):
    print('\n/*****************  video param ****************/\n')
    for key in dict.keys():
        print('{} : {}'.format(key,dict[key]))
    print('\n')
def opencv_video(video):
    # print("子进程开始执行>>> pid={},ppid={}".format(os.getpid(),os.getppid()))
    # video = cv2.VideoCapture(path)
    #
    dict_ =video_param(video)
    # m_.append({'size':dict_['size']})
    print_video_param(dict_)

    idx = 0
    print('video start ~')

    # while m_[0]["start"] == False:
    #     time.sleep(0.001)
        # print(m_[0]["start"])
    fps_wait = int(max((1000./dict_['fps']-1),1))
    print('opencv',fps_wait,' ms')
    while True:
        ret, img = video.read()
        if not isplaying:
            break

        if ret:
            milliseconds = video.get(cv2.CAP_PROP_POS_MSEC)
            # print('time:',milliseconds,end = '\r')
            # print('milliseconds : ',milliseconds)
            idx += 1
            cv2.putText(img, "[{}/{}]".format(idx,dict_['frame_count']), (5,35),cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 0, 20),3)
            cv2.putText(img, "[{}/{}]".format(idx,dict_['frame_count']), (5,35),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 220),1)

            cv2.namedWindow('video',0)
            cv2.imshow('video',img)

            if cv2.waitKey(fps_wait) == 27:
                break
        else:
            break
    cv2.destroyAllWindows()
    video.release()




def play_clips(path_):
    global global_image_start_time,global_image_end_time

    movie = VideoFileClip(path_)



    while True:
        time.sleep(0.05)
        if not isplaying:
            break
        if global_play:
            str_time = global_image_start_time/1000.
            end_time = global_image_end_time/1000.
            width_ = movie.size[0]
            height_ = movie.size[1]
            print(width_,height_)
            movie_clip = movie.subclip(str_time, end_time)# 将剪切的片段保存
            movie_clip.resize((int(width_/3),int(height_/3))).preview()
            # movie_clip.resize((640,480)).preview()


def opencv_sync(path_):
    global global_play
    global global_image_start_id
    global global_image_end_id
    global global_image_start_time,global_image_end_time
    global isplaying
    movie = VideoFileClip(path_)

    video_ = cv2.VideoCapture(path_)
    vw = movie.w
    vh = movie.h

    w = root.winfo_width()
    h = root.winfo_height()

    ratio = min(w/vw,h,vh)
    size = (int(vw*ratio/2.),int(vh*ratio/2.))
    #
    dict_ =video_param(video_)
    print_video_param(dict_)

    idx = 0
    print('video start ~')

    while True:

        time.sleep(0.1)
        if not isplaying:
            break
        if global_play:

            str_time = global_image_start_time/1000.
            end_time = global_image_end_time/1000.
            movie_clip = movie.subclip(str_time, end_time)# 将剪切的片段保存
            time.sleep(0.2)
            global_play = False

            for frame in movie_clip.iter_frames(fps=movie.fps):#

                if global_play == True:
                    break
                str = time.time()
                # flag_cnt += 1
                if not isplaying:
                    break

                frame = Image.fromarray(frame).resize(size)
                frame = ImageTk.PhotoImage(frame)
                lbVideo['image'] = frame
                lbVideo.image = frame
                lbVideo.update()


def opencv_checkid_start_image(path_):

    global global_image_start_id
    global global_image_end_id
    global global_play
    global global_image_start_time,global_image_end_time
    global isplaying
    global s_step
    global flag_choose_segment
    video_ = cv2.VideoCapture(path_)
    dict_ =video_param(video_)
    print_video_param(dict_)


    video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_start_id)# 从关键帧取得
    ret, img_ = video_.read()

    if ret:
        global_image_start_time = video_.get(cv2.CAP_PROP_POS_MSEC)
        cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 0, 20),6)
        cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

        cv2.namedWindow('check_start_image',0)
        cv2.imshow('check_start_image',img_)

        cv2.waitKey(1)

    while True:
        if not isplaying:
            break

        if flag_choose_segment:
            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_start_id)# 从关键帧取得

            ret, img_ = video_.read()
            global_image_start_time = video_.get(cv2.CAP_PROP_POS_MSEC)

            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            #
            if ret:
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 0, 20),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_start_image',0)
                cv2.imshow('check_start_image',img_)

                key = cv2.waitKey(1)

                flag_choose_segment = False


        key = cv2.waitKey(1)
        if key == ord('a') or key == ord('A') and global_play == False:#
            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            global_play = True
        if key == ord('s') or key == ord('S') and global_play == False:#
            if global_image_start_id >= s_step:
                global_image_start_id -= s_step

            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_start_id)# 从关键帧取得


            ret, img_ = video_.read()
            global_image_start_time = video_.get(cv2.CAP_PROP_POS_MSEC)


            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            #
            if ret:
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 0, 20),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_start_image',0)
                cv2.imshow('check_start_image',img_)

                key = cv2.waitKey(1)

        elif key == ord('d') or key == ord('D') and global_play == False:#
            if global_image_start_id < (dict_['frame_count']-1-s_step):
                global_image_start_id += s_step

            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_start_id)# 从关键帧取得


            ret, img_ = video_.read()
            global_image_start_time = video_.get(cv2.CAP_PROP_POS_MSEC)
            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            #
            if ret:
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 0, 20),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_start_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_start_image',0)
                cv2.imshow('check_start_image',img_)

                key = cv2.waitKey(1)

    cv2.destroyAllWindows()
    video_.release()
    video_ = None

def opencv_checkid_end_image(path_):

    global global_image_start_id
    global global_image_end_id
    global global_play
    global global_image_start_time,global_image_end_time
    global isplaying
    global s_step
    global flag_choose_segment
    video_ = cv2.VideoCapture(path_)

    # video_.set(cv2.CAP_PROP_FRAME_WIDTH,640);
    # video_.set(cv2.CAP_PROP_FRAME_HEIGHT,240);

    dict_ =video_param(video_)
    print_video_param(dict_)

    global_image_end_id = dict_['frame_count']-1

    video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_end_id)# 从关键帧取得
    ret, img_ = video_.read()

    if ret:
        global_image_end_time = video_.get(cv2.CAP_PROP_POS_MSEC)
        cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (55, 0, 220),6)
        cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

        cv2.namedWindow('check_end_image',0)
        cv2.imshow('check_end_image',img_)

        cv2.waitKey(1)

    while True:
        if not isplaying:
            break

        if flag_choose_segment:
            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_end_id)# 从关键帧取得
            ret, img_ = video_.read()
            # print(img_.shape)
            global_image_end_time = video_.get(cv2.CAP_PROP_POS_MSEC)

            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            #
            if ret:
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (55, 0, 220),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_end_image',0)
                cv2.imshow('check_end_image',img_)

                key = cv2.waitKey(1)
                flag_choose_segment = False

        key = cv2.waitKey(1)
        if key == ord('a') or key == ord('A') and global_play == False:#
            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            global_play = True
        if key == ord('s') or key == ord('S') and global_play == False:#
            if global_image_end_id>=s_step:
                global_image_end_id -= s_step

            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_end_id)# 从关键帧取得
            ret, img_ = video_.read()
            # print(img_.shape)
            global_image_end_time = video_.get(cv2.CAP_PROP_POS_MSEC)

            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            #
            if ret:
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (55, 0, 220),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_end_image',0)
                cv2.imshow('check_end_image',img_)

                key = cv2.waitKey(1)

        elif key == ord('d') or key == ord('D') and global_play == False:#
            if global_image_end_id < (dict_['frame_count']-s_step-1):
                global_image_end_id += s_step

            video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_end_id)# 从关键帧取得
            ret, img_ = video_.read()
            global_image_end_time = video_.get(cv2.CAP_PROP_POS_MSEC)
            #
            print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
            if ret:
                # print('------------------->>> opencv_checkid_start_image',global_image_start_id)
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (55, 0, 220),6)
                cv2.putText(img_, "[{}/{}]".format(global_image_end_id,dict_['frame_count']), (5,45),cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 155, 120),3)

                cv2.namedWindow('check_end_image',0)
                cv2.imshow('check_end_image',img_)

                key = cv2.waitKey(1)

    cv2.destroyAllWindows()
    video_.release()
    video_ = None

def moviepy_video(path,m_):
    print("子进程开始执行>>> pid={},ppid={}".format(os.getpid(),os.getppid()))
    movie = VideoFileClip(path)
    time.sleep(2.)

    tmp = m_[0]
    tmp["start"] = True
    m_[0] = tmp

    print(m_)

    # movie.preview()
    # print(movie.size())
    movie.resize((int(m_[1]['size'][0]/2),int(m_[1]['size'][1]/2))).preview()
    # movie.ipython_display(width=720)
    print('------------->>>')

def clip(path,m_):

    movie = VideoFileClip(path)

    vw = movie.w
    vh = movie.h

    w = root.winfo_width()
    h = root.winfo_height()

    ratio = min(w/vw,h,vh)
    size = (int(vw*ratio),int(vh*ratio))

    time.sleep(2.)
    for frame in movie.iter_frames(fps=movie.fps):

        # str = time.time()
        # flag_cnt += 1

        frame = Image.fromarray(frame).resize(size)
        frame = ImageTk.PhotoImage(frame)
        print('',type(frame))
        lbVideo['image'] = frame
        lbVideo.image = frame
        lbVideo.update()

def opencv_video(path,m_):

    print("子进程开始执行>>> pid={},ppid={}".format(os.getpid(),os.getppid()))
    video = cv2.VideoCapture(path)

    dict_ =video_param(video)
    m_.append({'size':dict_['size']})
    print_video_param(dict_)

    idx = 0
    print('video start ~')

    while m_[0]["start"] == False:
        time.sleep(0.001)
        # print(m_[0]["start"])

    while True:
            ret, img = video.read()


            if ret:
                milliseconds = video.get(cv2.CAP_PROP_POS_MSEC)
                print('time:',milliseconds,end = '\r')
                # print('milliseconds : ',milliseconds)
                idx += 1
                cv2.putText(img, "[{}/{}]".format(idx,dict_['frame_count']), (5,25),cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 20),3)
                cv2.putText(img, "[{}/{}]".format(idx,dict_['frame_count']), (5,25),cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 220),1)

                cv2.namedWindow('video',0)
                cv2.imshow('video',img)

                if cv2.waitKey(1) == 27:
                    break
            else:
                break
    cv2.destroyAllWindows()
    video.release()

def save_clips(path_):
    global global_image_start_time,global_image_end_time
    global global_image_start_id
    global global_image_end_id
    global global_seg_idx
    movie = VideoFileClip(path_)

    path_make = './video_make/'
    if not os.path.exists(path_make):
        os.mkdir(path_make)
    doc_ = path_.split('/')[-1].strip('.mp4').strip('.MP4')+'/'
    if not os.path.exists(path_make+doc_):
        os.mkdir(path_make+doc_)
    save_idx = 0
    while True:
        time.sleep(0.05)
        if not isplaying:
            break
        if global_play:
            save_idx = global_seg_idx
            #-------
            m_dict = {
                'start_frame':global_image_start_id,
                's_time':global_image_start_time,

                'end_frame':global_image_end_id,
                'e_time':global_image_end_time,
                }

            f = open(path_make+doc_ + "clip_{}.json".format(save_idx),"w")
            json.dump(m_dict,f,indent = 1)
            f.close()
            #-------
            root.title(f'开始剪辑...')
            str_time = global_image_start_time/1000.
            end_time = global_image_end_time/1000.

            movie_clip = movie.subclip(str_time, end_time)# 将剪切的片段保存
            movie_clip.write_videofile(path_make+doc_ + "clip_{}.mp4".format(save_idx))
            root.title(f'剪辑完成...')
            time.sleep(1.)
            root.title(f'正在播放')

def choose_segment(path,cfg):
    global global_image_start_id
    global global_image_end_id
    global global_image_start_time,global_image_end_time
    global flag_choose_segment
    global global_play
    global global_seg_idx

    video = cv2.VideoCapture(path)

    len_ = len(cfg['data'])

    print('video_segment num : ',len_)

    seg_idx = 0

    #---------------------------
    if len_ > 0:
        image_start_id = cfg['data'][seg_idx]['start_frame']
        image_end_id = cfg['data'][seg_idx]['end_frame']

        global_image_start_id = cfg['data'][seg_idx]['start_frame']
        global_image_end_id = cfg['data'][seg_idx]['end_frame']
        global_image_start_time = cfg['data'][seg_idx]['s_time']
        global_image_end_time = cfg['data'][seg_idx]['e_time']


        video.set(cv2.CAP_PROP_POS_FRAMES, int((image_start_id+image_end_id)/2))# 从关键帧取得
        ret, img_ = video.read()

        flag_choose_segment = True

        cv2.putText(img_, "[Part {} - {}:{}]".format(seg_idx,global_image_start_id,global_image_end_id), (5,55),cv2.FONT_HERSHEY_DUPLEX, 1.9, (255, 0, 20),20)
        cv2.putText(img_, "[Part {} - {}:{}]".format(seg_idx,global_image_start_id,global_image_end_id), (5,55),cv2.FONT_HERSHEY_DUPLEX, 1.9, (0, 255, 220),5)

        cv2.namedWindow('segment',0)
        cv2.imshow('segment',img_)
        cv2.waitKey(10)

        time.sleep(1)
        flag_choose_segment = False

    while True:
        time.sleep(0.1)
        if global_play == False:
            # global_image_start_id = video_.set(cv2.CAP_PROP_POS_FRAMES, global_image_start_id)# 从关键帧取得
            #
            #
            # ret, img_ = video_.read()
            # global_image_start_time = video_.get(cv2.CAP_PROP_POS_MSEC)
            # global_image_end_id =


            cv2.namedWindow('segment',0)

            key_ = cv2.waitKey(5)

            if key_ == ord('a') or key_ == ord('A') and global_play == False:#
                print('check image start end time [ {:.4} ~ {:.4} ]'.format(global_image_start_time/1000.,global_image_end_time/1000.))
                global_seg_idx = seg_idx
                global_play = True

            if (key_ == ord('d') or key_ == ord('D')) and len_>0:
                seg_idx += 1
                if seg_idx>=(len_):
                    seg_idx = 0
                print('seg_idx : ',seg_idx)
                global_image_start_id = cfg['data'][seg_idx]['start_frame']
                global_image_end_id = cfg['data'][seg_idx]['end_frame']
                global_image_start_time = cfg['data'][seg_idx]['s_time']
                global_image_end_time = cfg['data'][seg_idx]['e_time']

                video.set(cv2.CAP_PROP_POS_FRAMES, int((global_image_start_id+global_image_end_id)/2))# 从关键帧取得
                ret, img_ = video.read()

                cv2.putText(img_, "[Part {} - {}:{}]".format(seg_idx,global_image_start_id,global_image_end_id), (5,55),cv2.FONT_HERSHEY_DUPLEX, 1.9, (255, 0, 20),20)
                cv2.putText(img_, "[Part {} - {}:{}]".format(seg_idx,global_image_start_id,global_image_end_id), (5,55),cv2.FONT_HERSHEY_DUPLEX, 1.9, (0, 255, 220),5)
                flag_choose_segment = True
                cv2.namedWindow('segment',0)
                cv2.imshow('segment',img_)
                cv2.waitKey(1)
                #

                time.sleep(2)
                flag_choose_segment = False


    cv2.destroyAllWindows()
    video.release()

# 创建主菜单
MainMenu = tkinter.Menu(root)
subMenu = tkinter.Menu(tearoff=0)
def open_video():
    global isplaying
    global global_play
    global global_image_start_id
    global s_step
    global flag_choose_segment
    global global_seg_idx

    global_seg_idx = 0

    flag_choose_segment = False
    s_step = 2

    global_image_start_id = 0
    r_ = False
    isplaying = r_
    global_play = False
    fn  = askopenfilename(title = "打开视频文件",
                            filetypes = [('视频','*.mp4 *.avi')])

    if fn:

        try:
            cv2.destroyAllWindows()
        except:
            pass

        path_json = './video_ana/'+fn.split('/')[-1].replace('.mp4','.json').replace('.MP4','.json')
        dict_seg = {}
        dict_seg['data'] = []
        if os.access(path_json,os.F_OK):# checkpoint
            f = open(path_json, encoding='utf-8')#读取 json文件
            dict_seg = json.load(f)
            f.close()

            print('\n dict_seg : \n',dict_seg)

        isplaying = False
        time.sleep(1.)

        # ps=Pool(2)
        print('打开视频 ：',fn)
        cv_video = cv2.VideoCapture(fn)
        #
        root.title(f'正在播放')



        isplaying = True

        t4 = Thread(target = opencv_sync,args = (fn,))
        t4.daemon = True
        t4.start()

        t5 = Thread(target = opencv_checkid_start_image,args = (fn,))
        t5.daemon = True
        t5.start()

        t6 = Thread(target = opencv_checkid_end_image,args = (fn,))
        t6.daemon = True
        t6.start()

        t7 = Thread(target =save_clips,args = (fn,))
        t7.daemon = True
        t7.start()

        if os.access(path_json,os.F_OK):
            t8 = Thread(target = choose_segment,args = (fn,dict_seg,))
            t8.daemon = True
            t8.start()





def exiting():
    global isplaying
    isplaying = False
    sleep(0.05)
    try:
        cv2.destroyAllWindows()
    except:
        pass
    root.destroy()


if __name__ == '__main__':

    subMenu.add_command( label = "打开视频文件",command=open_video)
    MainMenu.add_cascade(label = '文件',menu = subMenu)



    root['menu'] = MainMenu
    root.protocol('WM_DELETE_WINDOW',exiting)
    root.mainloop()
