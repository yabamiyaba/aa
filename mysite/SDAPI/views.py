import pwd
from django.shortcuts import render
from curses.ascii import HT

# Create your views here.
from django.http import HttpResponse

"""
test. check if can receive seed etc. by URL.
"""

def test_show(request, seed_val, guidance_scale, height, width, prompt_txt, steps):
    output = f"Seed: {seed_val}, GS: {guidance_scale}, height: {height}, width: {width}, steps: {steps}, prompt: {prompt_txt}"
    return HttpResponse(output)

"""
test. check if can show img on browser
"""
#from django.template import loader
from django.shortcuts import render
def test_imshow(request):
    context = {
        "imgname" : "test.png"
    }
    return render(request, "SDAPI/index.html", context)

"""
use stable-sdk. reference: https://github.com/Stability-AI/stability-sdk/blob/main/nbs/demo_colab.ipynb
need to be installed stability_sdk
"""

import getpass, os
import io
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

#画像を保存
import sys
sys.path.append("../")
from mysite import settings
#画像をhtmlに反映
#リダイレクト

#render して HeepRequest で返す



def SDAPI_request(request, seed_val, guidance_scale, height, width, steps, prompt_txt):
    os.environ["STABILITY_HOST"] = 'grpc.stability.ai:443'
    os.environ["STABILITY_KEY"] = "sk-grnCOk3zjrmcyHnk7dggwLMz8SWHZbexCzb1KcFLekfTFoLq"
    stability_api = client.StabilityInference(
        key=os.environ["STABILITY_KEY"],
        verbose=True,
    )
    # the object returned is a python generator
    answers = stability_api.generate(
        prompt=prompt_txt,
        seed=seed_val, # if provided, specifying a random seed makes results deterministic
        steps=steps, # defaults to 50 if not specified
    )

    # iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                #画像を保存
                if len(prompt_txt) > 252:
                    imgname = prompt_txt[:251] + ".png"
                else:
                    imgname = f"{prompt_txt}.png"
                img.save(str(settings.MEDIA_ROOT) + "/" + imgname)
                #画像を保存したディレクトリを参照してHTMLに反映
                
                ##反映したものを redirect で返す
                #render して HttpResponse を試す
                context = {
                    "imgname" : imgname
                    }
                return render(request, "SDAPI/index.html", context)
                #return HttpResponse(context["imgname"])