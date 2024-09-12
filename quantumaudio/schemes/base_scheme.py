from abc import ABC, abstractmethod
from typing import Any
import numpy as np
import qiskit

class Scheme(ABC):
    """
    Abstract base class for Quantum Audio Schemes.

    This class defines the bare minimum interface that any specific modulation
    scheme must follow. Subclasses should provide implementations
    of the `encode` and `decode` methods according to the specifics of their
    modulation schemes.
    """

    @abstractmethod
    def encode(self, data: np.ndarray) -> qiskit.QuantumCircuit:
        """Encode the input data using the scheme.

        Args:
            data: A numpy array containing the data to be encoded.

        Returns:
            A qiskit.QuantumCircuit representing the encoded data.
        """
        pass

    @abstractmethod
    def decode(self, circuit: qiskit.QuantumCircuit) -> np.ndarray:
        """Decode the quantum circuit using the scheme.

        Args:
            circuit: A qiskit.QuantumCircuit that contains the encoded data.

        Returns:
            A numpy array containing the decoded data.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the modulation scheme."""
        return f'{self.name} ({self.__class__.__name__})'