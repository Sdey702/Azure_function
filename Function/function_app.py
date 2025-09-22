import azure.functions as func
import logging
import json
import os
from Bank.bank_global import decode_and_upload_to_ftp


"""
  We are getting POST request then we are checking reqquest method and request have reques
  body or not and also check body have bankname and file if not we raise the exception
  if everything present we call decode_and_upload_to_ftp function and extartact requerd 
  id and login detais from environment variable and call the above function.

  the function will decod and decript the file and send the file to blob stroage and 
  craete new file inside ftp location with decript file values

"""


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# We are only consider POST Menthod
@app.route(route="http_trigger",methods=['POST'])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:


    logging.info('Python HTTP trigger function processed a request.')
    
    # My Code Start
    
    # # Check for query string parameters
    # if req.params:
    #     logging.warning("Received a request with query parameters. Sending an error.")

    #     # 1. Create response
    #     response_data = {
    #         "message" : "Query parameters are not allowed. Please remove them and try again."
    #     }
    #     # 2. Serialize the dictionary to a JSON string
    #     json_response_body = json.dumps(response_data)

    #     # 3. Return an HttpResponse with the JSON string and correct content type
    #     return func.HttpResponse(
    #         body=json_response_body,
    #         mimetype="application/json",
    #         status_code=400  # Bad Request
    #     )
       

     # If no query parameters, proceed to handle the request body and body schould be json
    try:
        req_body = req.get_json()

        # Get Bank Name
        bank_name = req_body.get('BankName')
        base64_file = req_body.get('File')

        if bank_name == None:
            raise ValueError("We are not able to fetch bank name please check")
        elif base64_file == None:
            raise ValueError("We are not able to fetch file please check")
        
        # We have Bank Name and File

        # Extracting Blob strogr details
        blob_storage_conn_str = os.environ.get("MY_STORAGE")
        blob_container_name = os.environ.get("MY_CONTAINER")

        # Extracting Key Vault details
        key_vault_uri = os.environ.get("KEY_VAULT_URL")
        pgp_secret_name = os.environ.get("SERECT_NAME")
        pass_phrase = os.environ.get("PASSPHRASE")
        
        # Extracting FTP details
        ftp_host =  os.environ.get("FTP_HOST")
        ftp_user = os.environ.get("FTP_USER")
        ftp_password = os.environ.get("FTP_PASSWORD")
        remote_path = os.environ.get("FTP_PATH")
        

        try:
            return_str = decode_and_upload_to_ftp(base64_file,bank_name,blob_storage_conn_str,blob_container_name,key_vault_uri,pgp_secret_name,pass_phrase,ftp_host,ftp_user,ftp_password,remote_path)
            
            
            # 1. Create a Python dictionary
            response_data = {
                "message":return_str
            }

            # 2. Serialize the dictionary to a JSON string
            json_response_body = json.dumps(response_data)

            # 3-6. Return an HttpResponse with the JSON string and correct content type
            return func.HttpResponse(
                body=json_response_body,
                mimetype="application/json",
                status_code=200
            )


        
        except Exception as e:
                logging.info(e)
                error = str(e)
                # 1. Create response
                response_data = {
                    "message" : f"Enternal server error {error}"
                }
                # 2. Serialize the dictionary to a JSON string
                json_response_body = json.dumps(response_data)

                # 3. Return an HttpResponse with the JSON string and correct content type
                return func.HttpResponse(
                    body=json_response_body,
                    mimetype="application/json",
                    status_code=500  # Bad Request
                )
 
        



    except ValueError as e:
        
        logging.info(e)
        error = str(e)
        # 1. Create response
        response_data = {
            "message" : f"Enternal server error {error}"
        }
        # 2. Serialize the dictionary to a JSON string
        json_response_body = json.dumps(response_data)

        # 3. Return an HttpResponse with the JSON string and correct content type
        return func.HttpResponse(
            body=json_response_body,
            mimetype="application/json",
            status_code=400  # Bad Request
        )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        # 1. Create response
        error = str(e)
        # 1. Create response
        response_data = {
            "message" : f"Enternal server error {error}"
        }
        # 2. Serialize the dictionary to a JSON string
        json_response_body = json.dumps(response_data)

        # 3. Return an HttpResponse with the JSON string and correct content type
        return func.HttpResponse(
            body=json_response_body,
            mimetype="application/json",
            status_code=500  # Bad Request
        )
    


    # Code End
