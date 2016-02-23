Setting up an AWS instance (Ubuntu 14.04)

```
sudo apt-get install git
sudo apt-get update
sudo apt-get install python-pip
sudo apt-get install python-dev
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_7.0-28_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1404_7.0-28_amd64.deb
sudo apt-get update
sudo apt-get install cuda-7-0
```

Reboot (using `sudo reboot`), and add this to your `.bashrc`:

```
export CUDA_HOME=/usr/local/cuda-7.0
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64 
 
PATH=${CUDA_HOME}/bin:${PATH} 
export PATH
```

Then run these commands: 
```
sudo pip install --upgrade pip
sudo apt-get install build-essential libffi-dev libssl-dev
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow-0.7.0-py2-none-linux_x86_64.whl

Clone the git repository and then install the requirements after going into the `genre` subdirectory

```
sudo pip install -r requirements.txt
```
