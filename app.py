import os
import streamlit as st
import moviepy.editor as me
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip

# Hide Streamlit menu and footer
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob { display: none; }
    .css-1v0mbdj { display: none; }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

def extract_audio_from_video(video_path, audio_output_path):
    try:
        video = me.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_output_path)
        return True
    except Exception as e:
        st.error(f"Audio extraction failed: {str(e)}")
        return False

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return add_punctuation(text)
    except sr.UnknownValueError:
        st.error("Could not understand the audio")
        return ""
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return ""

def add_punctuation(text):
    replacements = {
        " and": ", and", " but": ", but", " so": ", so",
        " because": ", because", " although": ", although",
        " while": ", while", " or": ", or", " yet": ", yet",
        " nevertheless": ", nevertheless", " moreover": ", moreover",
        " then": ". Then", " therefore": ". Therefore",
        " however": ". However", " thus": ". Thus",
        " otherwise": ". Otherwise", " furthermore": ". Furthermore"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text + "." if not text.endswith(".") else text

def translate_text(text, target_language="en"):
    try:
        if not text:
            return ""
        return GoogleTranslator(source='auto', target=target_language).translate(text)
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        return text  # Return original text as fallback

def text_to_speech_gTTS(text, output_audio_file, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_audio_file)
        return True
    except Exception as e:
        st.error(f"Speech synthesis failed: {str(e)}")
        return False

def merge_audio_with_video(video_path, audio_path, output_video_path):
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        else:
            audio = audio.set_duration(video.duration)

        final_video = video.set_audio(audio)
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
        return True
    except Exception as e:
        st.error(f"Video merging failed: {str(e)}")
        return False

# Streamlit UI
st.title("Audio Convertor App ")

uploaded_file = st.file_uploader("Upload video file", type=["mp4", "mov", "avi"])
target_lang = st.selectbox("Target Language", ["en", "es", "fr", "de", "hi", "ja"], index=0)

if st.button("Process Video") and uploaded_file:
    # File paths
    temp_video = "temp_video.mp4"
    extracted_audio = "extracted_audio.wav"
    translated_audio = "translated_audio.mp3"
    final_video = "final_output.mp4"

    try:
        # Save uploaded video
        with open(temp_video, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Step 1: Extract audio
        if not extract_audio_from_video(temp_video, extracted_audio):
            raise Exception("Audio extraction failed")

        # Step 2: Transcribe audio
        original_text = transcribe_audio(extracted_audio)
        if not original_text:
            raise Exception("No text transcribed")

        # Step 3: Translate text
        translated_text = translate_text(original_text, target_lang)
        if not translated_text:
            raise Exception("Translation failed")

        # Step 4: Generate translated audio
        if not text_to_speech_gTTS(translated_text, translated_audio, lang=target_lang):
            raise Exception("Audio generation failed")

        # Step 5: Merge audio with video
        if not merge_audio_with_video(temp_video, translated_audio, final_video):
            raise Exception("Video merging failed")

        # Display results
        st.success("Processing complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.write(original_text)
        
        with col2:
            st.subheader("Translated Text")
            st.write(translated_text)

        # Download and preview
        st.video(final_video)
        with open(final_video, "rb") as f:
            st.download_button("Download Translated Video", f, file_name=final_video)

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")

    finally:
        # Cleanup temporary files
        for path in [temp_video, extracted_audio, translated_audio]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

st.markdown("---")
