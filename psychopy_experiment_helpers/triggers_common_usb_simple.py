import time

from psychopy import logging


def create_eeg_port():
    try:
        import serial

        port = serial.Serial("/dev/ttyUSB0", baudrate=115200)
        port.write(0x00)
        return port
    except:
        raise Exception("Can't connect to EEG")


def simple_send_trigger(port_eeg, trigger_no):
    port_eeg.write(trigger_no.to_bytes(1, 'big'))
    time.sleep(0.005)
    port_eeg.write(0x00)
    time.sleep(0.005)


class TriggerHandler:
    def __init__(self, send_eeg_trigg, data_saver):
        if send_eeg_trigg:
            self.port_eeg = create_eeg_port()
        else:
            self.port_eeg = None
        self.data_saver = data_saver
        self.trigger_no = 0

    def send_trigger(self, trigger_name):
        # * iterate counter
        self.trigger_no += 1
        if self.trigger_no == 9:
            self.trigger_no = 1

        # * format and save trigger name
        line = f"{self.trigger_no}:{trigger_name}"
        self.data_saver.triggers_list.append(line)

        if self.port_eeg is not None:
            simple_send_trigger(self.port_eeg, self.trigger_no)
