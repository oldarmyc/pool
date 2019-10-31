
import pathlib
import urllib
import yaml
import sys
import sh
import re
import os


from repo_mirror import exceptions


class Mirror(object):
    def __init__(self):
        self.mirror_directory = 'mirrors'
        self.snapshot_directory = 'snapshot'
        self.channels = {
            'main': {
                'channel': 'https://repo.anaconda.com/pkgs/main/',
                'platforms': ['linux-64', 'osx-64', 'win-64', 'noarch']
            },
            'msys2': {
                'channel': 'https://repo.anaconda.com/pkgs/msys2',
                'platforms': ['win-64']
            },
            'r': {
                'channel': 'https://repo.anaconda.com/pkgs/r',
                'platforms': ['linux-64', 'osx-64', 'win-64', 'noarch']
            },
            'ae5-admin': {
                'channel': 'https://conda.anaconda.org/ae5-admin',
                'platforms': ['noarch']
            }
        }
        self.setup_dir(self.mirror_directory)
        self.aws_bucket = 'airgap.svc.anaconda.com'

    def setup_dir(self, dir_path):
        if not os.path.exists(dir_path):
            pathlib.Path(dir_path).mkdir(parents=True)

    def validate_url(self, url):
        DOMAIN_FORMAT = re.compile(
            r"(?:^(\w{1,255}):(.{1,255})@|^)"
            r"(?:(?:(?=\S{0,253}(?:$|:))"
            r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
            r"(?:[a-z0-9]{1,63}))))"
            r"(:\d{1,5})?",
            re.IGNORECASE
        )
        SCHEME_FORMAT = re.compile(r"^(http)s?$", re.IGNORECASE)
        valid_url = True

        url = url.strip()
        url_parts = urllib.parse.urlparse(url)
        scheme = url_parts.scheme
        domain = url_parts.netloc

        if not scheme:
            return False

        if not re.fullmatch(SCHEME_FORMAT, scheme):
            return False

        if not domain:
            return False

        if not re.fullmatch(DOMAIN_FORMAT, domain):
            return False

        return valid_url

    def validate_platforms(self, platforms):
        valid_platforms = ['win-64', 'osx-64', 'linux-64']
        for platform in platforms:
            if platform not in valid_platforms:
                return False

        return True

    def add_channel(self, channel_name, channel_url, platforms):
        if self.channels.get(channel_name) is not None:
            return

        if not self.validate_url(channel_url):
            return

        if not self.validate_platforms(platforms):
            return

        self.channels[channel_name.lower()] = {
            'channel': channel_url,
            'platforms': platforms
        }

    def remove_channel(self, channel_name):
        try:
            del self.channels[channel_name]
        except Exception:
            pass

    def build_yaml(self, channel_name):
        base = {
            'fetch_installers': False,
            'check_md5': True,
            'verbose': 2
        }
        channel_info = self.channels.get(channel_name)
        if channel_info is None:
            return

        # Create yaml files for each platform to split them all up
        for platform in channel_info.get('platforms'):
            base['platforms'] = [platform]
            base['channels'] = [channel_info.get('channel')]

            tmp_mirror = f'./{self.mirror_directory}/{channel_name}-{platform}'
            base['mirror_dir'] = tmp_mirror
            self.setup_dir(tmp_mirror)

            with open(
                f'{self.mirror_directory}/{channel_name}-{platform}.yaml', 'w'
            ) as yaml_file:
                yaml.dump(base, yaml_file, default_flow_style=False)

    def run_mirror(self, channel_name):
        cas_sync = sh.Command('cas-sync')
        try:
            cas_sync(
                '--config',
                '-f',
                f'mirrors/{channel_name}.yaml',
                _out=sys.stdout
            )
        except Exception as e:
            raise exceptions.MirrorConfig(
                f'There was an issue setting up the config to mirror: {e}'
            )

        try:
            cas_sync('-f', f'mirrors/{channel_name}.yaml', _fg=True)
        except Exception as e:
            raise exceptions.MirrorRun(
                f'There was an error during package pull for mirror: {e}'
            )
