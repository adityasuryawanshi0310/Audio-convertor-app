import streamlit as st
from gtts import gTTS
import os
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

# Function to merge audio and video
def merge_audio_with_video(video_path, audio_path, output_video_path):
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        st.write(f"Video duration: {video.duration}")
        st.write(f"Audio duration: {audio.duration}")

        if audio.duration == 0:
            st.error("The audio file is empty.")
            return

        # Trimming the audio to match the video duration
        audio = audio.subclip(0, video.duration)
        final_video = video.set_audio(audio)
        
        # Specify FPS for audio and save the output
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", audio_fps=44100)
        st.success("Video with merged audio successfully saved!")
    except Exception as e:
        st.error(f"Error merging audio with video: {e}")

# Function to generate speech
def text_to_speech(text, language, voice, rate=115):
    try:
        # Use gTTS for text-to-speech conversion
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save the audio output
        audio_output_path = "output_audio.mp3"
        tts.save(audio_output_path)

        # Adjust speech rate using pydub
        sound = AudioSegment.from_file(audio_output_path)
        altered_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * (rate / 100))})
        altered_sound = altered_sound.set_frame_rate(sound.frame_rate)
        altered_sound.export(audio_output_path, format="mp3")

        return audio_output_path
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

# Streamlit app for audio-video conversion
def main():
    st.title("Audio-Video Converter")

    # Step 1: Upload video
    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    if video_file:
        video_path = os.path.join("uploaded_video.mp4")
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        st.video(video_path)

    # Step 2: Enter text for conversion
    text = st.text_area("Enter the text you want to convert to speech")
    language = st.selectbox("Choose Language", ["en", "hi"])
    voice = st.selectbox("Choose Voice Type", ["Male", "Female"])
    rate = st.slider("Speech Rate", min_value=50, max_value=200, value=115)

    if st.button("Convert Text to Speech and Merge with Video"):
        if not video_file:
            st.error("Please upload a video file first!")
            return

        if not text:
            st.error("Please enter the text to convert!")
            return

        # Convert text to speech
        st.info("Generating speech...")
        audio_output_path = text_to_speech(text, language, voice, rate)

        if audio_output_path:
            st.success("Speech generated successfully!")

            # Step 3: Merge audio with video
            final_video_path = "final_output_video.mp4"
            merge_audio_with_video(video_path, audio_output_path, final_video_path)
            st.success("Final video with audio generated!")
            st.video(final_video_path)

if __name__ == "__main__":
    main()
