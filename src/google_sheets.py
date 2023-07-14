import os

from googleapiclient.discovery import build

from googleapiclient.http import MediaFileUpload

from google.oauth2 import service_account




# Set the path to your JSON credentials file
def upload_excel(path):
    credentials_file = '/Users/gaurav.gupta2/Downloads/spotbot-390605-8e51a76187fa.json'




    # Set the path to your Excel file

    excel_file_path = path




    # Set the name of the Google Drive folder

    folder_name = 'SpotBot'




    # Load credentials from JSON file

    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=[ 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'])




    # Create Google Drive and Google Sheets service clients

    drive_service = build('drive', 'v3', credentials=credentials)

    sheets_service = build('sheets', 'v4', credentials=credentials)




    # Specify the file details

    folder_name = 'SpotBot'  # Name of the folder where the file will be uploaded

    file_path = excel_file_path  # Path to the Excel file on your local machine

    file_name = os.path.basename(file_path)




    # Create the file metadata

    file_metadata = {

        'name': file_name,

        'parents': [drive_service.files().list(q=f"name='{folder_name}'").execute()['files'][0]['id']],

        'mimeType': 'application/vnd.google-apps.spreadsheet'

    }




    # Upload the file to Google Drive

    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)

    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

    # print(uploaded_file)




    # Get the link to the converted Google Sheet

    web_content_link = uploaded_file.get('webViewLink')




    # print('Excel file uploaded and converted to a Google Sheet successfully!')

    return web_content_link


