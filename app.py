import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Hides the hamburger menu */
    footer {visibility: hidden;}    /* Hides 'Made with Streamlit' */
    header {visibility: hidden;}    /* Hides the header and profile menu */
    
    /* Hide the profile logo */
    .viewerBadge_container__1QSob { 
        display: none; 
    }
    
    /* Hide the entire header which contains the Streamlit icon and View Profile */
    .css-1v0mbdj { 
        display: none; 
    }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)
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

st.write("Upload your video and specify voice index (0 for male, 1 for female).")

video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
voice_index = st.selectbox("Select Voice Index", ["Male", "Female"])
rate = st.slider("Select Speech Rate", 50, 300, 115)  # Default rate is 115

if st.button("Process Video"):
    if video_file is not None:
        video_path = "uploaded_video.mp4"
        audio_output_path = "extracted_audio.wav"
        translated_audio_output_path = "translated_audio.mp3"  # Use mp3 format
        final_video_path = "final_video.mp4"
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())

        # Extract audio from video
        extract_audio_from_video(video_path, audio_output_path)

        # Transcribe audio to text
        transcription = transcribe_audio(audio_output_path)

        if transcription:
            # Translate transcription to English
            translated_text = translate_text(transcription, target_language="en")
            # Generate speech from translated text
            text_to_speech_gTTS(translated_text, translated_audio_output_path, lang='en')
            # Merge audio with video
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
     
