import random
from pathlib import Path

from psychopy import core, event, logging, visual

from psychopy_experiment_helpers.show_info import show_info
from psychopy_experiment_helpers.triggers_common_usb_simple import TriggerHandler

stimuli_dir = Path(__file__).parent / "categorized_videos"


# def deg_to_height(deg, config):
#     size_in_cm = (deg / 360) * (2 * 3.1415 * config["Screen_distance"])
#     return size_in_cm / config["Screen_height"]


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

    all_video_names = [str(f.relative_to(stimuli_dir)) for f in stimuli_dir.glob("**/*.mp4")]

    random.shuffle(all_video_names)
    print(all_video_names)

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
        for video_name in all_video_names
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
