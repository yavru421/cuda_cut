import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import onnxruntime as ort
from rembg import remove, new_session
import subprocess
import time

def is_cuda_available():
    try:
        providers = ort.get_available_providers()
        return 'CUDAExecutionProvider' in providers
    except Exception:
        return False

def process_images(input_paths, output_dir, log_callback, session=None, progress_callback=None):
    total = len(input_paths)
    for idx, file in enumerate(input_paths):
        try:
            with Image.open(file) as img:
                out = remove(img, session=session) if session else remove(img)
                out_path = os.path.join(output_dir, os.path.basename(file))
                if out_path.lower().endswith(('.jpg', '.jpeg')) and out.mode == 'RGBA':
                    out = out.convert('RGB')
                if out.mode == 'RGBA' and not out_path.lower().endswith('.png'):
                    out_path = os.path.splitext(out_path)[0] + '.png'
                out.save(out_path)
                log_callback(f"Processed: {file} -> {out_path}")
        except Exception as e:
            log_callback(f"Failed: {file} ({e})")
        if progress_callback:
            progress_callback(idx + 1, total)
def preview_image():
    path = input_var.get()
    if not path or not os.path.isfile(path):
        messagebox.showerror("Error", "Please select a valid image file.")
        return
    try:
        img = Image.open(path)
        img.thumbnail((256, 256))
        img_tk = ImageTk.PhotoImage(img)
        preview_panel.img = img_tk
        preview_panel.config(image=img_tk)
        # Try to show processed preview
        session = get_user_session()
        out = remove(img, session=session) if session else remove(img)
        out.thumbnail((256, 256))
        out_tk = ImageTk.PhotoImage(out)
        preview_panel_out.img = out_tk
        preview_panel_out.config(image=out_tk)
    except Exception as e:
        messagebox.showerror("Preview Error", str(e))

def preview_video():
    path = input_var.get()
    if not path or not os.path.isfile(path):
        messagebox.showerror("Error", "Please select a valid video file.")
        return
    try:
        subprocess.Popen(["ffplay", path])
    except Exception as e:
        messagebox.showerror("Preview Error", f"Failed to launch ffplay: {e}")

def get_user_session():
    provider = provider_var.get()
    model = model_var.get()
    kwargs = {}
    if provider != "Auto":
        kwargs["providers"] = [provider]
        if provider == "CUDAExecutionProvider":
            cuda_id = cuda_id_var.get()
            mem_limit = cuda_mem_var.get()
            opts = {}
            if cuda_id:
                opts["device_id"] = int(cuda_id)
            if mem_limit:
                opts["gpu_mem_limit"] = int(mem_limit)
            kwargs["provider_options"] = [opts]
    try:
        return new_session(model_name=model, **kwargs)
    except Exception as e:
        messagebox.showerror("Session Error", f"Failed to create session: {e}")
        return None

def select_input():
    path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
    if path:
        input_var.set(path)

def select_input_folder():
    path = filedialog.askdirectory(title="Select Folder")
    if path:
        input_var.set(path)

def select_output():
    path = filedialog.askdirectory(title="Select Output Folder")
    if path:
        output_var.set(path)

def update_progress(current, total):
    progress_var.set(int((current / total) * 100))
    progress_bar.update_idletasks()

def run_removal():
    input_path = input_var.get()
    output_dir = output_var.get()
    if not input_path or not output_dir:
        messagebox.showerror("Error", "Please select both input and output paths.")
        return
    if os.path.isdir(input_path):
        files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"))]
    else:
        files = [input_path]
    os.makedirs(output_dir, exist_ok=True)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Starting background removal...\n")
    progress_var.set(0)
    session = get_user_session()
    def worker():
        process_images(files, output_dir, lambda msg: log_text.insert(tk.END, msg + "\n"), session=session, progress_callback=update_progress)
        log_text.insert(tk.END, "Done.\n")
        progress_var.set(100)
    threading.Thread(target=worker, daemon=True).start()

root = tk.Tk()
root.title("CUDA_Cut (by John Daniel Dondlinger)")
root.geometry("900x650")

input_var = tk.StringVar()
output_var = tk.StringVar()
provider_var = tk.StringVar(value="Auto")
cuda_id_var = tk.StringVar()
cuda_mem_var = tk.StringVar()
model_var = tk.StringVar(value="u2net")
progress_var = tk.IntVar(value=0)

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill="x")

input_label = tk.Label(frame, text="Input Image/Folder/Video:")
input_label.grid(row=0, column=0, sticky="w")
input_entry = tk.Entry(frame, textvariable=input_var, width=50)
input_entry.grid(row=0, column=1, padx=5)
input_img_btn = tk.Button(frame, text="Select Image", command=select_input)
input_img_btn.grid(row=0, column=2, padx=2)
input_folder_btn = tk.Button(frame, text="Select Folder", command=select_input_folder)
input_folder_btn.grid(row=0, column=3, padx=2)

output_label = tk.Label(frame, text="Output Folder:")
output_label.grid(row=1, column=0, sticky="w", pady=(10,0))
output_entry = tk.Entry(frame, textvariable=output_var, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=(10,0))
output_btn = tk.Button(frame, text="Select Output Folder", command=select_output)
output_btn.grid(row=1, column=2, padx=2, pady=(10,0))

# Model picker
model_label = tk.Label(frame, text="Model:")
model_label.grid(row=2, column=0, sticky="w", pady=(10,0))
model_options = [
    ("u2net", "U2Net (default, general purpose)"),
    ("u2netp", "U2Netp (fast, lightweight)"),
    ("u2net_human_seg", "U2Net Human Seg (best for people)"),
    ("silueta", "Silueta (cartoon/illustration)")
]
model_menu = tk.OptionMenu(frame, model_var, *(opt[0] for opt in model_options))
model_menu.grid(row=2, column=1, sticky="w", pady=(10,0))
model_desc_label = tk.Label(frame, text=model_options[0][1], fg="gray")
model_desc_label.grid(row=2, column=2, columnspan=2, sticky="w", pady=(10,0))

def update_model_desc(*args):
    val = model_var.get()
    for k, desc in model_options:
        if k == val:
            model_desc_label.config(text=desc)
            break
model_var.trace_add('write', update_model_desc)

# Provider selection
provider_label = tk.Label(frame, text="Provider:")
provider_label.grid(row=3, column=0, sticky="w", pady=(10,0))
provider_menu = tk.OptionMenu(frame, provider_var, "Auto", "CUDAExecutionProvider", "CPUExecutionProvider")
provider_menu.grid(row=3, column=1, sticky="w", pady=(10,0))

cuda_id_label = tk.Label(frame, text="CUDA Device ID:")
cuda_id_label.grid(row=3, column=2, sticky="e", pady=(10,0))
cuda_id_entry = tk.Entry(frame, textvariable=cuda_id_var, width=5)
cuda_id_entry.grid(row=3, column=3, sticky="w", pady=(10,0))

cuda_mem_label = tk.Label(frame, text="CUDA Mem Limit (MB):")
cuda_mem_label.grid(row=4, column=2, sticky="e", pady=(0,0))
cuda_mem_entry = tk.Entry(frame, textvariable=cuda_mem_var, width=8)
cuda_mem_entry.grid(row=4, column=3, sticky="w", pady=(0,0))

cuda_status = "CUDA Available" if is_cuda_available() else "CUDA NOT Available (using CPU)"
cuda_label = tk.Label(root, text=f"ONNX Runtime: {cuda_status}", fg="green" if "Available" in cuda_status else "red")
cuda_label.pack(anchor="w", padx=10, pady=(10,0))

# Progress bar
progress_bar = tk.Scale(root, from_=0, to=100, orient="horizontal", variable=progress_var, length=600, showvalue=0, state="disabled")
progress_bar.pack(padx=10, pady=(5,0))

# Preview panel
preview_frame = tk.Frame(root)
preview_frame.pack(padx=10, pady=10, fill="x")
tk.Label(preview_frame, text="Input Preview:").grid(row=0, column=0)
tk.Label(preview_frame, text="Output Preview:").grid(row=0, column=1)
preview_panel = tk.Label(preview_frame)
preview_panel.grid(row=1, column=0, padx=10)
preview_panel_out = tk.Label(preview_frame)
preview_panel_out.grid(row=1, column=1, padx=10)

preview_btn = tk.Button(preview_frame, text="Preview Image", command=preview_image)
preview_btn.grid(row=2, column=0, pady=5)
preview_video_btn = tk.Button(preview_frame, text="Preview Video (ffplay)", command=preview_video)
preview_video_btn.grid(row=2, column=1, pady=5)

start_btn = tk.Button(root, text="Start Background Removal", command=run_removal, bg="#4CAF50", fg="white")
start_btn.pack(pady=10)

log_text = tk.Text(root, height=14, width=100)
log_text.pack(padx=10, pady=5)

root.mainloop()
