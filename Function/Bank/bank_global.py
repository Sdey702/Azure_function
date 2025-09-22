import base64
import ftplib
import logging
import uuid
import io
import subprocess
from datetime import datetime
from azure.storage.blob import BlobClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from ftplib import FTP

# Configure logging for better visibility of the process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def decode_and_upload_to_ftp(base64_string: str,
                            bank_name: str,
                            blob_storage_conn_str: str,
                            blob_container_name: str,
                            key_vault_uri: str,
                            pgp_secret_name: str,
                            pass_phrase: str,
                            ftp_host: str,
                            ftp_user: str,
                            ftp_password: str,
                            remote_path: str) -> str:

    """
    Decodes a Base64-encoded CSV file, temporarily stores it in Azure Blob Storage,
    and then uploads it to an FTP server.

    Args:
        base64_string: The Base64-encoded content of the CSV file.
        ftp_host: The hostname or IP address of the FTP server.
        ftp_user: The username for FTP authentication.
        ftp_password: The password for FTP authentication.
        remote_path: The full path on the FTP server where the file will be saved.
        blob_storage_conn_str: The connection string for the Azure Storage account.
        blob_container_name: The name of the blob container to use for temporary storage.
    """

    # get blob stroage details


    # Create a unique temporary blob name with a timestamp and a UUID
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    temp_blob_name = f"{bank_name}_temp_upload_{timestamp}_{uuid.uuid4()}.csv"
    
    # Create a BlobClient for the temporary blob
    try:
        blob_client = BlobClient.from_connection_string(
            conn_str=blob_storage_conn_str,
            container_name=blob_container_name,
            blob_name=temp_blob_name
        )
        logging.info(f"Blob client created for: {temp_blob_name}")
    except Exception as e:
        logging.error(f"Failed to create blob client. Check your connection string and container name. Details: {e}")
        return str(e)

    try:
        # Step 1: Decode the Base64 string.
        logging.info("Attempting to decode Base64 string...")
        decoded_bytes = base64.b64decode(base64_string.encode('utf-8'))
        

        # Step 2: Write the decoded data to a temporary blob.
        logging.info(f"Uploading decoded content to temporary blob '{temp_blob_name}'...")
        blob_client.upload_blob(decoded_bytes, overwrite=True)
        logging.info(f"Successfully uploaded decoded content to blob.")


        # Step 3: Retrieve the PGP private key from Azure Key Vault.
        logging.info("Retrieving PGP private key from Azure Key Vault...")
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
        # Retrieve and decode
        private_key_b64 = secret_client.get_secret(pgp_secret_name).value
        private_key = base64.b64decode(private_key_b64).decode("utf-8")

        # logging.warning(f"Private Key -> '{private_key}'")

        # Step 4: Decrypt the data using the retrieved PGP key.

        # import the key
        import_proc = subprocess.run(
            ["gpg", "--batch", "--yes", "--import"],
            input=private_key.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # import_error = import_proc.stderr.decode()
        # logging.error(f"import_error -> '{import_error}'")

        # Run gpg with passphrase
        proc = subprocess.run(
            [
                "gpg",
                "--batch", "--yes",              # non-interactive
                "--passphrase", pass_phrase,      # supply passphrase
                "--pinentry-mode", "loopback",   # required for --passphrase to work
                "--decrypt"
            ],
            input=decoded_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Get the decrypted output
        decrypted_text = proc.stdout.decode("utf-8")
        error_text = proc.stderr.decode("utf-8")

        if not decrypted_text:
            logging.error(f"decrypted data -> '{error_text}'")
            raise error_text

        

        # Step 5: Connect to FTP server and upload the blob content.
        csv_stream = io.BytesIO(decrypted_text.encode("utf-8"))
        logging.info(f"Connecting to FTP server at {ftp_host}...")
        with ftplib.FTP(ftp_host) as ftp:
            ftp.login(user=ftp_user, passwd=ftp_password)
            logging.info("Successfully logged into FTP.")
            
            # currently not suported so we created this 
            ftp.set_pasv(True)   # enable passive mode (default)
            ftp.af = 'AF_INET'   # force IPv4 (avoid EPSV)


             # 5. Upload the CSV directly
            Temp = f"STOR {remote_path}/{temp_blob_name}"
            logging.info(f"ftp path -> '{Temp}'")

            ftp.storbinary(Temp, csv_stream)
            
            # logging.info(f"Uploading file to {remote_path}...")
        logging.info(f"File uploaded successfully to '{remote_path}'.")


        return f"File uploaded successfully to {remote_path}"



    except base64.binascii.Error as e:
        logging.error(f"Failed to decode Base64 string. Invalid format. Details: {e}")
        raise Exception(str(e))
    except ftplib.all_errors as e:
        logging.error(f"FTP error occurred: {e}")
        raise Exception(str(e))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise Exception(str(e))
    # finally:
    #     # Step 4: Clean up the temporary blob.
    #     try:
    #         logging.info(f"Deleting temporary blob '{temp_blob_name}'...")
    #         blob_client.delete_blob()
    #         logging.info(f"Temporary blob has been cleaned up.")
    #     except Exception as e:
    #         logging.warning(f"Could not delete temporary blob. Manual cleanup may be required. Details: {e}")


