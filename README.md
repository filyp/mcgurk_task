# Installation on windows

1. Install PsychoPy - [Installation — PsychoPy](https://www.psychopy.org/download.html)
2. Clone this repository.
3. Run `pip install -r requirements.txt`

You may need to adapt the mechanism of sending triggers to your setup. Edit the file `psychopy_experiment_helpers/triggers_common_usb.py` to do so.

Note that this task requires photos of the experimenter's face. Put them in `stimuli/name/pos.png`, `stimuli/name/neg.png`, and `stimuli/name/neu.png`. Then you select the name on the start of the experiment.

# Running

```bash
python main.py config/full.yaml
```
