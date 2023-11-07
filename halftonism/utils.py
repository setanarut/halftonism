from PIL import Image
import numpy as np


def _sawtooth(t, width=1):
    """
    Return a periodic sawtooth or triangle waveform.

    width = 1 gives a right-sided sawtooth

    width = 0 gives a left-sided sawtooth

    width = 0.5 gives a symmetric triangle.
    """
    t, w = np.asarray(t), np.asarray(width)
    w = np.asarray(w + (t - t))
    t = np.asarray(t + (w - w))
    if t.dtype.char in ["fFdD"]:
        ytype = t.dtype.char
    else:
        ytype = "d"
    y = np.zeros(t.shape, ytype)
    mask1 = (w > 1) | (w < 0)
    np.place(y, mask1, np.nan)
    tmod = np.mod(t, 2 * np.pi)
    mask2 = (1 - mask1) & (tmod < w * 2 * np.pi)
    tsub = np.extract(mask2, tmod)
    wsub = np.extract(mask2, w)
    np.place(y, mask2, tsub / (np.pi * wsub) - 1)
    mask3 = (1 - mask1) & (1 - mask2)
    tsub = np.extract(mask3, tmod)
    wsub = np.extract(mask3, w)
    np.place(y, mask3, (np.pi * (wsub + 1) - tsub) / (np.pi * (1 - wsub)))
    return y


def _gradient_sawtooth(repeat: int, width=0):
    """width = 0.5 gives a symmetric triangle."""
    t = np.linspace(0, 1, 257)
    t = t[:-1]
    tri = _sawtooth(2 * np.pi * float(repeat) * t, width)
    tri = np.interp(tri, (-1, 1), (0, 255)).astype("uint8")
    return tri.reshape((1, (256)))


def _gradient_sine(repeat: int) -> np.ndarray:
    x = np.linspace(-np.pi, np.pi, 257)
    x = x[:-1]
    sine1D = 128.0 + (127.0 * np.sin(x * float(repeat)))
    return np.uint8(sine1D)


def _most_common_color_RGB(image: np.ndarray):
    """input image ndarray shape should be RGB shape, for example: (512, 512, 3)"""
    a2D = image.reshape(-1, image.shape[-1])

    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(a2D.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


def _most_common_color_RGBA(image_RGBA: np.ndarray):
    """input image ndarray shape should be RGBA shape, for example: (512, 512, 4)"""
    RGB_pixels = image_RGBA.reshape(-1, 4)
    # remove transparent pixels
    just_non_alpha = RGB_pixels[RGB_pixels[:, 3] != 0]
    # delete alpha channel
    if just_non_alpha.shape[0] == 0:
        return False
    just_non_alpha = np.delete(just_non_alpha, 3, axis=1)

    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(just_non_alpha.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


def save_palette_as_image(palette: list[tuple], image_path: str):
    im = Image.new("RGB", (len(palette) + 2, 3), (128, 128, 128))
    for index, color in enumerate(palette):
        im.putpixel((index + 1, 1), color)
    im = im.resize((int(im.width * 32), int(im.height * 32)), Image.NEAREST)
    im.save(image_path)


def make_gradient_frames(
    frame_skipping=1, repeat=16, waveform="sawtooth"
) -> np.ndarray:
    grad = gradient(repeat, waveform)
    frames_num = int(256 / repeat)
    gradient_frames = grad
    for x in range(frame_skipping, frames_num, frame_skipping):
        gradient_frames = np.vstack([gradient_frames, np.roll(grad, x)])
    return gradient_frames


def gradient_vstack(gradient: np.ndarray, heigth: int):
    stack = gradient
    for i in range(heigth - 1):
        stack = np.vstack((stack, gradient))
    return stack


def apply_gradient_map(img: Image.Image, gradient: np.ndarray) -> Image.Image:
    nd_img = np.array(img.convert("L"))
    nd_img = np.uint8(nd_img)
    return Image.fromarray(np.take(gradient, nd_img))


def gradient(repeat: int = 1, waveform: str = "sawtooth"):
    """returns 1x256 grayscale gradient array

    waveform params:

    "sawtooth", "sine, "triangle"
    """
    match waveform:
        case "sawtooth":
            return _gradient_sawtooth(repeat)
        case "triangle":
            return _gradient_sawtooth(repeat, 0.5)
        case "sine":
            return _gradient_sine(repeat)


__all__ = [
    "gradient",
    "make_gradient_frames",
    "apply_gradient_map",
    "gradient_vstack",
    "save_palette_as_image",
]
