# coding:utf-8
# pyaudioインストール参考サイト：https://qiita.com/musaprg/items/34c4c1e0e9eb8e8cc5a1
import pyaudio
import wave
import time
import threading
import Speech_to_Text


# 何秒ごとにレコーディングさせるか

def timekeep():
    """
    何秒ごとにレコーディングさせるか

    """
    time.sleep(2)


def recoding():
    """
    レコーディング
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16  # int16型
    CHANNELS = 2             # ステレオ
    RATE = 44100             # 441.kHz
    RECORD_SECONDS = 10       # 10秒録音
    WAVE_OUTPUT_FILENAME = "Speech.wav"  # Speech.wavに取得した音声を保存

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    # レコーディング開始
    print("* recording")

    frames = [stream.read(CHUNK)
              for i in range(int(RATE / CHUNK * RECORD_SECONDS))]
    # レコーディング終了
    print("* done recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
