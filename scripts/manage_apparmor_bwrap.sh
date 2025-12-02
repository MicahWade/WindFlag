#!/bin/bash
# This script manages the AppArmor profile for bwrap to allow user namespace creation
# on Ubuntu 23.10+ and 24.04+.

PROFILE_NAME="usr.bin.bwrap"
PROFILE_SOURCE_PATH="./config/apparmor/$PROFILE_NAME"
PROFILE_DEST_PATH="/etc/apparmor.d/$PROFILE_NAME"

function install_profile() {
    echo "Installing AppArmor profile for bwrap..."
    if [ ! -f "$PROFILE_SOURCE_PATH" ]; then
        echo "Error: AppArmor profile source not found at $PROFILE_SOURCE_PATH"
        exit 1
    fi

    if [ ! -d "/etc/apparmor.d" ]; then
        echo "Error: AppArmor directory /etc/apparmor.d not found. Is AppArmor installed?"
        exit 1
    fi

    sudo cp "$PROFILE_SOURCE_PATH" "$PROFILE_DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to copy profile to $PROFILE_DEST_PATH. Do you have sudo privileges?"
        exit 1
    fi
    echo "Profile copied to $PROFILE_DEST_PATH."

    echo "Loading and enforcing AppArmor profile..."
    sudo apparmor_parser -r "$PROFILE_DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to load profile with apparmor_parser. Check profile syntax."
        exit 1
    fi
    sudo aa-enforce "$PROFILE_DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to enforce profile."
        exit 1
    fi
    echo "AppArmor profile for bwrap installed and enforced."
    echo "You can verify its status with: sudo aa-status"
}

function remove_profile() {
    echo "Removing AppArmor profile for bwrap..."
    if [ ! -f "$PROFILE_DEST_PATH" ]; then
        echo "Profile not found at $PROFILE_DEST_PATH. Nothing to remove."
        exit 0
    fi

    echo "Disabling and unloading AppArmor profile..."
    sudo aa-disable "$PROFILE_DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to disable profile. Attempting to remove anyway."
    fi
    sudo rm "$PROFILE_DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to remove profile file. Do you have sudo privileges?"
        exit 1
    fi
    echo "AppArmor profile for bwrap removed."
    echo "You might need to restart AppArmor for changes to fully take effect (e.g., sudo systemctl reload apparmor)."
}

function check_status() {
    echo "Checking AppArmor profile status for bwrap..."
    sudo aa-status | grep "$PROFILE_DEST_PATH"
    if [ $? -eq 0 ]; then
        echo "Profile '$PROFILE_NAME' is active."
    else
        echo "Profile '$PROFILE_NAME' is NOT active."
    fi
    echo ""
    echo "Full AppArmor status:"
    sudo aa-status
}

function main() {
    if [ "$#" -eq 0 ]; then
        echo "Usage: $0 {install|remove|status}"
        exit 1
    fi

    case "$1" in
        install)
            install_profile
            ;;
        remove)
            remove_profile
            ;;
        status)
            check_status
            ;;
        *)
            echo "Invalid command. Usage: $0 {install|remove|status}"
            exit 1
            ;;
    esac
}

main "$@"
