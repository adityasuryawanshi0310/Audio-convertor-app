import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip

# Extract audio from video
def extract_audio_from_video(video_path, audio_output_path):
    video = me.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path)

# Transcribe audio to text
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
        st.error(f"Google Speech Recognition service error: {e}")
        return ""

# Add punctuation to the transcribed text
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

# Translate text
def translate_text(text, target_language="en"):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        st.error(f"Translation service error: {e}")
        return text

# Convert text to speech using gTTS
def text_to_speech_gTTS(text, output_audio_file, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_audio_file)
    os.system(f"mpg321 {output_audio_file}")

# Merge translated audio with video
def merge_audio_with_video(video_path, audio_path, output_video_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    audio = audio.subclip(0, video.duration)  # Match audio duration with video
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_video_path)

# Streamlit UI
st.title("Audio Converter")
st.write("Upload a video file, and the app will transcribe, translate, and replace the audio.")

video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

if st.button("Process Video"):
    if video_file is not None:
        # Define file paths
        video_path = os.path.join("temp", "uploaded_video.mp4")
        audio_output_path = os.path.join("temp", "extracted_audio.wav")
        translated_audio_output_path = os.path.join("temp", "translated_audio.wav")
        final_video_path = os.path.join("temp", "final_video.mp4")

        # Create 'temp' directory if not exists
        os.makedirs("temp", exist_ok=True)

        # Save the uploaded video
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())

        # Extract audio from video
        extract_audio_from_video(video_path, audio_output_path)

        # Transcribe audio
        transcription = transcribe_audio(audio_output_path)
        if transcription:
            # Translate the text (add language options if needed)
            translated_text = translate_text(transcription, target_language="en")
            
            # Convert text to speech (gTTS)
            text_to_speech_gTTS(translated_text, translated_audio_output_path)
            
            # Merge new audio with video
            merge_audio_with_video(video_path, translated_audio_output_path, final_video_path)
            
            # Provide download link and video preview
            st.success("Processing complete! You can download the final video below.")
            with open(final_video_path, "rb") as final_video_file:
                st.download_button("Download Final Video", final_video_file, file_name="final_video.mp4")
            st.video(final_video_path)

            # Cleanup temporary files
            if st.button("Cleanup Temporary Files"):
                try:
                    os.remove(video_path)
                    os.remove(audio_output_path)
                    os.remove(translated_audio_output_path)
                    os.remove(final_video_path)
                    st.success("Temporary files have been deleted.")
                except Exception as e:
                    st.error(f"Could not delete temporary files: {e}")
        else:
            st.error("Transcription failed.")
    else:
        st.error("Please upload a video file.")
