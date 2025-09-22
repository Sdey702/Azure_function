# Azure_function

# 📌 Project Overview

This project integrates **Azure API Management (APIM)**, **Azure Functions**, **Azure Blob Storage**, **Azure Key Vault**, and **FTP** to securely handle file uploads and decryption.  

---

## 🔄 Workflow

1. **API Management (APIM)**  
   - Entry point for incoming requests.  
   - Base URL:  
     ```
     https://testapimsubhankar.azure-api.net
     ```

2. **Azure Function**  
   - Validates the request body.  
   - Decodes the Base64 input data.  
   - Uploads the decoded file to **Blob Storage**.  
   - Fetches the **PGP private key** from **Key Vault**.  
   - Uses the key to **decrypt** the file.  
   - Uploads the decrypted file to the configured **FTP server**.  
   - FTP credentials and host details are provided via **environment variables**.

---

## ⚙️ Configuration

- **Environment Variables** (set in Azure Function App settings):
  - `FTP_HOST`
  - `FTP_USER`
  - `FTP_PASS`

- **Azure Services** used:
  - **API Management** (secure request routing)  
  - **Blob Storage** (temporary file storage)  
  - **Key Vault** (secure key management)  
  - **FTP Server** (final file destination)  

---

## 🚀 Flow Diagram (Conceptual)

```
APIM (https://testapimsubhankar.azure-api.net)
        |
        v
Azure Function
  ├─ Validate Request Body & Decode Base64
  ├─ Upload Decode File to Blob Storage
  ├─ Retrieve Private Key from Key Vault
  ├─ Decrypt File
  └─ Upload to FTP
```
