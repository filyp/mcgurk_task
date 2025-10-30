import random
import time
from copy import deepcopy
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
    
    assert config["Pre_video_duration"] > 0.4, "Loading videos may interfere with timing if ITI is so short"

    # EEG triggers
    trigger_handler = TriggerHandler(config["Send_EEG_trigg"], data_saver=data_saver)
    exp.trigger_handler = trigger_handler

    all_video_names = [
        str(f.relative_to(stimuli_dir)) for f in stimuli_dir.glob("**/*.mp4")
    ]

    # ! greeting texts
    for greeting_text in config["Greeting_texts"]:
        show_info(exp, greeting_text, duration=None)

    # ! create movie order
    # movie_order = deepcopy(all_video_names)
    # movie_order = movie_order * config["Repeats"]
    # movie_order = []
    movie_order = {}
    for type_, repeats in config["Repeats"].items():
        type_movies = [n for n in all_video_names if n.startswith(type_)]
        random.shuffle(type_movies)
        movie_order[type_] = type_movies * repeats

    types_order = list(movie_order.keys())
    random.shuffle(types_order)
    print(types_order)

    for i, type_ in enumerate(types_order):
        one_type_movies = movie_order[type_]

        # ! block break, wait for space press
        if i != 0:
            show_info(exp, config["Break_text"], duration=None)

        for movie_name in one_type_movies:
            # ! wait some duration while loading a movie
            win.flip()  # to make the text or video disappears
            clock.reset()
            # * load movie
            movie = visual.MovieStim(
                win,
                stimuli_dir / movie_name,
                size=(config["Video_height"] / 9 * 16, config["Video_height"]),
                units="height",  # or 'deg', 'norm', etc.
                volume=1.0,  # Audio volume (0.0 to 1.0)
                loop=False,  # set to True if you want the video to loop
                autoStart=False,  # automatically start playing when drawn
            )
            to_wait = config["Pre_video_duration"] - clock.getTime()
            if to_wait > 0:
                core.wait(to_wait)
            else:
                logging.warning(f"Movie loaded in {clock.getTime()} seconds")

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

            movie.stop()
            del movie
            
            data_saver.check_exit()

    show_info(exp, config["End_text"], duration=None)
