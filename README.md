# Azure_function



# *************************** Overview ********************************



We Have APIM [Base URL : https://testapimsubhankar.azure-api.net]
         |
        \ /
Aure Function [We have environment Variable set inside that For FTP Host and USER PASS We need to change]
         |
        \ /
After Request come to Azure Function We check the request body preseent or Not
then decode the base64 then upload to blob storage 

then for key vault we extrat private key and use that key for decript the file
then upload the file to FTP location


# ***********************************************************************
