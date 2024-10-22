import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip
st.markdown("""
<style>
.stBaseButton-header
{
            visibility: hidden;
}            
</style>            
""",unsafe_allow_html=True)
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
st.error("Could not understand the audio.")
return ""
except sr.RequestError as e:
st.error(f"Could not request results from Google Speech Recognition service; {e}")
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
output_audio_file = output_audio_file.replace(".wav", ".mp3")  # Save as mp3
tts.save(output_audio_file)
os.system(f"mpg321 {output_audio_file}")
def merge_audio_with_video(video_path, audio_path, output_video_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Adjust the audio duration to match the video duration
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    else:
        # If the audio is shorter, add silence to match the video duration
        audio = audio.set_duration(video.duration)
    
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_video_path)
    try:
        # Load video and audio files
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # Ensure the audio duration matches the video duration
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        else:
            # Adjust audio to match video duration
            audio = audio.set_duration(video.duration)

        # Set the audio for the video
        final_video = video.set_audio(audio)
        
        # Write the final video file
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


st.title("Audio Converter") 
