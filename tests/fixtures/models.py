DEFAULT_CHANNELS = {
    'main': {
        'channel': 'https://repo.anaconda.com/pkgs/main/',
        'platforms': ['linux-64', 'osx-64', 'win-64', 'noarch']
    },
    'msys2': {
        'channel': 'https://repo.anaconda.com/pkgs/msys2',
        'platforms': ['win-64', 'noarch']
    },
    'r': {
        'channel': 'https://repo.anaconda.com/pkgs/r',
        'platforms': ['linux-64', 'osx-64', 'win-64', 'noarch']
    },
    'ae5-admin': {
        'channel': 'https://conda.anaconda.org/ae5-admin',
        'platforms': ['linux-64', 'noarch']
    }
}

TEST_LINUX_YAML = [
    'channels:\n',
    '- https://conda.anaconda.org/ae5-admin\n',
    'check_md5: true\n',
    'fetch_installers: false\n',
    'mirror_dir: ./mirrors/ae5-admin-linux-64\n',
    'platforms: linux-64\n',
    'verbose: 2\n'
]

TEST_NOARCH_YAML = [
    'channels:\n',
    '- https://conda.anaconda.org/ae5-admin\n',
    'check_md5: true\n',
    'fetch_installers: false\n',
    'mirror_dir: ./mirrors/ae5-admin-noarch\n',
    'platforms: noarch\n',
    'verbose: 2\n'
]
