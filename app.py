import streamlit as st
from utils.auth import check_credentials, register_user, load_users, save_users
from utils.ai_story import split_into_scenes
from utils.tts import synthesize_narration
from utils.image_gen import make_scene_images
from utils.video_gen import stitch_video
import os

st.set_page_config(page_title='AI StoryWeaver', layout='centered')

if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'username' not in st.session_state:
    st.session_state.username = None

def show_login():
    st.session_state.page = 'login'

def show_signup():
    st.session_state.page = 'signup'

def show_landing():
    st.session_state.page = 'landing'

def show_create():
    st.session_state.page = 'create'

def show_output():
    st.session_state.page = 'output'

# Navigation
if st.session_state.page == 'login':
    st.markdown('<h1 style="text-align:center">🔐 AI StoryWeaver</h1>', unsafe_allow_html=True)
    st.write('Login to continue (demo uses local JSON users).')
    u = st.text_input('Username')
    p = st.text_input('Password', type='password')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Login'):
            if check_credentials(u, p):
                st.success('Login successful')
                st.session_state.username = u
                show_landing()
            else:
                st.error('Invalid credentials')
    with col2:
        if st.button('Sign up'):
            show_signup()

elif st.session_state.page == 'signup':
    st.markdown('<h1 style="text-align:center">📝 Sign Up - AI StoryWeaver</h1>', unsafe_allow_html=True)
    su = st.text_input('Choose username')
    sp1 = st.text_input('Password', type='password')
    sp2 = st.text_input('Confirm password', type='password')
    if st.button('Create account'):
        if not su or not sp1:
            st.error('Enter valid username and password')
        elif sp1 != sp2:
            st.error('Passwords do not match')
        else:
            ok, msg = register_user(su, sp1)
            if ok:
                st.success(msg)
                st.session_state.username = su
                show_landing()
            else:
                st.error(msg)
    if st.button('Back to login'):
        show_login()

elif st.session_state.page == 'landing':
    st.markdown(f"<h1 style='text-align:center'>🏠 Welcome, {st.session_state.username}</h1>", unsafe_allow_html=True)
    st.write('Start creating AI video stories or logout.')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Create Story'):
            show_create()
    with col2:
        if st.button('Logout'):
            st.session_state.username = None
            show_login()

elif st.session_state.page == 'create':
    st.markdown('<h1 style="text-align:center">📝 Create Story</h1>', unsafe_allow_html=True)
    title = st.text_input('Story Title', 'The Clever Jackal')
    theme = st.text_input('One-line theme', 'A clever jackal escapes a pit')
    style = st.selectbox('Style', ['Folk Tale','Fantasy','Adventure','Mystery','Myth'])
    num_scenes = st.slider('Number of scenes', 3, 8, 5)
    if st.button('Generate'):
        base = f"{title}. {theme}. A {style.lower()} inspired tale."
        scenes = split_into_scenes(base, target=num_scenes)
        st.session_state.scenes = scenes
        st.success('Scenes created')
        # generate narration
        audio_path, narration_text = synthesize_narration(scenes)
        st.session_state.audio = audio_path
        st.session_state.narration_text = narration_text
        # generate images
        image_paths = make_scene_images(scenes)
        st.session_state.images = image_paths
        # stitch video
        video_path = stitch_video(image_paths, audio_path)
        st.session_state.video = video_path
        st.success('Video created')
        show_output()
    if st.button('Back'):
        show_landing()

elif st.session_state.page == 'output':
    st.markdown('<h1 style="text-align:center">🎬 Your AI Story Video</h1>', unsafe_allow_html=True)
    video = st.session_state.get('video')
    scenes = st.session_state.get('scenes', [])
    narration = st.session_state.get('narration_text', '')
    if not video:
        st.warning('No video generated yet.')
        if st.button('Back'):
            show_create()
    else:
        st.video(video)
        st.download_button('Download MP4', data=open(video,'rb').read(), file_name=os.path.basename(video), mime='video/mp4')
        with st.expander('Scenes & Narration'):
            for i,s in enumerate(scenes,1):
                st.write(f"**Scene {i}:** {s}")
            st.write('---')
            st.write(narration)
        if st.button('Back to Landing'):
            show_landing()
        if st.button('Logout'):
            st.session_state.username = None
            show_login()
