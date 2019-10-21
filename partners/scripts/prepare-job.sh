#!/bin/bash
sudo apt-get update
#sudo apt-get -y upgrade
sudo apt install -y build-essential unzip zip go-dep jq

#Installing go
wget https://dl.google.com/go/go1.13.1.linux-amd64.tar.gz
sudo tar -xvf go1.13.1.linux-amd64.tar.gz
sudo mv go /usr/local

mkdir -p $HOME/go/src/terratest/test
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$GOROOT/bin:$GOPATH/bin:/usr/bin:$PATH
#mv ./devops/quickstart-terraform_test.go $HOME/go/src/terratest/test
cd $HOME/go/src/terratest/test

cat  << EOF > Gopkg.toml
[[constraint]]
  name = "github.com/gruntwork-io/terratest"
  version = "0.19.1"
EOF

dep ensure

#Installing terraform
wget https://releases.hashicorp.com/terraform/0.12.10/terraform_0.12.10_linux_amd64.zip
unzip terraform_0.12.10_linux_amd64.zip
sudo mv terraform /usr/bin

#Installing Packer
export VER="1.4.4"
wget https://releases.hashicorp.com/packer/${VER}/packer_${VER}_linux_amd64.zip
unzip packer_${VER}_linux_amd64.zip
sudo mv packer /usr/bin

rm -rf terraform_0.12.10_linux_amd64.zip packer_${VER}_linux_amd64.zip
