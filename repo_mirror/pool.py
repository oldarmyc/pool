
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

    # Run through all of the default channels
    for channel in mirror.channels.keys():
        print(f'Building yaml file for {channel}')
        mirror.build_yaml(channel)
        for platform in mirror.channels[channel]['platforms']:
            temp_channel = f'{channel}-{platform}'
            try:
                print(f'Running mirror for {temp_channel}')
                mirror.run_mirror(temp_channel)
            except Exception:
                print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
                print(f'{temp_channel} had an issue running the mirror')
                continue

            try:
                print(f'Generating file list for {temp_channel}')
                tree = sh.Command('tree')
                tree(
                    f'{mirror.mirror_directory}/{temp_channel}',
                    _out=(
                        f'{mirror.mirror_directory}/{temp_channel}'
                        f'/{temp_channel}.txt'
                    )
                )
            except Exception:
                print(f'{temp_channel} had an issue getting the file list')
                pass

            try:
                temp_file = f'{temp_channel}_{time.strftime("%Y%m%d")}.tar.gz'
                print(f'Creating tarball for {temp_channel}')
                sh.tar(
                    '-czf',
                    temp_file,
                    '-C',
                    f'{mirror.mirror_directory}/',
                    temp_channel
                )
                successful_tarballs.append(temp_file)
            except Exception:
                print(f'{temp_channel} failed to generate the repo tarball')
                pass

    print('Starting upload to S3')
    upload_files(mirror, successful_tarballs)


if __name__ == '__main__':
    main()
