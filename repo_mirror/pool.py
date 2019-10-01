
from boto3.s3 import transfer


import boto3
import time
import sh


from repo_mirror.mirror import Mirror


def upload_files(mirror, all_tarballs):
    upload_config = transfer.TransferConfig(
        max_concurrency=10,
        use_threads=True
    )
    s3 = boto3.client('s3')
    for file_name in all_tarballs:
        print(f'Uploading {file_name} to S3')
        s3.upload_file(
            file_name,
            mirror.aws_bucket,
            file_name,
            ExtraArgs={'ACL': 'public-read'},
            Config=upload_config
        )


def main():
    mirror = Mirror()
    successful_tarballs = []

    # Download the packages and setup the channel dirs
    for channel in mirror.channels.keys():
        print(f'Building yaml file for {channel}')
        mirror.build_yaml(channel)
        try:
            print(f'Running mirror for {channel}')
            mirror.run_mirror(channel)
        except Exception:
            print(f'{channel} had an issue running the mirror')
            continue

        try:
            print(f'Generating file list for {channel}')
            tree = sh.Command('tree')
            tree(
                f'{mirror.mirror_directory}/{channel}',
                _out=f'{mirror.mirror_directory}/{channel}/{channel}.txt'
            )
        except Exception:
            print(f'{channel} had an issue getting the file list')
            pass

        try:
            temp_file = f'{channel}_{time.strftime("%Y%m%d")}.tar.gz'
            print(f'Creating tarball for {channel}')
            sh.tar(
                '-czf',
                temp_file,
                '-C',
                f'{mirror.mirror_directory}/',
                channel
            )
            successful_tarballs.append(temp_file)
        except Exception:
            print(f'{channel} failed to generate the repo tarball')
            pass

    print('Starting upload to S3')
    upload_files(mirror, successful_tarballs)


if __name__ == '__main__':
    main()
