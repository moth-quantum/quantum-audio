## Migration Guidelines

### From Quantum Audio Version v0.0.2 to v0.1.0

### 1. Loading a scheme

**v0.0.2**
  ```python
  import quantumaudio
  qpam = quantumaudio.QuantumAudio('qpam') #returns a QuantumAudio Instance with QPAM scheme
  ```

**v0.1.0**
  ```python
  import quantumaudio
  qpam = quantumaudio.load_scheme('qpam') #returns a Scheme Class
  ```
  or
  
  ```python
  from quantumaudio import schemes
  qpam = schemes.QPAM()
  ```

### 2. Encoding a Digital Audio Array into Quantum Circuit

**v0.0.2**
  ```python
  qpam.load_input(digital_audio)
  qpam.prepare()
  qpam.measure()
  
  circuit = qpam.circuit
  ```

**v0.1.0**
  ```python
  circuit = qpam.encode(digital_audio)
  ```
  or
  ```python
  circuit = qpam.encode(digital_audio, measure=False) # Return circuit without measurement
  ```
For manually implementing each step of the ```encode()``` operation, please check [Documentation]()
