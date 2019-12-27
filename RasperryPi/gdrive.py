import subprocess


def sync(record=None):
    if record is not None:
        record.write_log("INFO: start Google Drive connection")
    
    subprocess.call(["../GoogleDrive/connect_to_gdrive.sh"])

    if record is not None:
        record.write_log("INFO: Google Drive connection done, start synchronization")
    
    subprocess.call(["../GoogleDrive/sync_with_gdrive.sh"])

    if record is not None:
        record.write_log("INFO: Google Drive synchronization done")

if __name__ == "__main__":
    sync()
