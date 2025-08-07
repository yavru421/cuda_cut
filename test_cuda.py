import onnxruntime as ort

def main():
    providers = ort.get_available_providers()
    print(f"ONNX Runtime available providers: {providers}")
    if 'CUDAExecutionProvider' in providers:
        print("CUDA (GPU) is available and will be used by ONNX Runtime.")
    else:
        print("CUDA (GPU) is NOT available. ONNX Runtime will use CPU.")

if __name__ == "__main__":
    main()
