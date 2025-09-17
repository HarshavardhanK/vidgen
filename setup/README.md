# Setup Scripts

This directory contains installation scripts for the video generation pipeline dependencies.

**System Requirements (Current):**
- NVIDIA-SMI 565.57.01
- Driver Version: 565.57.01
- CUDA Version: 12.7

## Scripts

### docker.sh
Installs Docker and Docker Compose on Ubuntu systems. Run with sudo privileges to set up containerization support.

### nvidia_ctk_runtime.sh
Installs NVIDIA Container Toolkit for GPU acceleration in Docker containers. Requires existing NVIDIA drivers and Docker installation. Run with sudo privileges.

## Usage

Execute scripts in the following order:
1. Run `docker.sh` to install Docker
2. Run `nvidia_ctk_runtime.sh` to enable GPU support in containers

Both scripts require root privileges and should be run from the project root directory.