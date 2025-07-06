import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

import argparse
import os

def extract_audio(input_video, output_audio):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vn",
        "-ac", "1",
        "-ar", "44100",
        output_audio
    ]
    subprocess.run(cmd, check=True)

def add_vhs_hiss(input_wav, output_wav):
    sr, data = wavfile.read(input_wav)
    data = data.astype(np.float32) / 32768.0

    if data.ndim > 1:
        data = data.mean(axis=1)

    t = np.arange(len(data)) / sr

    hiss_amp = 0.01
    hiss = np.random.normal(0, hiss_amp, size=data.shape).astype(np.float32)
    tremolo = np.interp(np.random.rand(len(data)), [0, 1], [0.5, 1.5]).astype(np.float32)
    hiss *= tremolo

    hum_freq = 50
    hum = 0.003 * np.sin(2 * np.pi * hum_freq * t)

    volume_vib = (np.random.rand(len(data)) - 0.5) * 0.05

    dropouts = np.ones_like(data)
    for _ in range(int(len(data) / sr * 0.5)):
        pos = np.random.randint(0, len(data) - 500)
        length = np.random.randint(100, 500)
        dropouts[pos:pos+length] *= np.random.uniform(0.2, 0.6)

    clicks = np.zeros_like(data)
    num_clicks = int(len(data) / sr * 5)
    click_positions = np.random.choice(len(data), num_clicks, replace=False)
    for pos in click_positions:
        length = np.random.randint(200, 1000)
        click = np.linspace(1, 0, length)
        if pos + length < len(data):
            clicks[pos:pos+length] += click

    wow_freq = 0.2
    flutter_freq = 5.0
    wow = 0.003 * np.sin(2 * np.pi * wow_freq * t)
    flutter = 0.001 * np.sin(2 * np.pi * flutter_freq * t)
    modulated_t = t + wow + flutter
    modulated_data = np.interp(modulated_t, t, data)

    echo = np.zeros_like(modulated_data)
    delay_samples = int(0.03 * sr)
    decay = 0.3
    echo[delay_samples:] = modulated_data[:-delay_samples] * decay

    processed = (modulated_data + echo) * (1 + volume_vib)
    processed = processed * dropouts
    processed += hiss + hum + clicks * 0.1

    processed = np.tanh(processed * 3) / 3
    processed = np.clip(processed, -1, 1)

    output_data = (processed * 32767).astype(np.int16)
    wavfile.write(output_wav, sr, output_data)

def merge_audio_video(input_video, input_audio, output_video):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", input_audio,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, check=True)

def convert_video_format(input_video, output_video, width=640, height=480, fps=29.97):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", f"scale={width}:{height},setsar=1:1",
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-an",
        output_video
    ]
    subprocess.run(cmd, check=True)


def merge_audio_video(input_video, input_audio, output_video):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", input_audio,
        "-c:v", "copy",
        "-c:a", "aac", 
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Применение эффекта VHS к звуку и видео (MP4).")
    parser.add_argument("video_in", help="Входное видео.")
    parser.add_argument("video_out", help="Выходное видео.")
    args = parser.parse_args()

    video_in = args.video_in
    video_out = args.video_out

    extracted_audio = "extracted.wav"
    processed_audio = "vhs_audio.wav"
    video_4_3 = "video_4_3.mp4"

    try:
        extract_audio(video_in, extracted_audio)
        add_vhs_hiss(extracted_audio, processed_audio)
        convert_video_format(video_in, video_4_3, width=640, height=480, fps=29.97)
        merge_audio_video(video_4_3, processed_audio, video_out)
    finally:
        for f in [extracted_audio, processed_audio, video_4_3]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    main()
