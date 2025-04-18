### Using Virtual Environment for Python:

An environment can be created using **[conda](https://docs.anaconda.com/miniconda/#quick-command-line-install)** (recommended for better management and ease of use) or `venv` (comes with Python).

#### Option 1: Using conda:
Create Environment: ```conda create --name myenv python=3.10``` <br>

To run `pip` and `python` commands, the environment needs to be activated using the following command: <br>


**Activate**:  ```conda activate myenv``` <br>

To exit an environment using the following command: <br>

**Deactivate**: ```conda deactivate```

---

#### Option 2: Using venv:
Create Environment: ```python -m venv myenv``` <br>

To run `pip` and `python` commands, the environment needs to be activated: 
  - Activate in MAC/Linux: ```source myenv/bin/activate``` <br>
  - Activate in Windows:  ```myenv\Scripts\activate```

Deactivate: ```deactivate```

---

### Using Virtual Environment with Notebook:
The environment can be used with notebook using the following steps:

- activate the environment in terminal
- do ```pip install ipykernel```
- do ```python -m ipykernel install --user --name=kernel_name```
- In the top menu bar, go to **Kernel** and choose **Change Kernel**. Select the newly created `kernel_name`.  
