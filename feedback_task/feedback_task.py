import random
from pathlib import Path

from psychopy import core, event, logging, visual

from feedback_task.triggers import TriggerTypes, get_trigger_name
from psychopy_experiment_helpers.show_info import show_info

message_dir = Path(__file__).parent.parent / "messages"
stimuli_dir = Path(__file__).parent.parent / "stimuli"

color_dict = dict(
    red="#FF0000",
    green="#00FF00",
    blue="#0000FF",
    yellow="#FFFF00",
)


def deg_to_height(deg, config):
    size_in_cm = (deg / 360) * (2 * 3.1415 * config["Screen_distance"])
    return size_in_cm / config["Screen_height"]


def load_img(name, size, win, config):
    return visual.ImageStim(
        win=win,
        image=stimuli_dir / name,
        size=(None, deg_to_height(size, config)),
        interpolate=True,
    )


def load_text(text, win, config):
    return visual.TextStim(
        win=win,
        text=text,
        color="black",
        # height=config["Text_feedback_font_size"],
        height=deg_to_height(config["Speed_feedback_size"], config),
        font="Arial",
    )
    

def load_feedback_stimuli(win, config):
    _v = config["Experiment_version"]
    return dict(
        number=dict(
            # pos=load_text("+1", win, config),
            # neg=load_text("-1", win, config),
            # neu=load_text("J", win, config),
            pos=load_img("points_pos_Plus1.png", config["Feedback_size"], win, config),
            neg=load_img("points_neg_Minus1.png", config["Feedback_size"], win, config),
            neu=load_img("points_neut_J.png", config["Feedback_size"], win, config),
        ),
        facesimple=dict(
            # pos=load_img("smiley_face.png", config["Feedback_size"], win, config),
            # neg=load_img("sad_face.png", config["Feedback_size"], win, config),
            # neu=load_img("empty_face.png", config["Feedback_size"], win, config),
            pos=load_img("simple_pos_smiley_face.png", config["Feedback_size"], win, config),
            neg=load_img("simple_neg_sad_face.png", config["Feedback_size"], win, config),
            neu=load_img("simple_neut_empty_face.png", config["Feedback_size"], win, config),
        ),
        facecomplex=dict(
            pos=load_img(f"{_v}/pos.png", config["Face_feedback_size"], win, config),
            neg=load_img(f"{_v}/neg.png", config["Face_feedback_size"], win, config),
            neu=load_img(f"{_v}/neu.png", config["Face_feedback_size"], win, config),
        ),
        symbol=dict(
            # pos=load_img("tick.png", config["Feedback_size"], win, config),
            # neg=load_img("cross.png", config["Feedback_size"], win, config),
            # neu=load_img("equal.png", config["Feedback_size"], win, config),
            pos=load_img("symbol_pos_tick.png", config["Feedback_size"], win, config),
            neg=load_img("symbol_neg_cross.png", config["Feedback_size"], win, config),
            neu=load_img("symbol_neut_equal.png", config["Feedback_size"], win, config),
        ),
        color=dict(
            pos=load_img("green_square.png", config["Feedback_size"], win, config),
            neg=load_img("red_square.png", config["Feedback_size"], win, config),
            neu=load_img("blue_square.png", config["Feedback_size"], win, config),
        ),
        text=dict(
            # pos=load_text("dobrze", win, config),
            # neg=load_text("błędnie", win, config),
            # neu=load_text("żyrafa", win, config),
            pos=load_img("text_pos_dobrze.png", config["Text_feedback_size"], win, config),
            neg=load_img("text_neg_blednie.png", config["Text_feedback_size"], win, config),
            neu=load_img("text_neut_probnie.png", config["Text_feedback_size"], win, config),
        ),
        training=dict(
            pos=load_img("thumbs_up.png", config["Feedback_size"], win, config),
            neg=load_img("thumbs_down.png", config["Feedback_size"], win, config),
            neu=None,
        ),
    )


def feedback_task(exp, config, data_saver):
    # unpack necessary objects for easier access
    win = exp.win
    clock = exp.clock

    # EEG triggers
    if config["Trigger_type"] == "usb":
        from psychopy_experiment_helpers.triggers_common_usb import (
            TriggerHandler,
            create_eeg_port,
        )
    elif config["Trigger_type"] == "parport":
        from psychopy_experiment_helpers.triggers_common_parport import (
            TriggerHandler,
            create_eeg_port,
        )
    else:
        raise ValueError("Invalid trigger type: {}".format(config["Trigger_type"]))
    port_eeg = create_eeg_port() if config["Send_EEG_trigg"] else None
    trigger_handler = TriggerHandler(port_eeg, data_saver=data_saver)
    exp.trigger_handler = trigger_handler

    # load stimuli
    fixation = load_img("dot.png", config["Fixation_size"], win, config)
    star = load_img("star.png", config["Star_size"], win, config)
    too_slow = load_text("zbyt wolno", win, config)
    too_fast = load_text("zbyt szybko", win, config)
    # load feedback stimuli
    feedback = load_feedback_stimuli(win, config)
    demo_feedback = load_feedback_stimuli(win, config)
    for feedback_type in config["Feedback_types"]:
        demo_feedback[feedback_type]["pos"].pos = (-0.25, -0.25)
        demo_feedback[feedback_type]["neg"].pos = (0, -0.25)
        demo_feedback[feedback_type]["neu"].pos = (0.25, -0.25)

    block_order = config["Feedback_types"]
    random.shuffle(block_order)
    logging.data(f"Block order: {block_order}")

    def run_trial(speed_feedback, neutral_feedback=False):
        nonlocal allowed_error

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
            trigger_name = get_trigger_name(TriggerTypes.REACTION, block_num, block_type)
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

    # ! greeting texts
    for greeting_text in config["Greeting_texts"]:
        show_info(exp, greeting_text, duration=None)

    # ! training block
    block_num = 0  # block 0 is training
    block_type = "training"
    allowed_error = 100  # in milliseconds
    for trial_num in range(config["N_train_trials"]):
        run_trial(speed_feedback=True)

    show_info(exp, config["Post_training_text"], duration=None)

    allowed_error = 100  # reset allowed error
    for _ in range(3):
        for block_type in block_order:
            block_num += 1

            # ! show new block text and demo feedback
            demo_feedback[block_type]["pos"].draw()  # draws just for one frame, frame shown inside show_info
            demo_feedback[block_type]["neg"].draw()
            demo_feedback[block_type]["neu"].draw()
            f_expl = config["Feedback_explanations"][block_type]
            txt = config["New_block_text"].format(block_num=block_num, f_expl=f_expl)
            show_info(exp, txt, duration=None)

            # ! choose which trials will have neutral feedback
            indexes = list(range(config["N_trials_per_block"]))
            logging.data(f"Indexes: {indexes}")
            indexes = random.sample(indexes, config["N_neutral_trials_per_block"])
            logging.data(f"Indexes: {indexes}")
            logging.flush()

            trigger_name = get_trigger_name(TriggerTypes.BLOCK_START, block_num, block_type)
            trigger_handler.prepare_trigger(trigger_name)
            trigger_handler.send_trigger()

            # * add some wait between BLOCK_START trigger and first fixation trigger
            win.flip()
            core.wait(0.5)

            for trial_num in range(config["N_trials_per_block"]):
                run_trial(
                    speed_feedback=config["Speed_feedback"],
                    neutral_feedback=trial_num in indexes,
                )
    
    show_info(exp, config["End_text"], duration=None)
