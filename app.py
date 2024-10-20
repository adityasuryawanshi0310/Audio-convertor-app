import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from googletrans import Translator
import pyttsx3 
from gtts import gTTS

from moviepy.editor import AudioFileClip, VideoFileClip

def extract_audio_from_video(video_path, audio_output_path):
    video = me.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        punctuated_text = add_punctuation(text)
        return punctuated_text
    except sr.UnknownValueError:
        print("Could not understand the audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def add_punctuation(text):
    punctuated_text = text.replace(" and", ", and").replace(" but", ", but")
    punctuated_text = punctuated_text.replace(" so", ", so").replace(" because", ", because")
    punctuated_text = punctuated_text.replace(" although", ", although").replace(" while", ", while")
    punctuated_text = punctuated_text.replace(" or", ", or").replace(" yet", ", yet")
    punctuated_text = punctuated_text.replace(" nevertheless", ", nevertheless").replace(" moreover", ", moreover")
    punctuated_text = punctuated_text.replace(" then", ". Then").replace(" therefore", ". Therefore")
    punctuated_text = punctuated_text.replace(" however", ". However").replace(" thus", ". Thus")
    punctuated_text = punctuated_text.replace(" otherwise", ". Otherwise").replace(" furthermore", ". Furthermore")
    if not punctuated_text.endswith("."):
        punctuated_text += "."
    return punctuated_text

def translate_text(text, target_language="en"):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

def text_to_speech_gTTS(text, output_audio_file, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_audio_file)
    os.system(f"mpg321 {output_audio_file}")


def merge_audio_with_video(video_path, audio_path, output_video_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    audio = audio.subclip(0, video.duration)
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_video_path)

st.title("Audio Converter")

st.write("Upload your video and specify voice index (0 for male, 1 for female).")

video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
voice_index = st.selectbox("Select Voice Index", [0, 1])
rate = st.slider("Select Speech Rate", 50, 300, 150)

if st.button("Process Video"):
    if video_file is not None:
        video_path = "uploaded_video.mp4"
        audio_output_path = "extracted_audio.wav"
        translated_audio_output_path = "translated_audio.wav"
        final_video_path = "final_video.mp4"
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())
        extract_audio_from_video(video_path, audio_output_path)
        transcription = transcribe_audio(audio_output_path)
        if transcription:
            translated_text = translate_text(transcription, target_language="en")
            text_to_speech_gTTS(translated_text, translated_audio_output_path, voice_index=voice_index, rate=rate)
            merge_audio_with_video(video_path, translated_audio_output_path, final_video_path)
            st.success("Processing complete! You can download the final video below.")
            with open(final_video_path, "rb") as final_video_file:
                st.download_button("Download Final Video", final_video_file, file_name=final_video_path)
            st.video(final_video_path)
            if st.button("Cleanup Temporary Files"):
                try:
                    os.remove(video_path)
                    os.remove(audio_output_path)
                    os.remove(translated_audio_output_path)
                    os.remove(final_video_path)
                    st.success("Temporary files have been deleted.")
                except PermissionError:
                    st.error("Could not delete temporary files. They may still be in use.")
        else:
            st.error("Transcription failed.")
    else:
        st.error("Please upload a video file.")
