import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip

# Function to extract audio from a video
def extract_audio_from_video(video_path, audio_output_path):
    video = me.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path)

# Function to transcribe audio to text using Google Speech Recognition
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

# Function to add basic punctuation to the transcribed text
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

# Function to translate text into a target language using Google Translate
def translate_text(text, target_language="en"):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

# Function to convert text to speech using Google Text-to-Speech (gTTS)
def text_to_speech_gTTS(text, output_audio_file, lang='en'):
    tts = gTTS(text=text, lang=lang)
    output_audio_file = output_audio_file.replace(".wav", ".mp3")  # Save as mp3
    tts.save(output_audio_file)
    os.system(f"mpg321 {output_audio_file}")

# Function to merge audio with a video
def merge_audio_with_video(video_path, audio_path, output_video_path):
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
        st.error(f"An error occurred: {e}")
        raise

# Streamlit app interface
st.title("Audio Converter")

# Hide the "View GitHub" and "View Profile" options
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Upload video file
video_file = st.file_uploader("Upload a Video", type=["mp4", "mov", "avi"])
transcribed_text = ""  # Initialize transcribed_text as an empty string

if video_file is not None:
    video_path = video_file.name
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())
    st.success(f"Uploaded {video_file.name}")

    # Extract audio
    audio_output_path = "extracted_audio.wav"
    extract_audio_from_video(video_path, audio_output_path)
    st.audio(audio_output_path)

    # Transcribe audio
    if st.button("Transcribe Audio"):
        transcribed_text = transcribe_audio(audio_output_path)
        if transcribed_text:
            st.text_area("Transcribed Text", transcribed_text)
        else:
            st.error("Failed to transcribe audio.")

    # Translate text (ensure transcribed_text is not empty)
    target_language = st.selectbox("Select Target Language", ["en", "es", "fr", "de", "hi", "zh-cn"])
    if st.button("Translate Text"):
        if transcribed_text:
            translated_text = translate_text(transcribed_text, target_language)
            st.text_area("Translated Text", translated_text)
        else:
            st.error("No transcribed text available for translation. Please transcribe the audio first.")

    # Text to speech
    output_audio_file = "translated_audio.mp3"
    if st.button("Convert Translated Text to Speech"):
        if translated_text:
            text_to_speech_gTTS(translated_text, output_audio_file, target_language)
            st.audio(output_audio_file)
        else:
            st.error("No translated text available for text-to-speech conversion.")

    # Merge audio with video
    output_video_path = "final_video.mp4"
    if st.button("Merge Audio with Video"):
        merge_audio_with_video(video_path, output_audio_file, output_video_path)
        st.video(output_video_path)
