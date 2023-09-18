# -*- coding:utf-8 -*-

# @Time    ：2023/9/15 14:05
# @Author  ：Yanbing Dong
# @FileName: utils.py

import queue
import threading

from model_utils import generate


html_template = """
        <script>
            const text = `{placeholder}`;
            console.log(text);
            let script = document.createElement('script');
            script.src = "https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.0.40/es5/bundle.js";
            document.head.append(script);

            script.onload = function() {
                const isLoaded = window.loadMathJax();
                if (isLoaded) {
                    console.log('Styles loaded!')
                }

                const el = window.document.getElementById('content-text');
                if (el) {
                    const options = {
                        htmlTags: true
                    };
                    const html = window.render(text, options);
                    console
                    el.outerHTML = html;
                }
            };
        </script>
        <div id="content"><div id="content-text"></div></div>
    """


def process(task_queue: queue.Queue, results: 'typing.Mapping[str, str]'):
    while True:
        item = task_queue.get()
        if item is None:
            break

        task_id = item[0]
        event = item[1]
        result = generate(*item[2:])
        results[task_id] = result.replace('\\', '\\\\')
        task_queue.task_done()
        event.set()


results = {}
task_queue = queue.Queue()
t = threading.Thread(target=process, args=(task_queue, results))
t.start()
print(f'thread id: {t.ident}')
