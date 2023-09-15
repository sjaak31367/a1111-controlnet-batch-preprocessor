# A1111 ControlNet Batch Pre-processor

A script to apply AUTOMATIC1111's [Stable Diffusion web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) [ControlNet Extension](https://github.com/Mikubill/sd-webui-controlnet) to a bunch of images with a single click, and store all the outputs, rather than having to run the ControlNet manually for each and every input image.  
-----
Originally made just to speed up running a bunch of video frames through OpenPose, but it might also be useful for other things for other people. :)  
**It's currently just a stand-alone Python script, but it might be an A1111 Extension at some point (or not).**

## Feature plans:
- Command line argument for url/port.
- Allow videos as input, and extract frames through FFMPEG.
- Make this an A1111 Extension.

## Examples:
(todo)  
placeholder:  
input dir: frame_01.png, frame_02.png, frame_03.png, ...  
Run script  
=  input/frame_01.png -> ControlNet -> output/frame_01.png  
=  input/frame_02.png -> ControlNet -> output/frame_02.png  
=  ...)  
output dir: frame_01.png, frame_02.png, frame_03.png, ...
![image](../assets/image.png)

## Requirements:
[AUTOMATIC1111 Stable Diffusion web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui),  
[ControlNet Extension](https://github.com/Mikubill/sd-webui-controlnet),  
[This repository](https://github.com/sjaak31367/a1111-controlnet-batch-preprocessor)

## Install:
1. Make sure you have A1111, and the ControlNet extension installed.
2. Install this repository (Either by hitting the green Code button, or by opening up CMD/GIT_Bash/Terminal and running  
`git clone https://github.com/sjaak31367/a1111-controlnet-batch-preprocessor.git`).
3. Run A1111 with `--api` flag.  
3.1. In `A1111/webui/webui-user.bat` line `set COMMANDLINE_ARGS=` append `--api` and restart A1111 (not just reload).

## Usage:
1. Have A1111 running. (at 127.0.0.1:7860, or edit in `scripts/script.py`)
2. Place the images you wish to run through a ControlNet in `inputs/*`.
3.
```sh
$ cd scripts  
$ python script.py
```
4. Wait as the images are run through the ControlNet.  
5. Results should be in `outputs/*`. :)

## Credits & License:
This repository: Sjaak31367 and contributors under AGPL-3.0  
Thanks to AUTOMATIC1111 and contributors for creating Stable Diffusion web UI!  
Thanks to Mikubill and contributors for creating ControlNet Extension!
