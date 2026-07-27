import torch

class HolographicMemory:
    """
    Implements Holographic Reduced Representations (HRR) operations.
    Memory is stored as vector superposition in the weight matrix.

    Binding: Circular Convolution (A * B)
    Unbinding: Circular Correlation (A # B)
    Superposition: Vector Addition (A + B)
    """

    @staticmethod
    def bind(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """
        Performs localized binding of two vectors via Circular Convolution.
        Mathematically: x * y = IFFT(FFT(x) * FFT(y))
        """
        x_fft = torch.fft.rfft(x, dim=-1)
        y_fft = torch.fft.rfft(y, dim=-1)
        bound = torch.fft.irfft(x_fft * y_fft, n=x.shape[-1], dim=-1)
        return bound

    @staticmethod
    def unbind(memory_trace: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
        """
        Retrieves an item from the holographic trace via Circular Correlation.
        Mathematically: M # K = IFFT(FFT(M) * conj(FFT(K)))
        """
        m_fft = torch.fft.rfft(memory_trace, dim=-1)
        k_fft = torch.fft.rfft(key, dim=-1)
        # Using conjugate for correlation
        retrieved = torch.fft.irfft(m_fft * torch.conj(k_fft), n=memory_trace.shape[-1], dim=-1)
        return retrieved

    @staticmethod
    def superimpose(memory_trace: torch.Tensor, new_item: torch.Tensor) -> torch.Tensor:
        """
        Adds a new item to the holographic memory trace.
        """
        return memory_trace + new_item

    @staticmethod
    def cosine_similarity(v1: torch.Tensor, v2: torch.Tensor) -> torch.Tensor:
        return torch.nn.functional.cosine_similarity(v1, v2, dim=-1)
