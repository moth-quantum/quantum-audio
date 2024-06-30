from abc import ABC, abstractmethod

class BaseScheme(ABC):
    """
    A Scheme denotes one of the Quantum Audio Representation Methods.
    The core functions of a Scheme is Encoding and Decoding.

    - Encoding: takes in a Digital Audio Array, does necessary
                pre-processing and Prepares a Quantum Circuit. 
                The Quantum Circuit can be used to create a state
                that represents the Original Digital Audio.
    
    - Decoding: takes in the Quantum Circuit measurements,
                does necessary post-processing and reconstructs back
                the original Digital Audio.

    The simplest form of interaction with a Scheme Object is to use 
    scheme.encode() and scheme.decode() methods. However, it
    involves several stages which can be manually implemented. 
    The stages are listed below:

    - calculate         : Calculates the necessary number of qubits
        				   with respect to the data, type of scheme
                          and any user defined values valid for some schemes. 
                        
    - prepare data      : Prepares the data by padding and reshaping.
    
    - convert data      : Converts the data to values suitable for encoding.
    
    - initalize circuit : Initalises circuit with the calculated no. of qubits
        				   for each quantum registers representing a different aspect
                          of the Audio data. e.g. time register, value register etc.
                         
    - value setting     : Encodes / Sets the converted values to the circuit.
    
    - measure(optional) : Measures the circuit with appropriate classical registers.
    
    - encode            : combines all the above steps 

    - execute(optional) : The circuit be executed externally or 
                          internally using aer simulator which is 
                          included in scheme.decode() method by default

    - decode components : First stage of decoding.
    				       Extracts required components directly from the 
                          counts. i.e. a dictionary with the outcome of 
                          measurements performed on the quantum circuit.
                                  
    - restore data       : Second stage of decosing.
                           undo the data conversion done at encoding

    - undo preparation   : Third stage of decoding.
    					   Undo the data preparation such as padding 
                           done at encoding. Can be done manually
                           using numpy slicing and reshape methods.

    - reconstruct data   : Takes in a counts dictionary for decoding.
                              
                           Combines decoding stages 1 and 2.
        
    - decode result      : Takes in a qiskit.result object for decoding. 
                              
                           Combines decoding stages 1, 2 and 3.
                              
                           It considers additional metadata such as 
                           original sample length to undo the padding 
                           done at data preparation stage.

    - decode             : Takes in a qiskit.circuit object for decoding.
                              
                           Performs measurement (if needed) and default
                           execution, followed by all stages of decoding.
    """

    def __init__(self):
        self.name        = 'Quantum Audio Representation Scheme'
        self.qubit_depth = None
        self.n_fold      = None
        self.labels      = None
        self.positions   = None

    @abstractmethod
    def calculate(self):
        pass

    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def convert_data(self):
        pass

    @abstractmethod
    def initalize_circuit(self):
        pass

    @abstractmethod
    def value_setting(self):
        pass

    @abstractmethod
    def measure(self):
        pass

    def encode(self):
        pass

    @abstractmethod
    def decode_components(self):
        pass

    @abstractmethod
    def reconstruct_data(self):
        pass

    @abstractmethod
    def decode_result(self):
        pass

    def decode(self):
        pass