from psychopy import visual, logging
import os

from code.load_data import read_text_from_file
from code.check_exit import check_exit
from code.triggers import send_trigger_eeg


def ophthalmic_procedure(win, screen_res, frames_per_sec, trigger_no, triggers_list, text_size=40, text_color='white',
                         text_font='Arial', port_eeg=None, vis_offset=60, secs_of_msg=5, secs_of_blinks=9,
                         secs_of_saccades=9):
    """
    :param text_font:
    :param text_color:
    :param port_nirs:
    :param port_eeg:
    :param send_nirs_triggers:
    :param text_size:
    :param triggers_list:
    :param trigger_no:
    :param frames_per_sec:
    :param screen_res:
    :param win:
    :param send_eeg_triggers:
    :param vis_offset: No of pixels of margin between fixation crosses and screen border
    :param secs_of_msg:
    :param secs_of_blinks:
    :param secs_of_saccades:
    :return:
    """
    logging.info('Starting ophthalmic procedure... ')
    # prepare stim's
    ophthalmic_info = read_text_from_file(os.path.join('.', 'messages', 'ophthalmic_instruction.txt'))
    corners_info = read_text_from_file(os.path.join('.', 'messages', 'ophthalmic_corners.txt'))

    ophthalmic_info = visual.TextStim(win=win, font=text_font, text=ophthalmic_info, height=text_size,
                                      wrapWidth=screen_res['width'], color=text_color)
    corners_info = visual.TextStim(win=win, font=text_font, text=corners_info, height=text_size,
                                   wrapWidth=screen_res['width'], color=text_color)
    # crosses are located in corners
    crosses = [[x, y] for x in [-screen_res['width'] / 2 + vis_offset, screen_res['width'] / 2 - vis_offset] for y in
               [-screen_res['height'] / 2 + vis_offset, screen_res['height'] / 2 - vis_offset]]
    crosses = [visual.TextStim(win=win, font=text_font, text=u'+', height=3 * text_size, color=text_color, pos=pos) for
               pos in crosses]

    ophthalmic_info.setAutoDraw(True)
    for _ in range(frames_per_sec * secs_of_msg):
        win.flip()
        check_exit()
    ophthalmic_info.setAutoDraw(False)
    win.flip()

    for frame_counter in range(frames_per_sec * secs_of_blinks):
        if frame_counter % frames_per_sec == 0:
            trigger_no = send_trigger_eeg(trigger_no=trigger_no, port_eeg=port_eeg)
            triggers_list.append((str(trigger_no - 1), "BLINK"))
        win.flip()
        check_exit()

    corners_info.setAutoDraw(True)
    for _ in range(frames_per_sec * secs_of_msg):
        win.flip()
        check_exit()
    corners_info.setAutoDraw(False)

    [item.setAutoDraw(True) for item in crosses]
    for frame_counter in range(frames_per_sec * secs_of_saccades):
        if frame_counter % frames_per_sec == 0:
            trigger_no = send_trigger_eeg(trigger_no=trigger_no, port_eeg=port_eeg)
            triggers_list.append((str(trigger_no - 1), "BLINK"))
        win.flip()
        check_exit()
    [item.setAutoDraw(False) for item in crosses]
    win.flip()

    logging.info('Ophthalmic procedure finished correctly!')

    return trigger_no, triggers_list
