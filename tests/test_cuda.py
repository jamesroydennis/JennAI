# /home/jdennis/Projects/JennAI/tests/test_cuda.py

import torch
import pytest # Import pytest for test functionality

# This part runs when you execute the script directly (e.g., 'python tests/test_cuda.py')
# It provides immediate feedback on CUDA availability.
if __name__ == '__main__':
    print(f"Is CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA is NOT available. Tests requiring CUDA will likely fail.")


# This is a pytest test function
# pytest will discover and run any function starting with 'test_'
def test_cuda_device_available():
    """
    Tests if a CUDA-enabled GPU device is available and can be accessed by PyTorch.
    """
    # Use an assert statement for pytest to check for success/failure
    assert torch.cuda.is_available(), "CUDA is not available or not detected by PyTorch!"

    # Optional: print more detailed info if CUDA is available, for verbose output (-v)
    if torch.cuda.is_available():
        print(f"\n[Test] CUDA device count: {torch.cuda.device_count()}")
        print(f"[Test] Current CUDA device: {torch.cuda.current_device()}")
        print(f"[Test] CUDA device name: {torch.cuda.get_device_name(0)}")

    # You can add more specific checks here, e.g.,
    # assert torch.cuda.device_count() > 0, "No CUDA devices found!"
    # assert "NVIDIA" in torch.cuda.get_device_name(0), "CUDA device is not an NVIDIA GPU!"

# You can also add a pytest marker to easily run only CUDA tests later
# @pytest.mark.cuda # Uncomment this line if you added 'cuda' marker in pyproject.toml
# def test_some_gpu_specific_functionality():
#     # Test code that specifically uses GPU tensors or operations
#     a = torch.tensor([1, 2, 3], device='cuda')
#     b = torch.tensor([4, 5, 6], device='cuda')
#     assert torch.all(a + b == torch.tensor([5, 7, 9], device='cuda'))
