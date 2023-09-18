# -*- coding:utf-8 -*-

# @Time    ：2023/9/15 11:52
# @Author  ：Yanbing Dong
# @FileName: model_utils.py

from functools import partial

import fitz
import torch
from tqdm import tqdm

from nougat import NougatModel
from nougat.dataset.rasterize import rasterize_paper
from nougat.postprocessing import markdown_compatible, close_envs
from nougat.utils.dataset import ImageDataset

BATCHSIZE = 4


def generate(uploaded_file: 'st.runtime.uploaded_file_manager.UploadedFile') -> str:
    is_pdf = uploaded_file.name.lower().endswith('.pdf')
    if is_pdf:
        pdf = fitz.open("pdf", uploaded_file.read())
        _pages = list(range(len(pdf)))
        images = rasterize_paper(pdf)
    else:
        images = [uploaded_file]

    predictions = [""] * len(images)
    pages = list(range(len(images)))
    compute_pages = pages.copy()

    dataset = ImageDataset(
        images,
        partial(model.encoder.prepare_input, random_padding=False),
    )

    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=BATCHSIZE,
        pin_memory=True,
        shuffle=False,
    )

    for idx, sample in tqdm(enumerate(dataloader), total=len(dataloader)):
        if sample is None:
            continue
        model_output = model.inference(image_tensors=sample)
        for j, output in enumerate(model_output["predictions"]):
            if model_output["repeats"][j] is not None:
                if model_output["repeats"][j] > 0:
                    disclaimer = "\n\n+++ ==WARNING: Truncated because of repetitions==\n%s\n+++\n\n"
                else:
                    disclaimer = (
                        "\n\n+++ ==ERROR: No output for this page==\n%s\n+++\n\n"
                    )
                rest = close_envs(model_output["repetitions"][j]).strip()
                if len(rest) > 0:
                    disclaimer = disclaimer % rest
                else:
                    disclaimer = ""
            else:
                disclaimer = ""

            predictions[pages.index(compute_pages[idx * BATCHSIZE + j])] = (
                    markdown_compatible(output) + disclaimer
            )

    final = "".join(predictions).strip()
    return final


checkpoint = '/data1/dongyanbing/git/nougat/checkpoints/base'
model = NougatModel.from_pretrained(checkpoint).to(torch.bfloat16)
if torch.cuda.is_available():
    model.to("cuda")
model.eval()
