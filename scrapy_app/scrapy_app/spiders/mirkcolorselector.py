from PIL import Image, ImageOps, ImageColor
import requests
from io import BytesIO

def sampler_function(im, crop):
    # Load the image
    response = requests.get(im)

    # Open image with PIL
    img = Image.open(BytesIO(response.content))

    # Calc pixels to be cropped
    sz = img.width * crop

    # Crop pixels from top, bottom and sides
    img = ImageOps.crop(img, sz)

    # Get singe most predominant color from image
    result = img.convert('P', palette=Image.ADAPTIVE, colors=1)
    result.putalpha(0)
    return result.getcolors(150*150)
