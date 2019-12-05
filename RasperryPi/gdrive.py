import subprocess


def sync():
    subprocess.call(["../GoogleDrive/connect_to_gdrive.sh"])
    subprocess.call(["../GoogleDrive/sync_with_gdrive.sh"])


if __name__ == "__main__":
    sync()
