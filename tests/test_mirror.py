
from unittest import TestCase


import mock
import os
import sh


from repo_mirror import exceptions
from tests.fixtures import models
from repo_mirror import mirror


class TestMirror(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        temp = 'ae5-admin'
        if os.path.isfile(f'mirrors/{temp}.yaml'):
            os.remove(f'mirrors/{temp}.yaml')

        if os.path.exists(f'mirrors/{temp}'):
            os.rmdir(f'mirrors/{temp}')

        if os.path.exists('mirrors'):
            os.rmdir('mirrors')

    def test_init(self):
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.mirror_directory,
            'mirrors',
            'Invalid mirror dir'
        )
        self.assertEqual(
            test_class.snapshot_directory,
            'snapshot',
            'Invalid snapshot directory'
        )
        self.assertEqual(
            test_class.channels,
            models.DEFAULT_CHANNELS,
            'Invalid set of default channels'
        )
        self.assertEqual(
            test_class.aws_bucket,
            'airgap-tarball',
            'Invalid defalut aws bucket'
        )
        if not os.path.exists('mirrors'):
            assert False, 'Mirror directory was not setup properly'

    def test_validate_url_success(self):
        test_url = 'https://conda.anaconda.org/ae5-admin'
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_url(test_url),
            True,
            'Invalid return on URL'
        )

    def test_validate_url_no_scheme(self):
        test_url = 'conda.anaconda.org/ae5-admin'
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_url(test_url),
            False,
            'Invalid return on URL'
        )

    def test_validate_url_bad_scheme(self):
        test_url = 'ftp://conda.anaconda.org/ae5-admin'
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_url(test_url),
            False,
            'Invalid return on URL'
        )

    def test_validate_url_no_domain(self):
        test_url = 'https://'
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_url(test_url),
            False,
            'Invalid return on URL'
        )

    def test_validate_url_bad_domain(self):
        test_url = 'https://conda'
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_url(test_url),
            False,
            'Invalid return on URL'
        )

    def test_validate_platform_success(self):
        test_platforms = ['linux-64']
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_platforms(test_platforms),
            True,
            'Invalid return on platforms'
        )

    def test_validate_platform_fail(self):
        test_platforms = ['linux-64', 'invalid']
        test_class = mirror.Mirror()
        self.assertEqual(
            test_class.validate_platforms(test_platforms),
            False,
            'Invalid return on platforms'
        )

    def test_add_channel_success(self):
        test_name = 'test'
        test_url = 'https://conda.anaconda.org/test'
        test_platforms = ['linux-64', 'win-64']
        test_class = mirror.Mirror()
        test_class.add_channel(test_name, test_url, test_platforms)

        if not test_class.channels.get('test'):
            assert False, 'Could not find added channel'

        test_channel = test_class.channels.get('test')
        self.assertEqual(
            test_channel.get('channel'),
            test_url,
            'URL was not found in channel listing'
        )
        self.assertEqual(
            test_channel.get('platforms'),
            test_platforms,
            'Platforms was not found in channel listing'
        )

    def test_add_channel_duplicate(self):
        test_name = 'ae5-admin'
        test_url = 'https://conda.anaconda.org/test'
        test_platforms = ['linux-64', 'win-64']
        test_class = mirror.Mirror()
        channel_count = len(test_class.channels)
        test_class.add_channel(test_name, test_url, test_platforms)

        self.assertEqual(
            channel_count,
            len(test_class.channels),
            'Channel counts do not match after duplicate channel add'
        )

    def test_add_channel_bad_url(self):
        test_name = 'test'
        test_url = 'ftp://conda.anaconda.org/test'
        test_platforms = ['linux-64', 'win-64']
        test_class = mirror.Mirror()
        test_class.add_channel(test_name, test_url, test_platforms)

        if test_class.channels.get('test'):
            assert False, (
                'Channel was added when it should have failed validation'
            )

    def test_add_channel_bad_platform(self):
        test_name = 'test'
        test_url = 'https://conda.anaconda.org/test'
        test_platforms = ['linux-64', 'win-64', 'invalid']
        test_class = mirror.Mirror()
        test_class.add_channel(test_name, test_url, test_platforms)

        if test_class.channels.get('test'):
            assert False, (
                'Channel was added when it should have failed validation'
            )

    def test_remove_channel(self):
        test_class = mirror.Mirror()
        test_class.remove_channel('msys2')

        if test_class.channels.get('msys2'):
            assert False, (
                'Channel was not removed as expected'
            )

    def test_remove_channel_fail(self):
        test_class = mirror.Mirror()
        channel_count = len(test_class.channels)
        test_class.remove_channel('unknown')

        self.assertEqual(
            channel_count,
            len(test_class.channels),
            'Channel counts do not match after failed channel remove'
        )

    def test_build_yaml_no_channels(self):
        test_channel = 'unknown'
        test_class = mirror.Mirror()
        test_class.build_yaml(test_channel)

        if os.path.isfile('mirrors/unknown.yaml'):
            assert False, 'Created yaml file when should not have'

    def test_build_yaml_success(self):
        test_channel = 'ae5-admin'
        test_class = mirror.Mirror()
        test_class.build_yaml(test_channel)

        if not os.path.isfile(f'mirrors/{test_channel}.yaml'):
            assert False, 'Did not create yaml file as expected'

        if not os.path.isfile(f'mirrors/{test_channel}.yaml'):
            assert False, 'Did not create yaml file as expected'

        if not os.path.exists(f'mirrors/{test_channel}'):
            assert False, 'Channel directory was not created'

        yaml_contents = []
        with open(f'mirrors/{test_channel}.yaml', 'r') as f:
            yaml_contents = f.readlines()

        self.assertEqual(
            yaml_contents,
            models.TEST_YAML,
            'yaml file contents are not expected values'
        )

    @mock.patch('sh.Command')
    def test_run_mirror_success(self, Command):
        Command().side_effect = ['pass', 'pass']
        test_class = mirror.Mirror()
        try:
            test_class.run_mirror('ae5-admin')
        except Exception:
            assert False, 'Exception was thrown and should not have'

    @mock.patch('sh.Command')
    def test_run_mirror_bad_config(self, Command):
        Command().side_effect = [
            sh.ErrorReturnCode_1(
                'cas-sync',
                ''.encode('utf-8'),
                ''.encode('utf-8')
            )
        ]
        test_class = mirror.Mirror()
        try:
            test_class.run_mirror('ae5-admin')
            assert False, 'Exception was not thrown'
        except exceptions.MirrorConfig:
            pass
        except Exception:
            assert False, 'Did not catch proper exception'

    @mock.patch('sh.Command')
    def test_run_mirror_bad_run(self, Command):
        Command().side_effect = [
            'pass',
            sh.ErrorReturnCode_1(
                'cas-sync',
                ''.encode('utf-8'),
                ''.encode('utf-8')
            )
        ]
        test_class = mirror.Mirror()
        try:
            test_class.run_mirror('ae5-admin')
            assert False, 'Exception was not thrown'
        except exceptions.MirrorRun:
            pass
        except Exception:
            assert False, 'Did not catch proper exception'
