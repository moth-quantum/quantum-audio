env_name="qa"
source ~/miniconda3/bin/activate
conda create --name $env_name python=3.10 -y

conda activate $env_name
pip install -r requirements.txt