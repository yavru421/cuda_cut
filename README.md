
# CUDA_Cut

Created by: John Daniel Dondlinger

CUDA_Cut is a simple, GPU-accelerated GUI application for removing backgrounds from images and videos using AI models (CUDA, cuDNN, ONNX Runtime, etc.).

## Features
- Easy-to-use graphical interface
- Batch processing of images and videos
- GPU acceleration (CUDA, cuDNN, ONNX Runtime)
- Automatic dependency installation
- ffplay/ffmpeg video preview support (optional)

## Requirements
- Windows 10/11
- Python 3.10+ (recommended)
- NVIDIA GPU with CUDA support (for GPU acceleration)
- [ffmpeg](https://ffmpeg.org/download.html) (optional, for video preview)

## Setup
1. **Install Python 3.10+** and add it to your PATH.
2. **Create a virtual environment** (if not already present):
   ```sh
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   ```sh
   venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **(Optional) Install ffmpeg** for video preview:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH, or
   - Use Chocolatey: `choco install ffmpeg`

## Usage
- Double-click `run_gui.bat` or run it from a terminal:
  ```sh
  run_gui.bat
  ```
- The script will check/install dependencies and launch the CUDA_Cut GUI.
- Input images go in the `input_images/` folder; output will be saved to `output_images/`.

## Troubleshooting
- If you see a warning about `ffplay`/`ffmpeg`, install it and add to your PATH for video preview.
- If you see a message about the virtual environment not found, create it as described above.
- For CUDA/cuDNN issues, ensure your GPU drivers and CUDA/cuDNN libraries are installed and match your hardware.

## Credits
- Created by John Daniel Dondlinger
- Uses [rembg](https://github.com/danielgatis/rembg), [onnxruntime-gpu](https://onnxruntime.ai/), and other open-source libraries.

---

For more help, open an issue or contact John Daniel Dondlinger.
