from psychopy import core, event, logging, visual


def show_info(
    exp,
    custom_text,
    alignText="center",
    pos=(0, 0),
    duration=None,
):
    screen_width = exp.screen_res["width"]

    hello_msg = custom_text
    hello_msg = visual.TextStim(
        win=exp.win,
        antialias=True,
        font=exp.config["Text_font"],
        text=hello_msg,
        height=exp.config["Text_size"],
        wrapWidth=screen_width,
        color=exp.config["Text_color"],
        alignText=alignText,
        pos=pos,
    )
    hello_msg.draw()
    exp.win.flip()
    if duration is None:
        # wait for key press or mouse click
        event.clearEvents()
        exp.mouse.clickReset()
        while True:
            # _, press_times = exp.mouse.getPressed(getTime=True)
            keys = event.getKeys(keyList=["f7", "return", "space"])

            if "f7" in keys:
                exp.data_saver.save_beh()
                exp.data_saver.save_triggers()
                logging.critical("Experiment finished by user! {} pressed".format(keys))
                exit(1)
            if "space" in keys:
                break

            core.wait(0.030)

    else:
        # wait for duration
        core.wait(duration)
