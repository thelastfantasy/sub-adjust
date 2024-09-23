#!/bin/sh

echo "Checking for Python 3 installation..."

if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Attempting to install it..."
    if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update
        sudo apt-get install python3 -y
    elif [ -x "$(command -v yum)" ]; then
        sudo yum install python3 -y
    else
        echo "Package manager not supported. Please install Python 3 manually."
        exit 1
    fi
fi

echo "Python 3 is installed."
echo "Running adjust-timestamp.py..."
nohup python3 adjust-timestamp.py &> /dev/null &
