import numpy as np
from os import mkdir, path
from shutil import rmtree
from PIL import Image
from pyora import Project as PyoraProject

# local
from .utils import (
    make_gradient_frames,
    _most_common_color_RGBA,
    _most_common_color_RGB,
    save_palette_as_image,
)


class Project:
    def __init__(
        self,
        ORA_path: str,
        repeat=8,
        waveform="sawtooth",
        frame_skipping=1,
    ):
        """frame_skipping 1 means no drop frame, 2 means drop every second frame"""
        self.paint_layers_alphas = []
        self.ORA = PyoraProject.load(ORA_path)
        self.palette = []
        self.top_layer = np.array(
            self.ORA.children[0].get_image_data(False).convert("L")
        )
        self.bottom_layer = np.array(
            self.ORA.children[-1].get_image_data(False).convert("RGB")
        )
        self.palette.append(_most_common_color_RGB(self.bottom_layer))
        # paint layers
        for idx, paint_layer in enumerate(reversed(self.ORA.children[1:-1])):
            p_layer_alpha = np.array(paint_layer.get_image_data(False).getchannel("A"))
            self.paint_layers_alphas.append(p_layer_alpha)
            p_layer = np.array(paint_layer.get_image_data(False).convert("RGBA"))
            color = _most_common_color_RGBA(p_layer)
            if color == False:
                raise Exception(
                    "Paint Layer {0} does not have opaque RGB color. The layer is completely transparent.".format(
                        idx
                    )
                )
            self.palette.append(color)

        self.gradient_frames = make_gradient_frames(
            frame_skipping=frame_skipping, repeat=repeat, waveform=waveform
        )
        self.total_frames = self.gradient_frames.shape[0]

    def save_palette(self, image_path: str):
        save_palette_as_image(self.palette, image_path)

    def get_paint_image(self, index):
        return Image.fromarray(self.paint_layers_alphas[index])

    def get_frame(self, frame_index: int) -> np.ndarray:
        """render and get single animation frame"""

        halftone_pattern = np.take(self.gradient_frames[frame_index], self.top_layer)
        # copy background layer for animation frame
        background_layer = self.bottom_layer.copy()

        for idx, paint_alpha in enumerate(self.paint_layers_alphas):
            # %50 blending
            blend = (paint_alpha.astype("int16") + halftone_pattern.astype("int16")) / 2
            # threshold for halftone
            threshold_mask = blend > 128
            # Paint each paint layer color over the background. (skip base color)
            background_layer[threshold_mask] = self.palette[idx + 1]
        return background_layer

    def save_frame(self, frame_index, file_path, scale=1, resample=3):
        """render frame and write to current dir"""
        frame = self.get_frame(frame_index)
        w, h = self.ORA.dimensions
        size = (round(w * scale), round(h * scale))
        frame = Image.fromarray(frame)
        if scale != 1:
            frame = frame.resize(size, resample=resample)
        frame.save(file_path)

    def save_frames(self):
        """saves frames to folder"""
        folder = "frames"
        if not path.exists(folder):
            mkdir(folder)
        if path.exists(folder):
            rmtree(folder)
            mkdir(folder)

        for i in range(self.total_frames):
            Image.fromarray(self.get_frame(i)).save("frames/" + str(i) + ".png")

    def save_halftone_patterns(self):
        """Saves heigthmap frames to folder"""
        folder = "dem_frames"
        if not path.exists(folder):
            mkdir(folder)
        if path.exists(folder):
            rmtree(folder)
            mkdir(folder)
        for i in range(self.total_frames):
            pattern = np.take(self.gradient_frames[i], self.top_layer)
            Image.fromarray(pattern).save("dem_frames/" + str(i) + ".png")

    def print_info(self):
        print("Project dimensions: {0}".format(self.ORA.dimensions))
        for i, c in enumerate(self.palette):
            print("Paint Layer:", i, c)

    def save_GIF(
        self,
        filename,
        scale=0.5,
        miliseconds=50,
        colors=256,
        resample=Image.Resampling.BICUBIC,
    ):
        # Image.Resampling.NEAREST = 0
        # Image.Resampling.BICUBIC = 3
        # Image.Resampling.LANCZOS = 1

        w, h = self.ORA.dimensions
        size = (round(w * scale), round(h * scale))
        gifa = []
        for x in range(self.total_frames):
            frm = Image.fromarray(self.get_frame(x))
            frm = frm.resize(size, resample=resample)
            # frm.thumbnail(size )
            frm = frm.convert(
                mode="P",
                matrix=None,
                dither=None,
                palette=Image.ADAPTIVE,
                colors=colors,
            )
            gifa.append(frm)
        # duration 100 milliseconds gives 10 frames per second
        gifa[0].save(
            filename,
            save_all=True,
            append_images=gifa[1:],
            dither=None,
            optimize=False,
            duration=miliseconds,
            loop=0,
        )

    def save_APNG(
        self, filename, scale=0.25, miliseconds=64, resample=Image.Resampling.BICUBIC
    ):
        # Image.Resampling.NEAREST = 0
        # Image.Resampling.BICUBIC = 3
        # Image.Resampling.LANCZOS = 1
        w, h = self.ORA.dimensions
        frames = []
        size = (round(w * scale), round(h * scale))
        for x in range(self.total_frames):
            frame = Image.fromarray(self.get_frame(x))
            frame = frame.resize(size, resample=resample)
            frames.append(frame)
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=miliseconds,
            loop=0,
        )
