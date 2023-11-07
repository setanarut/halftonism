# Halftonism

Artistic halftone generation library

![Krita ORA Screenshot](./example/example.gif)


## Installation

```shell
pip install git+https://github.com/setanarut/halftonism
```

#### Example

```python
from halftonism import Project

p = Project("example.ora", repeat=16, waveform="triangle")
p.save_GIF("example.gif", scale=0.25, miliseconds=70, colors=30, resample=3)
```

## Tutorial

### Preparing the ORA file
You can open the example.ora file in [example](./example/) folder with the [Krita](https://docs.krita.org/en/general_concepts/file_formats/file_ora.html). ([Openraster](https://www.openraster.org/) format). In the example you can see the color layers obtained using [fastLayerDecomposition](https://github.com/CraGL/fastLayerDecomposition) repository. It can also be done by hand painting without color layer decomposition.
Play around with layer orders and alpha levels for a more color balanced halftone outputs.

![Krita ORA Screenshot](./assets/krita_ORA_SS.jpg)

#### ORA Layer Structure

Before processing the ORA file with Python, you have to follow the template below.

1. Each color layer should contain only a single color.

2. The bottom background layer (base color) must be solid color.

3. There should be a grayscale heightmap at the top layer for halftone patterns. Top layer can be a computer generated heightmap ([Hydraulic-Erosion](https://github.com/dandrino/terrain-erosion-3-ways#simulation), Mandelbrot fractals) or real [DEM heightmaps](https://tangrams.github.io/heightmapper/) or any suitable grayscale gradient.  


### ORA processing with halftonism package

#### Antialiasing

For antialiasing, you can downscale image with [bicubic sampling](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#PIL.Image.Resampling.BICUBIC). For example, you can start with 2000x2000 and downscale to 500x500 for final output (500 / 2000 = 0.25 scale). The `save_GIF()` `save_APNG()` and `save_frame()` methods have `scale` and [resample](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#PIL.Image.Resampling.BICUBIC) arguments. 

Resampling example with `NEAREST` on the left and `BICUBIC` on the right. (scale 0.25)

![downsample](./assets/downsample.png)

```python
p.save_GIF("output.gif", scale=0.25, resample=Resampling.BICUBIC)
p.save_frame(0, "01_frame.png", scale=0.25., resample=3)
```

#### Project parameters

TO DO

#### Tips and tricks

TO DO
