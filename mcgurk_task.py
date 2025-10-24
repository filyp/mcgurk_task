import random
from pathlib import Path

from psychopy import core, event, logging, visual

from psychopy_experiment_helpers.show_info import show_info
from psychopy_experiment_helpers.triggers_common_usb_simple import TriggerHandler

stimuli_dir = Path(__file__).parent / "videos"

# color_dict = dict(
#     red="#FF0000",
#     green="#00FF00",
#     blue="#0000FF",
#     yellow="#FFFF00",
# )


# class TriggerTypes:
#     VIDEO_START = "VIDEO_START"
#     FIXATION = "FIXATION"
#     STAR_START = "STAR_START"
#     STAR_END = "STAR_END"
#     REACTION = "REACTION"
#     FEEDBACK_POS = "FEEDBACK_POS"
#     FEEDBACK_NEG = "FEEDBACK_NEG"
#     FEEDBACK_NEU = "FEEDBACK_NEU"
#     TOO_SLOW = "TOO_SLOW"
#     TOO_FAST = "TOO_FAST"
#     BLOCK_START = "BLOCK_START"


def deg_to_height(deg, config):
    size_in_cm = (deg / 360) * (2 * 3.1415 * config["Screen_distance"])
    return size_in_cm / config["Screen_height"]


# def load_img(name, size, win, config):
#     return visual.ImageStim(
#         win=win,
#         image=stimuli_dir / name,
#         size=(None, deg_to_height(size, config)),
#         interpolate=True,
#     )


# def load_text(text, win, config):
#     return visual.TextStim(
#         win=win,
#         text=text,
#         color="black",
#         # height=config["Text_feedback_font_size"],
#         height=deg_to_height(config["Speed_feedback_size"], config),
#         font="Arial",
#     )


def mcgurk_task(exp, config, data_saver):
    # unpack necessary objects for easier access
    win = exp.win
    clock = exp.clock

    # EEG triggers
    trigger_handler = TriggerHandler(config["Send_EEG_trigg"], data_saver=data_saver)
    exp.trigger_handler = trigger_handler

    all_video_names = [f.name for f in stimuli_dir.glob("*.mp4")]
    print(all_video_names)

    # todo remove \ufeff from file names

    movies = {
        video_name: visual.MovieStim(
            win,
            stimuli_dir / video_name,
            # size=(None, deg_to_height(3, config)),
            size=(None, config["Video_height"]),
            units="height",  # or 'deg', 'norm', etc.
            volume=1.0,  # Audio volume (0.0 to 1.0)
            loop=False,  # set to True if you want the video to loop
            autoStart=False,  # automatically start playing when drawn
        )
        for video_name in all_video_names[:10]
    }

    # ! greeting texts
    for greeting_text in config["Greeting_texts"]:
        show_info(exp, greeting_text, duration=None)

    for movie_name, movie in movies.items():
        # ! wait for space press
        show_info(exp, config["Wait_text"], duration=None)
        win.flip()  # to make the text disappear
        
        # ! wait some duration
        core.wait(config["Pre_video_duration"])

        # ! draw movie
        movie.seek(0)
        win.flip()  # wait for a new frame to always start the video exactly on new frame
        movie.play()  # it already plays (sound is playing)
        # sending the trigger takes 10ms, but the audio is video is already playing
        #     (at least the audio, video not yet)
        #     so the timing is correct - trigger starts to be sent right after video start
        trigger_handler.send_trigger(movie_name)
        while not movie.isFinished:
            movie.draw()
            win.flip()

    show_info(exp, config["End_text"], duration=None)

    return

    # load stimuli
    # block_order = config["Feedback_types"]
    # random.shuffle(block_order)
    # logging.data(f"Block order: {block_order}")

    def run_trial(speed_feedback, neutral_feedback=False):

        # ! open trial
        trigger_handler.open_trial()
        trial = dict(
            block_num=block_num,
            trial_num=trial_num,
            rt="-",
            allowed_error=allowed_error,
            block_type=block_type,
        )
        # * prepare inter-trial interval
        trial["iti_time"] = random.uniform(config["ITI_min"], config["ITI_max"])

        # ! draw inter-trial interval fixation
        trigger_name = get_trigger_name(TriggerTypes.FIXATION, block_num, block_type)
        trigger_handler.prepare_trigger(trigger_name)
        fixation.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(trial["iti_time"])
        fixation.setAutoDraw(False)
        data_saver.check_exit()

        # ! draw star (start)
        trigger_name = get_trigger_name(TriggerTypes.STAR_START, block_num, block_type)
        trigger_handler.prepare_trigger(trigger_name)
        event.clearEvents()
        win.callOnFlip(clock.reset)
        star.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Star_duration"])

        trigger_name = get_trigger_name(TriggerTypes.STAR_END, block_num, block_type)
        trigger_handler.prepare_trigger(trigger_name)
        star.setAutoDraw(False)
        win.flip()
        trigger_handler.send_trigger()
        data_saver.check_exit()

        # ! wait for press
        keys = event.waitKeys(
            keyList=[config["Response_key"]],
            maxWait=config["Max_wait"],
            timeStamped=clock,
        )
        if keys is not None:
            assert len(keys) == 1
            assert keys[0][0] == config["Response_key"]
            trial["rt"] = keys[0][1]
            trigger_name = get_trigger_name(
                TriggerTypes.REACTION, block_num, block_type
            )
            trigger_handler.prepare_trigger(trigger_name)
            trigger_handler.send_trigger()
        data_saver.check_exit()

        # ! wait with a black screen
        core.wait(config["Pre_feedback_blank_duration"])
        data_saver.check_exit()

        if trial["rt"] == "-":
            trial["feedback"] = "neg"
            trial["acc"] = -1
        else:
            if abs(trial["rt"] - 1) <= allowed_error / 1000:
                trial["feedback"] = "pos"
                trial["acc"] = 1
                allowed_error -= 10
            else:
                trial["feedback"] = "neg"
                trial["acc"] = 0
                allowed_error += 10

        if neutral_feedback:
            trial["feedback"] = "neu"

        # ! draw feedback
        feedback_stim = feedback[block_type][trial["feedback"]]
        feedback_trig = {
            "pos": TriggerTypes.FEEDBACK_POS,
            "neg": TriggerTypes.FEEDBACK_NEG,
            "neu": TriggerTypes.FEEDBACK_NEU,
        }[trial["feedback"]]
        trigger_name = get_trigger_name(feedback_trig, block_num, block_type)
        trigger_handler.prepare_trigger(trigger_name)
        feedback_stim.setAutoDraw(True)
        win.flip()
        trigger_handler.send_trigger()
        core.wait(config["Feedback_duration"])
        # hide feedback
        feedback_stim.setAutoDraw(False)
        win.flip()
        data_saver.check_exit()

        if speed_feedback and trial["feedback"] == "neg":
            # ! draw speed feedback
            if trial["rt"] == "-" or trial["rt"] > 1:
                s_feedback_stim = too_slow
                s_feedback_trig = TriggerTypes.TOO_SLOW
            else:
                s_feedback_stim = too_fast
                s_feedback_trig = TriggerTypes.TOO_FAST

            trigger_name = get_trigger_name(s_feedback_trig, block_num, block_type)
            trigger_handler.prepare_trigger(trigger_name)
            s_feedback_stim.setAutoDraw(True)
            win.flip()
            trigger_handler.send_trigger()
            core.wait(config["Speed_feedback_duration"])
            # hide feedback
            s_feedback_stim.setAutoDraw(False)
            win.flip()
            data_saver.check_exit()

        # save beh
        data_saver.beh.append(trial)
        trigger_handler.close_trial(trial["acc"])

        logging.data("Trial data: {}\n".format(trial))
        logging.flush()


    # for block_type in block_order:
    #     block_num += 1

    # # ! show new block text and demo feedback
    # demo_feedback[block_type]["pos"].draw()  # draws just for one frame, frame shown inside show_info
    # demo_feedback[block_type]["neg"].draw()
    # demo_feedback[block_type]["neu"].draw()
    # f_expl = config["Feedback_explanations"][block_type]
    # txt = config["New_block_text"].format(block_num=block_num, f_expl=f_expl)
    # show_info(exp, txt, duration=None)

    # # ! choose which trials will have neutral feedback
    # indexes = list(range(config["N_trials_per_block"]))
    # logging.data(f"Indexes: {indexes}")
    # indexes = random.sample(indexes, config["N_neutral_trials_per_block"])
    # logging.data(f"Indexes: {indexes}")
    # logging.flush()

    # trigger_name = get_trigger_name(TriggerTypes.BLOCK_START, block_num, block_type)
    # trigger_handler.prepare_trigger(trigger_name)
    # trigger_handler.send_trigger()

    # # * add some wait between BLOCK_START trigger and first fixation trigger
    # win.flip()
    # core.wait(0.5)

    # for trial_num in range(config["N_trials_per_block"]):
    #     run_trial(
    #         speed_feedback=config["Speed_feedback"],
    #         neutral_feedback=trial_num in indexes,
    #     )

