import os
import boto3
from dotenv import load_dotenv
from pathlib import Path
import shutil
import subprocess
import traceback

load_dotenv()

aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')

vid_s3_bucket = os.environ.get('VID_S3_BUCKET')
aud_s3_bucket = os.environ.get('AUD_S3_BUCKET')

def list_s3_files(bucket_name, access_key=aws_access_key, secret_key=aws_secret_key):
    s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key= secret_key)
    
    file_list = []
    myBucket = s3.Bucket(bucket_name)
    for my_bucket_object in myBucket.objects.all():
        file_list.append(my_bucket_object.key)
        print(my_bucket_object.key)
        
    return file_list

def download_aws(aws_filename, local_filename, bucket_name, access_key=aws_access_key, secret_key=aws_secret_key):
    s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    Path("content/vids/").mkdir(parents=True, exist_ok=True)
    Path("content/auds/").mkdir(parents=True, exist_ok=True)

    s3.Bucket(bucket_name).download_file(aws_filename, f"content/vids/{local_filename}")
    print("Download Successful!")
    return True

def upload_aws(local_filename, aws_filename, bucket_name, access_key=aws_access_key, secret_key=aws_secret_key):
    s3 = boto3.client('s3', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    
    s3.upload_file(local_filename, bucket_name, aws_filename)
    print("Upload Successful!")
    return True

def mp4_to_mp3(file_name):
    print("Convert mp4 to mp3: ", file_name)
    mp3_file_name = file_name.split(".")[0] + ".mp3"
    cmd = f"ffmpeg -i content/vids/{file_name} -vn content/auds/{mp3_file_name}"
    os.system(cmd)
    upload_aws(f"content/auds/{mp3_file_name}", mp3_file_name, aud_s3_bucket)

def cleanup_files():
    shutil.rmtree("content/")
    print("File Cleanup Successful!")

if __name__ == '__main__':
    try:
        for file in list_s3_files(vid_s3_bucket):
            aws_filename = file.replace(" ", "_")
            download_aws(file, aws_filename, vid_s3_bucket)
            mp4_to_mp3(aws_filename)
        cleanup_files()
    except:
        traceback.print_exc()
        cleanup_files()