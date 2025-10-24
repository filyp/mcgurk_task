class TriggerTypes:
    FIXATION = "FIXATION"
    STAR_START = "STAR_START"
    STAR_END = "STAR_END"
    REACTION = "REACTION"
    FEEDBACK_POS = "FEEDBACK_POS"
    FEEDBACK_NEG = "FEEDBACK_NEG"
    FEEDBACK_NEU = "FEEDBACK_NEU"
    TOO_SLOW = "TOO_SLOW"
    TOO_FAST = "TOO_FAST"
    BLOCK_START = "BLOCK_START"


def get_trigger_name(
    trigger_type,
    block_num,
    block_type,
):
    # response will be added later, on close_trial
    # return "*".join([trigger_type, block_type[:3], ""])
    return "*".join([trigger_type, str(block_num), block_type, ""])
