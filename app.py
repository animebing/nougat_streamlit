# -*- coding:utf-8 -*-

# @Time    ：2023/9/15 11:50
# @Author  ：Yanbing Dong
# @FileName: app.py

import threading
import uuid

import streamlit as st
import streamlit.components.v1 as components

from utils import task_queue, results, html_template

title = 'NOUGAT'
st.set_page_config(page_title=title)
st.title(title)
with st.expander("About the demo", expanded=True):
    st.write(
        """
        - Input image or pdf file, then generate text
        """
    )

_, c_0, _ = st.columns([0.1, 6, 0.1])
with c_0:
    input_file = st.file_uploader(
        'Choose a file',
        type=['png', 'jpg', 'jpeg', 'webp', 'pdf'],
        key='input_file',
    )
    if input_file is not None and st.button('Generate'):
        with st.spinner('Wait for processing...'):
            task_id = str(uuid.uuid4())
            event = threading.Event()
            task_queue.put([task_id, event, input_file])
            event.wait()
            mmd = results[task_id]
        st.markdown("""---""")
        html = html_template.replace('{placeholder}', mmd)
        components.html(html, height=600, scrolling=True)
