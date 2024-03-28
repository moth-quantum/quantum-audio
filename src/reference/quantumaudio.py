# ==============================================================================
#                                  quantumaudio
#
# A Python class implementation for Quantum Representations of Audio in Qiskit
#
# Paulo Vitor Itaboraí (2022-2023)
#
# Itaborala @ QuTune Project, ICCMR Quantum - University of Plymotuh
#
# https://github.com/iccmr-quantum/quantumaudio (repo)
# https://iccmr-quantum.github.io/ (qutune website)
# ==============================================================================

import numpy as np
import numpy.typing as npt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute
from qiskit_aer import AerProvider
from qiskit.result import Counts
from qiskit.tools import job_monitor
from qiskit.compiler import transpile
from qiskit.visualization import plot_histogram
from bitstring import BitArray
from IPython.display import display, Audio
import matplotlib.pyplot as plt
import warnings
from typing import TypeVar, Optional, Tuple, Any



# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# =================================== QPAM =====================================
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

class QPAM():
    def __init__(self):
        self.norm = 1.
        
    def __repr__(self):
        return self.__class__.__name__
    
    def convert(self, original_audio: npt.NDArray) -> npt.NDArray:
        """Converts the digital audio into an array of probability amplitudes.

        The audio signal is normalized. The normalized samples can then be
        interpreted as probability amplitudes. In other words, by squaring every
        sample, their total sum is now 1.

        Args:
            original_audio: Numpy Array containing audio information.  
        
        Returns: 
            A Numpy Array containing normalized probability amplitudes.
        """
        prepared = (original_audio.copy()+1)/2
        self.norm = np.linalg.norm(prepared)
        return prepared/self.norm
    
    def prepare(self, audio_amplitudes: npt.NDArray, regsize: Tuple[int, int], regnames: Tuple[str, str], print_state: bool = False) -> 'QuantumCircuit':
        """Prepares a QPAM quantum circuit.

        Creates a qiskit QuantumCircuit that prepares a Quantum Audio state 
        using QPAM (Quantum Probability Amplitude Modulation) representation.
        The quantum circuits used for audio representations typically contain 
        two qubit registers, namely, 'treg' (which encodes time/index information) 
        and 'areg' (which encodes amplitude information).

        Note: In QPAM, the 'areg' (amplitude) register is NOT used as the amplitude 
        information is encoded in the probability amplitudes of the 'treg' (time) 
        register.
        
        Args:
            audio_amplitudes: Array with propbability amplitudes
            regsize: The size of both qubit registers in a tuple (treg_size, areg_size). 
                'treg_size' qubits for 'treg'; 'areg_size' qubits for 'areg'. 
                For QPAM, 'areg_size' is ALWAYS 0
            regnames: Label names for 'treg' and 'areg', passed as a tuple. For 
                visualization purposes only.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only.

        Returns: 
            A qiskit QuantumCircuit with specific QPAM preparation instructions.
        """

        # QPAM only needs the time register's size .
        # It doesn't have an amplitude register, so areg_size is necessarily 0
        treg_size=regsize[0]
        
        # Creates a Quantum Circuit
        treg = QuantumRegister(treg_size, regnames[0])
        qpam = QuantumCircuit(treg)
        
        # Value Setting Operation
        qpam.initialize(list(audio_amplitudes), treg)
            
        if print_state:
            for i, amps in enumerate(audio_amplitudes):
                print(f'{amps:.3f}|{i}>', end='')
                if i<len(audio_amplitudes)-1:
                    print(' + ', end='')
                else:
                    print()
        return qpam
    
    def measure(self, qc: 'QuantumCircuit', treg_pos: int = 0) -> None:
        """Appends Measurements to a QPAM audio circuit
        
        From a quantum circuit with a register containing a QPAM 
        representation of quantum audio, creates a classical register with 
        compatible size and adds isntructions for measuring the QPAM register.

        Args:
            qc: A qiskit quantum circuit containing at least 1 quantum register.
            treg_pos: Index of the QPAM ('treg') register in the circuit. 
                Default is 0
        """
        # Accesses the QuantumRegister containing the time information
        treg = qc.qregs[treg_pos]
        
        ctreg = ClassicalRegister(treg.size, 'ct')
        qc.add_register(ctreg)
        qc.measure(treg, ctreg)
        
    def reconstruct(self, treg_size: int, counts: 'Counts', shots: int, g: Optional[float] = None) -> npt.NDArray:
        """Builds a digital Audio from qiskit histogram data.

        Considering the QPAM encoding scheme, it uses the histogram data stored 
        in a Counts object (qiskit.result.Counts) to reconstruct an audio
        signal. It renormalizes the histogram counts and remaps the signal back 
        to the [-1 to 1] range.
        
        Args:
            treg_size: Size of the 'treg' (time) register.
            counts: Histogram from a qiskit job result (result.get_counts())
            shots: Amount of identical experiments ran by the qiskit job.
            g: Gain factor. This is a renormalization factor.
                (When bypassing audio signals through quantum circuits, this
                factor is usually proportional to the origal audio's norm).

        Returns:
            A Digital Audio as a Numpy Array. The signal is in float format.
        """
        g = self.norm if g is None else g
        
        # Builds a zeroed ndarray
        da = np.zeros(2**treg_size)
        
        # Assigns the respective probabilities to the array
        index = np.array([int(key, 2) for key in counts])
        da[index] = list(counts.values())

        # Renormalization, rescaling, and shifting
        return 2*g*np.sqrt(da/shots) -1


# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# =================================== SQPAM ====================================
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

class SQPAM():
    def __init__(self):
        pass
    
    def __repr__(self):
        return self.__class__.__name__
    
    def treg_index_X(self, qa: 'QuantumCircuit', t: int, treg: 'QuantumRegister', print_state: bool = False) -> None:
        r""" Auxilary function for matching control conditions with time indexes.
        
        Applies X gates on qubits of the time register whenever the respective 
        bit of the current time index (in binary representation) is 0. As a 
        result, the qubit will be flipped to \|1> and succesfully trigger 
        necessary control conditions of the circuit for this time index.

        Args:
            qa: The quantum circuit to be maniputated
            t: Time index that will be converted to binary form for comparison.
            treg: Quantum register of the time indexes.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only. To be used together 
                with all other SQPAM methods with a 'print_state' kwarg.

        Examples:
            treg_index_X(qa, 6, treg)
            (a time register 'treg' with, say, 5 qubits in 'qa' at instant 6)

            't' = 6 == '00110'. *treg_index_X()* applies X gates to qubits 0, 3 and 4
                (right to left) of register 'treg'.
        """
        t_bitstring = []
        for i, treg_qubit in enumerate(treg):
            t_bit = (t >> i) & 1
            t_bitstring.append(t_bit)
            if not t_bit:
                qa.x(treg_qubit)
        if print_state:
            print('|',end='')

            for i in reversed(t_bitstring):    
                print(i, end='')
            print('>',end='')
    
    def mc_Ry_2theta_t(self, qa: 'QuantumCircuit', t: int, a: float, treg: 'QuantumRegister', areg: 'QuantumRegister', print_state: bool = False) -> None:
        """ SQPAM Value-Setting operation.

        Applies a controlled Ry(2*theta) gate to the amplitude register, 
        controlled by the time register at the respective time index
        state. In other words. At index 't', it rotates the aplitude qubit
        by the angle mapped from the audio sample at the same index. 
        In quantum computing terms, this translates to a multi-controlled
        rotation gate.

        Args:
            qa: The quantum circuit to be manipulated.
            t: Time index that will be encoded.
            a: Angle of rotation.
            treg: Time register, 'treg'.
            areg: Amplitude Register, 'areg'.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only. To be used together 
                with all other SQPAM methods with a 'print_state' kwarg.
        """

        # Applies the necessary X gates at index t
        self.treg_index_X(self, qa, t, treg)

        # Creates an auxiliary circuit for the respective multi-controlled gates
        mc_ry = QuantumCircuit()
        mc_ry.add_register(areg)
        mc_ry.ry(2*a, 0)
        mc_ry = mc_ry.control(treg.size)
        # Appends the circuit to qa
        qa.append(mc_ry, [i for i in range(treg.size + areg.size - 1, -1, -1)])

        # Prints the state
        if print_state:
            print(f'[cos({a:.3f})|0> + sin({a:.3f})|1>]', end='')       

        # Applies the X gates again, 'resetting' the time register
        self.treg_index_X(self, qa, t, treg, print_state)
    
    def convert(self, original_audio: npt.NDArray) -> npt.NDArray:
        r"""Converts digital audio into an array of probability amplitudes.

        The audio signal is mapped to an array of angles. The angles can then 
        be interpreted as real-valued parameters for a trigonometric 
        representation subspace of a qubit. In other words, the angles are used 
        to rotate a qubit - originally in the \|0> state - to the following 
        state: ( cos(angle)\|0> + sin(angle)\|1> ). Notice that this preserves 
        probabilities, as cos^2 + sin^2 = 1.

        Note: By convention, we are using the *np.arcsin* function to calculate 
        the angles. This means that the *SQPAM.reconstruct()* method will use 
        the even (sine) bins of the histogram to retrieve the signal.

        Args:
            original_audio: Numpy Array containing audio information.  
        
        Returns: 
            A Numpy Array containing angles between 0 and pi/2.
        """
        return np.arcsin(np.sqrt((original_audio+1)/2))
    
    def prepare(self, angles: npt.NDArray, regsize: Tuple[int, int], regnames: Tuple[str, str], print_state: bool = False) -> 'QuantumCircuit':
        """Prepares an SQPAM quantum circuit.

        Creates a qiskit QuantumCircuit that prepares a Quantum Audio state 
        using SQPAM (Single-Qubit Probability Amplitude Modulation).
        The quantum circuits used for audio representations typically contain 
        two qubit registers, namely, 'treg' (which encodes time/index information) 
        and 'areg' (which encodes amplitude information).

        Note: In SQPAM (as hinted by its name), the 'areg' (amplitude) register 
        contains a single qubit. The audio samples are mapped into angles that
        parametrize single qubit rotations of 'areg' - which are then correlated 
        to index states of the 'treg' register. 
        
        Args:
            angles: Array with propbability amplitudes
            regsize: The size of both qubit registers in a tuple (treg_size, areg_size). 
                'treg_size' qubits for 'treg'; 'areg_size' qubits for 'areg'. 
                For SQPAM, 'areg_size' is ALWAYS 1
            regnames: Label names for 'treg' and 'areg', passed as a tuple. For 
                visualization purposes only.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only.

        Returns: 
            A qiskit quantum circuit containing specific SQPAM preparation
            instructions.
        """
        
        # SQPAM has a single-qubit amplitude register,
        # so 'areg_size' is necessarily 1
        treg_size = regsize[0]
        # Time register
        treg = QuantumRegister(treg_size, regnames[0])
        # Amplitude register
        areg = QuantumRegister(1, regnames[1])

        # Init quantum circuit
        sq_pam = QuantumCircuit()
        sq_pam.add_register(areg)
        sq_pam.add_register(treg)
        
        # Hadamard Gate in the Time Register
        sq_pam.h(treg) 
        
        # Value setting operations
        for t, theta in enumerate(angles):        
            self.mc_Ry_2theta_t(self, sq_pam, t, theta, treg, areg, print_state)
            if  print_state and t != len(angles)-1:
                print(' + ')
        if print_state:
            print()  
        return sq_pam
    
    def measure(self, qc: 'QuantumCircuit', treg_pos: int = 1, areg_pos: int = 0) -> None:
        """Appends Measurements to an SQPAM audio circuit
        
        From a quantum circuit with registers containing an SQPAM 
        representation of quantum audio, creates two classical registers with 
        compatible sizes and adds instructions for measuring them.

        Args:
            qc: A quantum circuit containing at least 2 quantum registers.
            treg_pos: Index of the SQPAM ('treg') register in the circuit. 
                Default is 1
            areg_pos: Index of the SQPAM ('areg') register in the circuit. 
                Default is 0
        """
        # Creates classical registers for measurement
        treg = qc.qregs[treg_pos]
        areg = qc.qregs[areg_pos]
        
        ctreg = ClassicalRegister(treg.size, 'ct')
        careg = ClassicalRegister(areg.size, 'ca')
        qc.add_register(careg)
        qc.add_register(ctreg)

        # Measures the respective quantum registers
        qc.measure(treg, ctreg)
        qc.measure(areg, careg)
        
    def reconstruct(self, treg_size: int, counts: 'Counts', shots: int, inverted: bool = False, both: bool = False) -> npt.NDArray:
        """Builds a digital Audio from qiskit histogram data.

        Considering the SQPAM encoding scheme, it uses the histogram data stored 
        in a Counts object (qiskit.result.Counts) to reconstruct an audio
        signal. It separates the even bins (sine coefficients) from the odd 
        bins (cosine coefficients) of the histogram. Since the *SQPAM.convert()*
        method used the *np.arcsin()* function to prepare the state, the even 
        bins should be used for reconstructing the signal.

        However, the relations between sine and cosine means that a 
        reconstruction with the cosine terms will build a perfectly inverted 
        version of the signal. The user is able to choose between retrieving 
        original or phase-inverted (or both) signals.
        
        Args:
            treg_size: Size of the 'treg' (time) register, leading to the full
                audio size.
            counts: Histogram from a qiskit job result (result.get_counts())
            shots: Amount of identical experiments ran by the qiskit job.
            inverted: Retrieves the cosine amplitudes instead (leading to a 
                phase-inverted version of the signal).
            both: Retrieves both Sine and Cosine amplitudes in a tuple. 
                Overwrites the 'inverted' argument.

        Returns:
            A Digital Audio as a Numpy Array, or a Tuple with two signals. 
            The signals are in float format.
        """
        
        N = 2**treg_size
        
        cosine_amps = np.zeros(N)
        sine_amps = np.zeros(N)

        for state in counts:
            (t_bits, a_bit) = state.split()
            t = int(t_bits, 2)
            a = counts[state]
            
            if (a_bit == '0'):
                cosine_amps[t] = a
            elif (a_bit =='1'):
                sine_amps[t] = a


        if both:    
            return (cosine_amps, sine_amps)
        elif inverted:
            return 2*(cosine_amps/(cosine_amps+sine_amps))-1
        else:
            return 2*(sine_amps/(cosine_amps+sine_amps))-1
        

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ==================================== QSM =====================================
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

class QSM():
    def __init__(self):
        pass
    
    def __repr__(self):
        return self.__class__.__name__
    
    def treg_index_X(self, qc: 'QuantumCircuit', t: int, treg: 'QuantumRegister', print_state: bool = False) -> None:
        r""" Auxilary function for matching control conditions with time indexes.
        
        Applies X gates on qubits of the time register whenever the respective 
        bit of the current time index (in binary representation) is 0. As a 
        result, the qubit will be flipped to \|1> and succesfully trigger 
        necessary control conditions of the circuit for this time index.

        Args:
            qa: The quantum circuit to be maniputated
            t: Time index that will be converted to binary form for comparison.
            treg: Quantum register of the time indexes.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only. To be used together 
                with all other QSM methods with a 'print_state' kwarg.

        Examples:
            treg_index_X(qa, 6, treg)
            (a time register 'treg' with, say, 5 qubits in 'qa' at instant 6)

            't' = 6 == '00110'. *treg_index_X()* applies X gates to qubits 0, 3 and 4
                (right to left) of register 'treg'.
        """

        t_bitstring = []

        for i, treg_qubit in enumerate(treg):
            t_bit = (t >> i) & 1
            t_bitstring.append(t_bit)
            if not t_bit:
                qc.x(treg_qubit)
        if print_state:
            print('(x)|',end='')

            for i in reversed(t_bitstring):    
                print(i, end='')
            print('>',end='')
        
    def omega_t(self, qa: 'QuantumCircuit', t: int, a: int, treg: 'QuantumRegister', areg: 'QuantumRegister', print_state: bool = False) -> None:
        """QSM Value-Setting operation.     
        
        Applies a multi-controlled CNOT gate to qubits of amplitude register, 
        controlled by the time register at the respective time index
        state. In other words. At index 't', it flipps the amplitude qubits
        to match the original audio sample bits at the same index. 

        Args:
            qa: The quantum circuit to be manipulated.
            t: Time index that will be encoded.
            a: Quantized sample from original audio to be converted to binary.
            treg: Time register, 'treg'.
            areg: Amplitude Register, 'areg'.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only. To be used together 
                with all other SQPAM methods with a 'print_state' kwarg.
        """ 
        
        # Applies the necessary NOT gates at index t
        self.treg_index_X(self, qa, t, treg)
        astr=[]
        # Flips a qubit everytime a_bit==1
        for i, areg_qubit in enumerate(areg):
            a_bit = (a >> i) & 1
            astr.append(a_bit)
            if a_bit:
                qa.mct(treg, areg_qubit)

        if print_state:        
            print('|',end='')       
            for i in reversed(astr):    
                print(i, end='')
            print('>',end='')


        self.treg_index_X(self, qa, t, treg, print_state)
        
    def convert(self, original_audio):
        """ For the QSM encoding scheme, this function is dummy.
        
        QSM expects a quantized signal (N-Bit PCM) as input. 
        No pre-processing is needed after this point.
        """
        return original_audio
        
    def prepare(self, quantized_audio: npt.NDArray, regsize: Tuple[int, int], regnames: Tuple[str, str], print_state: bool = False) -> 'QuantumCircuit':
        """Prepares a QSM quantum circuit.

        Creates a qiskit QuantumCircuit that prepares a Quantum Audio state 
        using QSM (Quantum State Modulation).
        The quantum circuits used for audio representations typically contain 
        two qubit registers, namely, 'treg' (which encodes time/index information) 
        and 'areg' (which encodes amplitude information).

        Args:
            quantized_audio: Integer Array with the input signal.
            regsize: The size of both qubit registers in a tuple (treg_size, areg_size). 
                'treg_size' qubits for 'treg'; 'areg_size' qubits for 'areg'. 
            regnames: Label names for 'treg' and 'areg', passed as a tuple. For 
                visualization purposes only.
            print_state: Toggles a simple print of the prepared quantum state to the
                console, for visualization purposes only.

        Returns: 
            A qiskit quantum circuit containing specific QSM preparation
            instructions.
        """

        treg_size, areg_size = regsize

        # Time register
        treg = QuantumRegister(treg_size, regnames[0])
        # Amplitude register
        areg = QuantumRegister(areg_size, regnames[1])

        # Init quantum circuit
        qsm = QuantumCircuit()
        qsm.add_register(areg)
        qsm.add_register(treg)

        # Hadamard Gate in the Time Register
        qsm.h(treg)

        # Value setting operations
        for t, sample in enumerate(quantized_audio):        
            self.omega_t(self, qsm, t, sample, treg, areg, print_state)
            if print_state and t != len(quantized_audio)-1:
                print(' + ', end='')
        if print_state:
            print()  
        return qsm
    
    def measure(self, qc: 'QuantumCircuit', treg_pos: int = 1, areg_pos: int = 0) -> None:
        """Appends Measurements to a QSM audio circuit
        
        From a quantum circuit with registers containing a QSM 
        representation of quantum audio, creates two classical registers with 
        compatible sizes and adds instructions for measuring them.

        Args:
            qc: A quantum circuit containing at least 2 quantum registers.
            treg_pos: Index of the SQPAM ('treg') register in the circuit. 
                Default is 1
            areg_pos: Index of the SQPAM ('areg') register in the circuit. 
                Default is 0
        """

        treg = qc.qregs[treg_pos]
        areg = qc.qregs[areg_pos]
       
        ctreg = ClassicalRegister(treg.size, 'ct')
        careg = ClassicalRegister(areg.size, 'ca')        
        qc.add_register(careg)
        qc.add_register(ctreg)
        
        qc.measure(treg, ctreg)
        qc.measure(areg, careg)
        
    def reconstruct(self, treg_size: int, counts: 'Counts') -> npt.NDArray:
        """Builds a digital Audio from qiskit histogram data.

        Considering the QSM encoding scheme, it uses the histogram data stored 
        in a Counts object (qiskit.result.counts.Counts) to reconstruct an audio
        signal. It uses the bin labels of the histogram, which contains the
        measured quantum states in binary form. It converts the binary pairs to 
        (amplitude, index) pairs, building an Array.
        
        Args:
            treg_size: Size of the 'treg' (time) register.
            counts: Histogram from a qiskit job result (result.get_counts())

        Returns:
            A Digital Audio as a Numpy Array. The signal is in 
            quantized (int) format.
        """
    
        N = 2**treg_size
        audio = np.zeros(N, int)

        for state in counts:
            (t_bits, a_bits) = state.split()
            t = int(t_bits, 2)
            # The BitArray function converts binary words into signed integers,
            # in oposition to the int(a_bit, 2) function.
            a = BitArray(bin=a_bits).int
            audio[t] = a

        return audio


# //////////////////////////////////////////////////////////////////////////////
# ============================ Encoder Selector ================================
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

AnyEncoder = TypeVar('AnyEncoder', QPAM, SQPAM, QSM)

class EncodingScheme():
    def __init__(self):
        self._qa_encoders = {
            "qpam": QPAM, 
            "sqpam": SQPAM,
            "qsm": QSM,
        }
    def get_encoder(self, encoder_name: str) -> AnyEncoder:
        """Returns: encoder class associated with name.
        """
        encoder = self._qa_encoders.get(encoder_name)
        if not encoder:
            raise ValueError(f'"{encoder_name}" is not a valid name. Valid representations are: {list(self._qa_encoders.keys())}')
        return encoder    


# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =========================== Quantum Audio Class ==============================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

class QuantumAudio():
    
    def __init__(self, encoder_name: str):
        
        #Loads the methods from the specified representation
        self.encoder = EncodingScheme().get_encoder(encoder_name)
        self.encoder_name = encoder_name
        #The audio part
        self.input = np.array([])
        self.converted_input = None
        self.output = np.array([])
        
        #Qiskit part
        self.circuit = QuantumCircuit()
        self.treg_size = 0 # qubit size of the time register
        self.areg_size = 0 # qubit size of the amplitude register
        
        self.shots: Optional[int] = None
        self.job = None
        self.result = None
        self.counts = {}
        
    def __repr__(self):
        return self.__class__.__name__
    
    def load_input(self, input_audio: npt.NDArray[np.floating], bit_depth: int = 1) -> 'QuantumAudio':
        """Loads an audio file and calculates the qubit requirements.

        Brings a digital audio signal inside the class for further processing.
        Audio files should be in numpy.ndarray type and be in the (-1. to 1.)
        amplitude range. You can also optionally load a quantized audio signal 
        as input (-N to N-1) range, as long as you specify the bit depth of your
        quantized input 'areg_size'

        Args:
            input_audio: The audio signal to be converted. If not in 32-bit or 
                64-bit float format ('n'-bit integer PCM), specify bit depth.
            bit_depth: Audio bit depth IF using integer PCM. Ignore otherwise.

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.

        Examples:
            >>> float_audio = [0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25]
            >>> quantum_audio = qa.QuantumAudio('qpam').load_input(float_audio)
            For this input, the QPAM representation will require:
                    3 qubits for encoding time information and 
                    0 qubits for encoding ampĺitude information.
            
            >>> int_3bit_PCM_audio = [0, -1, 2, 3, -3, -4, 1]
            >>> quantum_audio = qa.QuantumAudio('qsm').load_input(int_3bit_PCM_audio, 3)
            For this input, the QSM representation will require:
                    3 qubits for encoding time information and 
                    3 qubits for encoding ampĺitude information.
        """

        self.treg_size = 1
        if len(input_audio)>1:
            self.treg_size = int(np.ceil(np.log2(len(input_audio))))
        
        if self.encoder_name == 'qpam':
            self.areg_size = 0
        elif self.encoder_name == 'sqpam':
            self.areg_size = 1
        else:
            self.areg_size = bit_depth       

        # Zero Padding
        zp = np.zeros(2**self.treg_size - len(input_audio))
        self.input = np.concatenate((input_audio, zp))
        
        if self.encoder_name =='qsm':
            self.input = self.input.astype(int)
        else:
            self.input = self.input.astype(float)/float(2**(bit_depth-1))
        
        print(f"For this input, the {self.encoder.__name__} representation will require:\n         {self.treg_size} qubits for encoding time information and \n         {self.areg_size} qubits for encoding ampĺitude information.")
        return self
        
    def _convert(self) -> 'QuantumAudio':
        """Pre-processing step for circuit preparation.
        
        Depends on the encoder. Loads the 'converted_input' attribute.

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.
        """
        self.converted_input = self.encoder.convert(self, self.input)
        return self
    
    def prepare(self, tregname: str = 't', aregname: str = 'a', print_state: bool = False) -> 'QuantumAudio':
        """Creates a Quantum Circuit that prepares the audio representation.
        
        Loads the 'circuit' attribute with the preparation circuit, according
        to the encoding technique used: QPAM, SQPAM or QSM.

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.
        """
        self._convert()
        self.circuit = self.encoder.prepare(self.encoder, self.converted_input, (self.treg_size, self.areg_size), (tregname, aregname), print_state)
        return self
    
    def measure(self, treg_pos: Optional[int] = None, areg_pos: Optional[int] = None) -> 'QuantumAudio':
        """Updates quantum circuit by adding measurements in the end.

        Will add a measurement instruction to the end of each qubit register.

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.
        """
        additional_args = []
        if treg_pos is not None:
            additional_args += [treg_pos]
        if areg_pos is not None:
            additional_args += [areg_pos]
        self.encoder.measure(self, self.circuit, *additional_args)
        return self
            
    def run(self, shots: int = 10, backend_name: str = 'aer_simulator', provider=AerProvider()) -> 'QuantumAudio':        
        """ Runs the Quantum Circuit in an IBMQ job.

        Transpiles and runs QuantumAudio.circuit in a qiskit job. Supports IBMQ
        remote backends.

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.
        """
        self.shots = shots
        backend = provider.get_backend(backend_name)
        
        if backend_name != 'aer_simulator':
            circuit = transpile(self.circuit, backend=backend, optimization_level=3)
            
        else:
            circuit = self.circuit
            
        job = execute(circuit, backend, shots=shots)
        if backend_name != 'aer_simulator':
            job_monitor(job)
        self.result = job.result()
        self.counts = job.result().get_counts()
        return self
    
    def reconstruct_audio(self, **additional_kwargs: Any) -> 'QuantumAudio':
        """Builds an audio signal from a qiskit result histogram.

        Depending on the chosen encoding technique, reconstructs an audio file
        using the histogram in QuantumAudio.counts (qiskit.result.Counts)

        Returns:
            Returns itself for using multiple QuantumAudio methods in one line
            of code.
        """
        additional_args = []
        
        if self.encoder_name == 'qpam' or self.encoder_name == 'sqpam':
            additional_args += [self.shots]        

        self.output = self.encoder.reconstruct(self, self.treg_size, self.counts, *additional_args, **additional_kwargs)
        return self
        
    def plot_audio(self) -> None:
        """Plots comparisons between the input and output audio files.

        Uses matplotlib.
        """
        plt.figure(figsize=(20, 3))
        plt.plot(np.zeros(2**self.treg_size), '-k', ms=0.1)
        plt.plot(self.input)
        #plt.axis('off')
        plt.title('input')
        plt.show()
        plt.close()
        
        plt.figure(figsize=(20, 3))
        plt.plot(np.zeros(2**self.treg_size), '-k', ms=0.1)
        plt.plot(self.output, 'r')
        #plt.axis('off')
        plt.title('output')
        plt.show()
    
    def listen(self, rate: int = 44100) -> None:
        """Plays the audio file using ipython.display.Audio()
        """
        display(Audio(self.output, rate=rate))


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# =========================== Utilitary Functions ==============================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def requantize_input(audio: npt.NDArray, bit_depth: int) -> npt.NDArray:
    """Requantizes Array signals and PCM audio signals.

    Utilitary Function for downsizing the bit depth of an audio file.
    Very useful for using with the QSM encoder 'QuantumAudio('qsm')'.

    Returns:
        (Numpy Array) Requantized audio signal.
    """
    Q = 2**bit_depth-1
    
    eps = 1e-16
    audio_shifted = ((audio+eps+1)/2)

    audio_quantized_norm = (np.rint((Q-1)*audio_shifted+1)-1)/(Q-1)
    
    audio_quantized = audio_quantized_norm*2-1

    return audio_quantized
