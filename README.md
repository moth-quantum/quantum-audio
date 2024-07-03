# Quantum Audio
Quantum Audio is a Python module for building quantum circuits that encode and decode audio signals as quantum states. This is primarily aimed for quantum computing simulators, but it might also run on real quantum hardware. The main objective is to have a readily available tools for using quantum representations of audio in artistic contexts and for studying future Quantum Signal Processing algorithms for audio.

This package provides Quantum Audio Representations of Digital Audio and necessary utilities.

Modules:

- schemes: Quantum Audio Encoding and Decoding Methods

    - QPAM   : Quantum Probability Amplitude Modulation
    - SQPAM  : Single-Qubit Probability Amplitude Modulation
    - MSQPAM : Multi-channel Single-Qubit Probability Amplitude Modulation
    - QSM    : Quantum State Modulation
    - MQSM   : Multi-channel Quantum State Modulation

- utils: Utilary functions for data processing, circuit preparation along
         with plotting and audio playback functions for Jupyter Notebook.

Usage:
    import quantumaudio
    from quantumaudio import schemes, utils


    # Example usages
    original_signal = utils.simulate_data(num_samples=8)
    
    # An instance of a scheme can be created either from schemes
    qpam = schemes.QPAM()

    # Or using quantumaudio
    sqpam = quantumaudio.load_scheme('spqam')

    # Encoding and Decoding
    encoded_circuit = qpam.encode(original_audio)
    decoded_signal = qpam.decode(encoded_circuit,shots=4000)    

    # Compare original vs reconstructed signal
    utils.plot([original_signal,decoded_signal])
"""
