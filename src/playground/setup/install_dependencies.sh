#!/bin/bash

# Function to detect the OS and install Python 3, pip, development headers, python-env, and additional packages
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
            echo "Updating package lists and installing packages on Debian/Ubuntu..."
            apt update
            apt install -y software-properties-common git curl wget apt-utils libc6
            ;;
        fedora)
            echo "Updating package lists and installing packages on Fedora..."
            dnf check-update
            dnf install -y git curl wget
            ;;
        centos|rhel)
            echo "Updating package lists and installing packages on CentOS/RHEL..."
            yum check-update
            yum install -y git curl wget
            ;;
        arch)
            echo "Updating package lists and installing packages on Arch Linux..."
            pacman -Syu --noconfirm git curl wget
            # pacman -Syu already updates package lists and upgrades the system
            ;;
        opensuse|sles)
            echo "Updating package lists and installing packages on openSUSE/SLES..."
            zypper refresh
            zypper install -y git curl wget
            ;;
        alpine)
            echo "Updating package lists and installing packages on Alpine Linux..."
            apk update
            apk add --no-cache git curl wget
            ;;
        *)
            echo "Unsupported or unrecognized distribution: $OS_ID"
            exit 1
            ;;
    esac
}

install_deps
