#!/bin/bash

# This script helps enable unprivileged user namespaces, which are required for bwrap
# (Bubblewrap) to function correctly for code execution sandboxing on Linux systems.

echo "Checking current status of kernel.unprivileged_userns_clone..."
CURRENT_VALUE=$(sysctl -n kernel.unprivileged_userns_clone 2>/dev/null)

if [ "$CURRENT_VALUE" == "1" ]; then
    echo "kernel.unprivileged_userns_clone is already enabled (value: 1)."
    echo "bwrap should be able to create user namespaces."
elif [ "$CURRENT_VALUE" == "0" ]; then
    echo "kernel.unprivileged_userns_clone is currently disabled (value: 0)."
    echo "bwrap will likely fail with 'Permission denied' errors when setting up uid map."
    echo ""
    echo "Do you want to enable it?"
    select yn in "Yes, temporarily (until reboot)" "Yes, permanently (modifies /etc/sysctl.conf)" "No"; do
        case $yn in
            "Yes, temporarily (until reboot)" )
                echo "Attempting to enable temporarily..."
                sudo sysctl -w kernel.unprivileged_userns_clone=1
                if [ $? -eq 0 ]; then
                    echo "Successfully enabled kernel.unprivileged_userns_clone temporarily."
                    echo "Please note: This change will revert after a system reboot."
                else
                    echo "Failed to enable kernel.unprivileged_userns_clone temporarily. Sudo privileges might be required."
                fi
                break;;
            "Yes, permanently (modifies /etc/sysctl.conf)" )
                echo "Attempting to enable permanently by modifying /etc/sysctl.conf..."
                if [ -w "/etc/sysctl.conf" ]; then
                    if grep -q "^kernel.unprivileged_userns_clone=" "/etc/sysctl.conf"; then
                        sudo sed -i 's/^kernel.unprivileged_userns_clone=.*/kernel.unprivileged_userns_clone=1/' "/etc/sysctl.conf"
                        echo "Updated kernel.unprivileged_userns_clone in /etc/sysctl.conf."
                    else
                        echo "kernel.unprivileged_userns_clone=1" | sudo tee -a "/etc/sysctl.conf" > /dev/null
                        echo "Added kernel.unprivileged_userns_clone=1 to /etc/sysctl.conf."
                    fi
                    sudo sysctl -p
                    if [ $? -eq 0 ]; then
                        echo "Successfully applied changes from /etc/sysctl.conf."
                        echo "kernel.unprivileged_userns_clone is now permanently enabled."
                    else
                        echo "Failed to apply changes from /etc/sysctl.conf. Please check manually."
                    fi
                else
                    echo "Error: /etc/sysctl.conf is not writable or sudo privileges are insufficient."
                    echo "Please edit /etc/sysctl.conf manually and add/update: kernel.unprivileged_userns_clone=1"
                    echo "Then run 'sudo sysctl -p' to apply the changes."
                fi
                break;;
            "No" )
                echo "Aborting. kernel.unprivileged_userns_clone remains disabled."
                break;;
            * ) echo "Invalid option. Please choose 1, 2, or 3.";;
        esac
    done
elif [ -z "$CURRENT_VALUE" ]; then
    echo "Could not determine the status of kernel.unprivileged_userns_clone."
    echo "This might happen if 'sysctl' command fails or the kernel parameter is not found."
    echo "If you are on a Linux system, you might need to enable it manually."
    echo "Refer to the documentation for details on how to do this."
else
    echo "Unexpected value for kernel.unprivileged_userns_clone: $CURRENT_VALUE"
    echo "Expected 0 or 1. Please investigate your system configuration."
fi

echo ""
echo "It is recommended to log out and log back in, or reboot your system, for these changes to take full effect."
