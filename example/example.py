from halftonism import Project

p = Project("example.ora", repeat=16, waveform="triangle")
p.save_GIF("example.gif", scale=0.25, miliseconds=70, colors=30, resample=3)
