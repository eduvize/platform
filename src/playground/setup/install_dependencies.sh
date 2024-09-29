#!/bin/bash

# Function to detect the OS and install Python 3.11, pip, development headers, python-env, and additional packages
install_deps() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
        OS_NAME=$NAME
    else
        echo "Cannot detect the OS distribution."
        exit 1
    fi

    echo "Detected OS: $OS_NAME"

    case "$OS_ID" in
        ubuntu|debian)
            echo "Updating package lists and installing Python 3.11 on Debian/Ubuntu..."
            export DEBIAN_FRONTEND=noninteractive
            apt update
            apt install -y software-properties-common git curl wget apt-utils
            add-apt-repository -y ppa:deadsnakes/ppa
            apt update
            apt install -y python3.11 python3.11-dev python3.11-venv python3-pip
            ;;
        fedora)
            echo "Updating package lists and installing Python 3.11 on Fedora..."
            dnf check-update
            dnf install -y git curl wget python3.11 python3.11-devel python3-pip
            ;;
        centos|rhel)
            echo "Updating package lists and installing Python 3.11 on CentOS/RHEL..."
            yum check-update
            yum install -y git curl wget
            yum install -y https://repo.ius.io/ius-release-el$(rpm -E '%{rhel}').rpm
            yum install -y python3.11 python3.11-devel python3-pip
            ;;
        arch)
            echo "Updating package lists and installing Python 3.11 on Arch Linux..."
            pacman -Syu --noconfirm git curl wget python python-pip
            ;;
        opensuse|sles)
            echo "Updating package lists and installing Python 3.11 on openSUSE/SLES..."
            zypper refresh
            zypper install -y git curl wget
            zypper addrepo -f https://download.opensuse.org/repositories/devel:languages:python/openSUSE_Tumbleweed/devel:languages:python.repo
            zypper refresh
            zypper install -y python311 python311-devel python3-pip
            ;;
        alpine)
            echo "Updating package lists and installing Python 3.11 on Alpine Linux..."
            apk update
            apk add --no-cache git curl wget python3.11 python3.11-dev py3-pip
            ;;
        *)
            echo "Unsupported or unrecognized distribution: $OS_ID"
            exit 1
            ;;
    esac
}

install_deps
