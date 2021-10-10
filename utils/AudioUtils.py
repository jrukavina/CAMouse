from multiprocessing import Process, Event, Value

import simpleaudio as sa

single_click = sa.WaveObject.from_wave_file('audio/click.wav')
double_click = sa.WaveObject.from_wave_file('audio/double_click.wav')
audioDict = {1: single_click,
             2: double_click}


class AudioPlayer:

    def __init__(self, dictionary=audioDict):
        self.dictionary = dictionary
        self.clickEvent = Event()
        self.targetSound = Value('i', 0)
        self.process = Process(name='audio_player', target=self.playFnc, daemon=True, args=())
        self.process.start()

    def playFnc(self):
        try:
            while True:
                self.clickEvent.wait()
                self.clickEvent.clear()
                play_obj = self.dictionary.get(self.targetSound.value).play()
                play_obj.wait_done()
                # winsound.Beep(1000, 50)
        except KeyboardInterrupt:
            return

    def play(self, audioKey: int):
        if audioKey in self.dictionary.keys():
            with self.targetSound.get_lock():
                self.targetSound.value = audioKey
            self.clickEvent.set()

    def terminate(self):
        self.process.join(1)
        if self.process.is_alive():
            self.process.terminate()
