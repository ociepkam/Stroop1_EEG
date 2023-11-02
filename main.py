#!/usr/bin/env python
# -*- coding: utf8 -*
import atexit
import csv
import numpy
import random
from os.path import join

from psychopy import visual, event, logging, gui, core

from code.ophthalmic_procedure import ophthalmic_procedure
from code.check_exit import check_exit
from code.load_data import read_text_from_file, load_config
from code.triggers import *
from misc.screen_misc import get_screen_res, get_frame_rate
from prepare_exp import prepare_exp


# GLOBALS
TEXT_SIZE = 20
TEXT_COLOR = '#505050'
VISUAL_OFFSET = 50
FIGURES_SCALE = 0.4
RESULTS = [['EXP', 'TRIAL_TYPE', 'TEXT', 'COLOR', 'WAIT', 'RESPTIME', 'RT', 'TRUE_KEY', 'ANSWER', 'CORR']]
POSSIBLE_KEYS = ['z', 'x', 'n', 'm']
LEFT_KEYS = POSSIBLE_KEYS[:2]
RIGHT_KEYS = POSSIBLE_KEYS[2:]
# TRIGGER_LIST = []
# TRIGGER_NO = 1


@atexit.register
def save_beh_results():
    num = random.randint(100, 999)
    with open(join('results', '{}_beh_{}.csv'.format(PART_ID, num)), 'w') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()
    # with open(join('results', '{}_triggermap_{}.txt'.format(PART_ID, num)), 'w') as trigger_file:
    #     trigger_writer = csv.writer(trigger_file)
    #     trigger_writer.writerows(TRIGGER_LIST)


def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color="#808080", text=msg, height=TEXT_SIZE, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def show_info_2(win, info, show_time):
    info.setAutoDraw(True)
    win.flip()
    time.sleep(show_time)
    info.setAutoDraw(False)
    check_exit()
    win.flip()


def prepare_key_matching_text(colors_key):
    text = ""
    for color, key in zip(colors_key, POSSIBLE_KEYS):
        text += "klawisz {} gdy wyswietlono napis w kolorze {}\n".format(key.upper(), color)
    return text


def feedb(ans, true_key):
    if data['Feedb']:
        if not ans:
            feedb_msg = no_feedb
        elif ans == true_key:
            feedb_msg = pos_feedb
        elif ans != true_key:
            feedb_msg = neg_feedb
        else:
            raise Exception("Wrong feedb")

        show_info_2(win=win, info=feedb_msg, show_time=data['Feedb_time'])


# doesn't work!!!!!!
# def prepare_trial_info(trial):
#     true_key = KEYS[trial['color']]
#     reaction_time = -1
#     if trial['trial_type'] == 'congruent_strong':
#         triggers = TriggersCongruentStrong
#     elif trial['trial_type'] == 'congruent_weak':
#         triggers = TriggersCongruentWeak
#     elif trial['trial_type'] == 'incongruent_strong':
#         triggers = TriggersIncongruentStrong
#     elif trial['trial_type'] == 'incongruent_weak':
#         triggers = TriggersIncongruentWeak
#     else:
#         triggers = TriggersNeutral
#     return true_key, reaction_time, triggers


def abort_with_error(err):
    logging.critical(err)
    raise Exception(err)


# exp info
data = load_config()

# prepare eeg
# if data['EEG']:
#     try:
#         import parallel
#         EEG = parallel.Parallel()
#         EEG.setData(0x00)
#     except:
#         raise Exception("Can't connect to EEG")
# else:
#     EEG = None


# part info
info = {'Part_id': '', 'Part_age': '20', 'Part_sex': ['MALE', "FEMALE"]}
dictDlg = gui.DlgFromDict(dictionary=info, title='Stroop')  # , fixed=['ExpDate']
if not dictDlg.OK:
    exit(1)
PART_ID = str(info['Part_id'] + info['Part_sex'] + info['Part_age'])

logging.LogFile('results/' + PART_ID + '.log', level=logging.INFO)
logging.info(info)

# prepare screen
SCREEN_RES = dict(get_screen_res())
win = visual.Window(list(SCREEN_RES.values()), fullscr=True, monitor='testMonitor', units='pix', screen=0, color='#262626')
mouse = event.Mouse(visible=False)
fixation = visual.TextStim(win, color=TEXT_COLOR, text='+', height=2 * TEXT_SIZE)

# prepare feedb
pos_feedb = visual.TextStim(win, text=u'Poprawna odpowied\u017A', color=TEXT_COLOR, height=TEXT_SIZE)
neg_feedb = visual.TextStim(win, text=u'Odpowied\u017A niepoprawna', color=TEXT_COLOR, height=TEXT_SIZE)
no_feedb = visual.TextStim(win, text=u'Nie udzieli\u0142e\u015B odpowiedzi', color=TEXT_COLOR, height=TEXT_SIZE)

# prepare trials
training_trials, experiment_trials, colors_to_key, colors_names = prepare_exp(data, win, TEXT_SIZE, data["words_dist"])
blocks = numpy.array_split(experiment_trials, data['Number_of_blocks'])

KEYS = {color: key for color, key in zip(colors_names, POSSIBLE_KEYS)}

keys_mapping_text = prepare_key_matching_text(colors_to_key)

key_labes = visual.TextStim(win=win, text='{0}        {1}                    {2}        {3}'.format(*colors_to_key), color=TEXT_COLOR,
                            wrapWidth=SCREEN_RES['width'],  height=TEXT_SIZE, pos=(0, -7 * VISUAL_OFFSET))

resp_clock = core.Clock()


# if data['ophthalmic_procedure']:
#     frames_per_sec = get_frame_rate(win)
#     TRIGGER_NO, TRIGGER_LIST = ophthalmic_procedure(win=win, port_eeg=EEG, frames_per_sec=frames_per_sec,
#                                                     screen_res=SCREEN_RES, trigger_no=TRIGGER_NO,
#                                                     triggers_list=TRIGGER_LIST)

# ----------------------- Start Stroop ----------------------- #


for idx, block in enumerate(training_trials):
    show_info(win, join('.', 'messages', 'training{}.txt'.format(idx+1)), insert=keys_mapping_text)
    for trial in block:
        # prepare trial
        true_key = KEYS[trial['color']]
        reaction_time = -1
        # true_key, reaction_time, triggers = prepare_trial_info(trial)

        # show fix
        show_info_2(win=win, info=fixation, show_time=data['Fix_time'])
        check_exit()
        # show problem
        event.clearEvents()
        win.callOnFlip(resp_clock.reset)
        for stim in trial['stim']:
            stim.setAutoDraw(True)
        key_labes.setAutoDraw(True)
        win.flip()

        while resp_clock.getTime() < data['Training_Resp_time']:
            key = event.getKeys(keyList=KEYS.values())
            if key:
                reaction_time = resp_clock.getTime()
                break
            check_exit()
            win.flip()

        for stim in trial['stim']:
            stim.setAutoDraw(False)
        key_labes.setAutoDraw(False)
        win.flip()

        if key:
            ans = key[0]
        else:
            ans = '-'
        RESULTS.append(
            ['training', trial['trial_type'], trial['text'], trial['color'], data['Training_Wait_time'],
             data['Training_Resp_time'], reaction_time, true_key, ans, ans == true_key])
        check_exit()

        # show feedb
        if data['Feedb']:
            feedb(key, [true_key])
            check_exit()

        # wait
        time.sleep(data['Training_Wait_time'])
        check_exit()

# ----------- Start experiment ------------- #

show_info(win, join('.', 'messages', 'instruction.txt'), insert=keys_mapping_text)

for idx, block in enumerate(blocks):
    for trial in block:
        # prepare trial
        # true_key, reaction_time, triggers = prepare_trial_info(trial)
        true_key = KEYS[trial['color']]
        reaction_time = -1
        jitter = random.random() * data['Jitter']

        # show fix
        show_info_2(win=win, info=fixation, show_time=data['Fix_time'])
        check_exit()

        # show problem
        event.clearEvents()
        win.callOnFlip(resp_clock.reset)
        for stim in trial['stim']:
            stim.setAutoDraw(True)
        key_labes.setAutoDraw(True)
        win.flip()
        # if data['NIRS']:
        #     NIRS.activate_line(triggers.ProblemAppear)
        # TRIGGER_NO = send_trigger_eeg(TRIGGER_NO, EEG)

        while resp_clock.getTime() < data['Experiment_Resp_time']:
            key = event.getKeys(keyList=KEYS.values())
            if key:
                reaction_time = resp_clock.getTime()
                # if data['NIRS']:
                #     NIRS.activate_line(triggers.ParticipantReact)
                # TRIGGER_NO = send_trigger_eeg(TRIGGER_NO, EEG)
                break
            check_exit()
            win.flip()

        for stim in trial['stim']:
            stim.setAutoDraw(False)
        key_labes.setAutoDraw(False)
        win.flip()

        if key:
            ans = key[0]
        else:
            ans = '-'

        RESULTS.append(
            ['experiment', trial['trial_type'], trial['text'], trial['color'], data['Experiment_Wait_time']+jitter,
             data['Experiment_Resp_time'], reaction_time, true_key, ans, ans == true_key])
        check_exit()

        # triggers
        trig_info = "_{}_{}_{}_{}".format(trial['trial_type'], trial['text'], trial['color'], true_key)
        # stim
        # TRIGGER_LIST.append((str(TRIGGER_NO - 1), "STIM"+trig_info))
        # # re
        # if key:
        #     TRIGGER_LIST.append((str(TRIGGER_NO), "RE"+trig_info+"_"+ans))


        # wait
        time.sleep(data['Experiment_Wait_time'])
        check_exit()

        # jitter
        time.sleep(jitter)
        check_exit()

    if idx+1 < len(blocks):
        show_info(win, join('.', 'messages', 'break{}.txt'.format(idx+1)))

show_info(win, join('.', 'messages', 'end.txt'))
