#!/usr/bin/env bash
set -euo pipefail

EXTERNAL_IP=$(curl -s ifconfig.me || true)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--bind-address=0.0.0.0 --node-external-ip=${EXTERNAL_IP:-} --write-kubeconfig-mode=644" sh -

sleep 10

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

kubectl wait --for=condition=ready node --all --timeout=60s

echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc
