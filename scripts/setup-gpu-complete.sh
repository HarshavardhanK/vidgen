#!/usr/bin/env bash
set -euo pipefail

install_nvidia_drivers() {
    
    if nvidia-smi >/dev/null 2>&1; then
        echo "NVIDIA drivers already installed"
        return
    fi
    
    sudo apt update
    sudo ubuntu-drivers install --gpgpu nvidia:550-server
    
    echo "NVIDIA drivers installed. Please reboot and run this script again."
    exit 0
}

install_container_toolkit() {
    if dpkg -l | grep nvidia-container-toolkit >/dev/null 2>&1; then
        echo "NVIDIA container toolkit already installed"
        return
    fi
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt update
    sudo apt install -y nvidia-container-toolkit
    echo "NVIDIA container toolkit installed"
}

install_nvidia_drivers
install_container_toolkit

echo "GPU setup complete. K3s will auto-detect NVIDIA runtime."
