import torch

class HebbianUpdater:
    """
    Implements the "NoProp" local learning rule for Fast Weights.

    Delta W = eta * (Target - Output) * Input

    In CCF, 'Target' is approximated by the 'Surprise' signal or next-token ground truth
    without global backpropagation.
    """

    def __init__(self, learning_rate=0.001):
        self.eta = learning_rate

    def update_fast_weights(self, fast_weights_layer, input_activation, target_activation):
        """
        Performs a local update on the weights.

        Args:
            fast_weights_layer (nn.Linear): The layer to update.
            input_activation (Tensor): Pre-synaptic activity [Batch, Dim].
            target_activation (Tensor): Post-synaptic target/surprise [Batch, Dim].
        """
        # Forward pass through current weights to get current output
        current_output = fast_weights_layer(input_activation)

        # Calculate local error
        error = target_activation - current_output

        # Calculate Delta W: Outer product of Error and Input
        # dW = eta * (Error^T * Input)
        # Dimensions: [Dim, Batch] * [Batch, Dim] -> [Dim, Dim]

        # Using Batch Multiplication via Einstein Summation for efficiency
        delta_w = self.eta * torch.einsum('bi,bj->ij', error, input_activation)

        # Normalize by batch size
        delta_w /= input_activation.size(0)

        # In-place update of weights
        with torch.no_grad():
            fast_weights_layer.weight.add_(delta_w)

        return error.norm().item()
