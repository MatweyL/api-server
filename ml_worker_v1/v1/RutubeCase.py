from transformers import pipeline, AutoTokenizer, EncoderDecoderModel

import torch

import sentencepiece

from diffusers import DiffusionPipeline, StableDiffusionPipeline

import pandas as pd

# summarizing model
tokenizer = AutoTokenizer.from_pretrained("IlyaGusev/rubert_telegram_headlines", do_lower_case=False,
                                          do_basic_tokenize=False, strip_accents=False)
model = EncoderDecoderModel.from_pretrained("IlyaGusev/rubert_telegram_headlines")

# translating model
tokenizer_tr = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ru-en")
tr_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en", tokenizer=tokenizer_tr,
                   device=torch.device('cuda'))

# generating model #1
# img_gen_1 = StableDiffusionPipeline.from_pretrained("alibaba-pai/pai-diffusion-general-large-zh")
# img_gen_1 = img_gen_1.to('cuda')

# generating model #2
img_gen_2 = DiffusionPipeline.from_pretrained("CompVis/ldm-text2im-large-256")
img_gen_2 = img_gen_2.to('cuda')

# generating model #3 ANIME STYLE
img_gen_3 = DiffusionPipeline.from_pretrained("animelover/novelai-diffusion", custom_pipeline="lpw_stable_diffusion",
                                              torch_dtype=torch.float16,
                                              use_auth_token="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")
img_gen_3.safety_checker = None  # we don't need safety checker. you can add not safe words to negative prompt instead.
img_gen_3 = img_gen_3.to("cuda")


def generate_video_preview(video_text: str, author_comments: str,
                           tags: str):  # -> List[BytesIO])  # Список сгенерированных превью-картинок

    # summary video-text
    if video_text is not None:

        if len(video_text) > 35:
            article_text = video_text

            input_ids = tokenizer(
                [article_text],
                add_special_tokens=True,
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = model.generate(
                input_ids=input_ids,
                max_length=100,
                no_repeat_ngram_size=3,
                num_beams=10,
                top_p=0.95
            )[0]

            headline = tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True,
                                        device=torch.device('cuda'))
            # translate rus-eng
            tr_headline = tr_pipe(headline)

        elif len(video_text) <= 35:
            tr_headline = tr_pipe(video_text)
    elif video_text is None:
        tr_headline = tr_pipe('картинка')

    # summary author_comments
    if author_comments is not None:

        if len(author_comments) > 35:
            article_text = author_comments

            input_ids = tokenizer(
                [article_text],
                add_special_tokens=True,
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = model.generate(
                input_ids=input_ids,
                max_length=100,
                no_repeat_ngram_size=3,
                num_beams=10,
                top_p=0.95
            )[0]

            author = tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True,
                                      device=torch.device('cuda'))
            # translate rus-eng
            tr_author = tr_pipe(author)

        elif len(author_comments) <= 35:
            tr_author = tr_pipe(author_comments)
    elif author_comments is None:
        tr_author = tr_pipe('картинка')

    if tags is not None:
        tags = tr_pipe(tags)
    elif tags is None:
        tags = tr_pipe('картинка')

    # make a prompt from summaries and tags
    for x in tr_headline[0].values():
        prompt1 = str(x)
    for x in tr_author[0].values():
        prompt2 = str(x)
    for x in tags[0].values():
        prompt3 = str(x)
    prompt = " ".join([prompt1, prompt2, prompt3])

    # generate 1 image
    image_2 = img_gen_2([prompt[0]], num_inference_steps=50, eta=0.3, guidance_scale=6).images
    for idx, image in enumerate(image_2):
        image.save("video_cover.png")

    # generate 3 image ANIME STYLE
    neg_prompt = "lowres, bad anatomy, error body, error hair, error arm, error hands, bad hands, error fingers, bad  fingers, missing fingers, error legs, bad legs, multiple legs, missing legs, error lighting, error shadow, error reflection, text, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    # we don't need autocast here, because autocast will make speed slow down.
    image = img_gen_3.text2img(prompt, negative_prompt=neg_prompt, width=512, height=768, max_embeddings_multiples=5,
                               guidance_scale=12).images[0]
    image.save("video_anime_style.png")

    # convert from *.png to BytesIO:
    with open('video_cover.png', 'rb') as f:
        video_byte = f.read()

    with open('video_anime_style.png', 'rb') as f:
        video_anime_byte = f.read()

    return video_byte, video_anime_byte


def generate_avatar_photo(avatar_description: str):  # -> List[BytesIO]:  # Список сгенерированных аватарок
    # summary avatar_description
    if avatar_description is not None:

        if len(avatar_description) > 35:
            article_text = avatar_description

            input_ids = tokenizer(
                [article_text],
                add_special_tokens=True,
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = model.generate(
                input_ids=input_ids,
                max_length=100,
                no_repeat_ngram_size=3,
                num_beams=10,
                top_p=0.95
            )[0]

            avatar = tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True,
                                      device=torch.device('cuda'))
            # translate rus-eng
            tr_avatar = tr_pipe(avatar)

        elif len(avatar_description) <= 35:
            tr_avatar = tr_pipe(avatar_description)
    elif avatar_description is None:
        tr_avatar = tr_pipe('картинка')

    prompt = [str(x) for x in tr_avatar[0].values()]

    # generate 1 image
    image_2 = img_gen_2([prompt[0]], num_inference_steps=50, eta=0.3, guidance_scale=6).images
    for idx, image in enumerate(image_2):
        image.save("avatar.png")

    # generate 3 image ANIME STYLE
    neg_prompt = "lowres, bad anatomy, error body, error hair, error arm, error hands, bad hands, error fingers, bad  fingers, missing fingers, error legs, bad legs, multiple legs, missing legs, error lighting, error shadow, error reflection, text, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    # we don't need autocast here, because autocast will make speed slow down.
    image = img_gen_3.text2img(prompt, negative_prompt=neg_prompt, width=512, height=768, max_embeddings_multiples=5,
                               guidance_scale=12).images[0]
    image.save("avatar_anime_style.png")

    # convert from *.png to BytesIO:
    with open('avatar.png', 'rb') as f:
        avatar_byte = f.read()

    with open('avatar_anime_style.png', 'rb') as f:
        avatar_anime_byte = f.read()

    return avatar_byte, avatar_anime_byte


def generate_channel_background_image(
        channel_background_image_description: str):  # -> List[BytesIO]:  # Список сгенерированных задних фонов для канала
    # summary generate_channel_background_image
    if channel_background_image_description is not None:

        if len(channel_background_image_description) > 35:
            article_text = channel_background_image_description

            input_ids = tokenizer(
                [article_text],
                add_special_tokens=True,
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = model.generate(
                input_ids=input_ids,
                max_length=100,
                no_repeat_ngram_size=3,
                num_beams=10,
                top_p=0.95
            )[0]

            background = tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True,
                                          device=torch.device('cuda'))
            # translate rus-eng
            tr_background = tr_pipe(background)

        elif len(channel_background_image_description) <= 35:
            tr_background = tr_pipe(channel_background_image_description)
    elif channel_background_image_description is None:
        tr_background = tr_pipe('картинка')

    prompt = [str(x) for x in tr_background[0].values()]

    # generate 1 image
    image_2 = img_gen_2([prompt[0]], num_inference_steps=50, eta=0.3, guidance_scale=6).images
    for idx, image in enumerate(image_2):
        image.save("background.png")

    # generate 3 image ANIME STYLE
    neg_prompt = "lowres, bad anatomy, error body, error hair, error arm, error hands, bad hands, error fingers, bad  fingers, missing fingers, error legs, bad legs, multiple legs, missing legs, error lighting, error shadow, error reflection, text, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    # we don't need autocast here, because autocast will make speed slow down.
    image = img_gen_3.text2img(prompt, negative_prompt=neg_prompt, width=512, height=768, max_embeddings_multiples=5,
                               guidance_scale=12).images[0]
    image.save("background_anime_style.png")

    # convert from *.png to BytesIO:
    with open('background.png', 'rb') as f:
        background_byte = f.read()

    with open('background_anime_style.png', 'rb') as f:
        backfground_anime_byte = f.read()

    return background_byte, backfground_anime_byte
