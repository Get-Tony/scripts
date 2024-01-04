"""Clean venvs - Find and optionally remove Python Virtual Environment folders on Windows and Linux systems."""
# Requires Python 3.5+
# Usage: python clean_venvs.py
# Author: Get-Tony@outlook.com
# Created: 2024-01-04
# Updated: 2024-01-04
# License: MIT

import os
import shutil
import concurrent.futures
import argparse


def is_virtual_env(path):
    """
    Check if a given path contains a Python virtual environment.
    Compatible with both Windows and Linux environments.
    """
    windows_dirs = ["Lib", "Scripts"]
    linux_dirs = ["bin", "lib", "lib64"]
    required_files = ["pyvenv.cfg"]
    is_windows_env = all(os.path.exists(os.path.join(path, d)) for d in windows_dirs)
    is_linux_env = all(os.path.exists(os.path.join(path, d)) for d in linux_dirs)
    has_cfg = any(os.path.exists(os.path.join(path, f)) for f in required_files)

    return (is_windows_env or is_linux_env) and has_cfg


def find_virtual_envs(start_path):
    """
    Recursively search for Python virtual environments starting from a given path.
    Uses multithreading to speed up the search process.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(is_virtual_env, os.path.join(root, d)): os.path.join(
                root, d
            )
            for root, dirs, _ in os.walk(start_path)
            for d in dirs
        }

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                yield futures[future]


def get_user_selection(virtual_envs):
    """
    Prompt the user to select virtual environments to delete.
    """
    while True:
        print(
            "\nSelect the indices of virtual environments to delete (comma-separated), or 'exit' to quit:"
        )
        for i, env in enumerate(virtual_envs, start=1):
            print(f"{i}. {env}")

        selection = input("Enter selection: ").strip()
        if selection.lower() == "exit":
            return None

        selected_indices = selection.split(",")
        try:
            selected_indices = [int(index.strip()) - 1 for index in selected_indices]
            return [virtual_envs[i] for i in selected_indices]
        except (ValueError, IndexError):
            print("Invalid selection, please try again.")


def confirm_deletion(selected_envs):
    """
    Confirm deletion with the user.
    """
    while True:
        print("\nSelected virtual environments for deletion:")
        for env in selected_envs:
            print(env)
        confirmation = input(
            "Type 'delete' to confirm, 'change' to modify selection, or 'exit' to cancel: "
        ).lower()
        if confirmation in ["delete", "change", "exit"]:
            return confirmation
        else:
            print("Invalid input, please try again.")


def delete_virtual_envs(envs_to_delete):
    """
    Delete the specified virtual environments.
    """
    for env in envs_to_delete:
        # Ensure that the path is a real directory and not a symbolic link
        if os.path.isdir(env) and not os.path.islink(env):
            try:
                shutil.rmtree(env)
                print(f"Deleted: {env}")
            except Exception as e:
                print(f"Failed to delete {env}: {e}")
        else:
            print(f"Skipped (not a real directory): {env}")


def main(start_path):
    virtual_envs = list(find_virtual_envs(start_path))

    if virtual_envs:
        print("Found Python virtual environments:")
        selected_envs = get_user_selection(virtual_envs)

        while selected_envs is not None:
            confirmation = confirm_deletion(selected_envs)
            if confirmation == "delete":
                print("Deleting selected virtual environments...")
                delete_virtual_envs(selected_envs)
                break
            elif confirmation == "change":
                selected_envs = get_user_selection(virtual_envs)
            else:  # 'exit'
                break
    else:
        print("No Python virtual environments found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find and remove Python Virtual Environment folders."
    )
    parser.add_argument(
        "--path",
        "-p",
        nargs="?",  # optional argument
        default=".",
        help="Path to search for virtual environments (default: current directory)",
    )
    args = parser.parse_args()
    main(args.path)
