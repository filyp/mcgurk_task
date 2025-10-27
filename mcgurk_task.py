from copy import deepcopy
import random
from pathlib import Path

from psychopy import core, event, logging, visual

from psychopy_experiment_helpers.show_info import show_info
from psychopy_experiment_helpers.triggers_common_usb_simple import TriggerHandler

stimuli_dir = Path(__file__).parent / "categorized_videos"


# def deg_to_height(deg, config):
#     size_in_cm = (deg / 360) * (2 * 3.1415 * config["Screen_distance"])
#     return size_in_cm / config["Screen_height"]


def mcgurk_task(exp, config, data_saver):
    # unpack necessary objects for easier access
    win = exp.win
    clock = exp.clock

    # EEG triggers
    trigger_handler = TriggerHandler(config["Send_EEG_trigg"], data_saver=data_saver)
    exp.trigger_handler = trigger_handler

    all_video_names = [
        str(f.relative_to(stimuli_dir)) for f in stimuli_dir.glob("**/*.mp4")
    ]

    movies = {
        video_name: visual.MovieStim(
            win,
            stimuli_dir / video_name,
            # size=(None, deg_to_height(config["Video_height_deg"], config)),
            size=(None, config["Video_height"]),
            units="height",  # or 'deg', 'norm', etc.
            volume=1.0,  # Audio volume (0.0 to 1.0)
            loop=False,  # set to True if you want the video to loop
            autoStart=False,  # automatically start playing when drawn
        )
        for video_name in all_video_names
    }

    # ! greeting texts
    for greeting_text in config["Greeting_texts"]:
        show_info(exp, greeting_text, duration=None)

    # ! create movie order
    # movie_order = deepcopy(all_video_names)
    # movie_order = movie_order * config["Repeats"]
    movie_order = []
    for type_, repeats in config["Repeats"].items():
        type_movies = [n for n in all_video_names if n.startswith(type_)]
        movie_order.extend(type_movies * repeats)
    random.shuffle(movie_order)
    print(len(movie_order))
    print(movie_order)

    for i, movie_name in enumerate(movie_order):
        # ! if block break, wait for space press
        if (i + 1) % config["Break_every_n_trials"] == 0:
            show_info(exp, config["Break_text"], duration=None)

        # ! wait some duration
        win.flip()  # to make the text or video disappear
        core.wait(config["Pre_video_duration"])

        # ! draw movie
        movie = movies[movie_name]
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
        
        data_saver.check_exit()

    show_info(exp, config["End_text"], duration=None)
