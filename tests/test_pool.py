
from unittest import TestCase


import mock
import glob
import os
import sh


from repo_mirror import exceptions
from repo_mirror import mirror
from repo_mirror import pool


import repo_mirror


class TestPool(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        temp_archives = glob.glob('*.tar.gz')
        for item in temp_archives:
            os.remove(item)

        if os.path.exists('mirrors'):
            os.rmdir('mirrors')

    def test_version(self):
        self.assertEqual(
            repo_mirror.__version__,
            '0.1.0',
            'Version expected was not returned correctly'
        )

    @mock.patch('sh.Command')
    def test_upload_file(self, Command):
        test_class = mirror.Mirror()
        test_tarballs = ['test.tar.gz']
        with mock.patch('repo_mirror.pool.transfer.TransferConfig'):
            with mock.patch('repo_mirror.pool.boto3.client'):
                with mock.patch('repo_mirror.pool.boto3.client.upload'):
                    pool.upload_files(test_class, test_tarballs)

    @mock.patch('sh.Command')
    def test_main_success(self, Command):
        test_class = mirror.Mirror()
        Command().side_effect = ['pass']
        with mock.patch('repo_mirror.mirror.Mirror.build_yaml'):
            with mock.patch('repo_mirror.mirror.Mirror.run_mirror'):
                with mock.patch('repo_mirror.pool.upload_files'):
                    pool.main()

        temp_archives = glob.glob('*.tar.gz')
        self.assertEqual(
            len(temp_archives),
            len(test_class.channels),
            'Incorrect number of archives'
        )

    @mock.patch('sh.Command')
    def test_main_error_channel(self, Command):
        test_class = mirror.Mirror()
        Command().side_effect = ['pass']

        raise_exception = mock.Mock()
        raise_exception.side_effect = [
            exceptions.MirrorRun(),
            '',
            '',
            ''
        ]
        with mock.patch('repo_mirror.mirror.Mirror.build_yaml'):
            with mock.patch(
                'repo_mirror.mirror.Mirror.run_mirror',
                side_effect=raise_exception
            ):
                with mock.patch('repo_mirror.pool.upload_files'):
                    pool.main()

        temp_archives = glob.glob('*.tar.gz')
        self.assertEqual(
            len(temp_archives),
            len(test_class.channels) - 1,
            'Incorrect number of archives'
        )
        for item in temp_archives:
            if 'main' in item:
                assert False, 'Main archive should not have succeeded'

    @mock.patch('sh.Command')
    def test_main_error_file_list(self, Command):
        test_class = mirror.Mirror()
        Command().side_effect = [
            sh.ErrorReturnCode_1(
                'tree',
                ''.encode('utf-8'),
                ''.encode('utf-8')
            ),
            'pass',
            'pass',
            'pass'
        ]
        with mock.patch('repo_mirror.mirror.Mirror.build_yaml'):
            with mock.patch('repo_mirror.mirror.Mirror.run_mirror'):
                with mock.patch('repo_mirror.pool.upload_files'):
                    pool.main()

        temp_archives = glob.glob('*.tar.gz')
        self.assertEqual(
            len(temp_archives),
            len(test_class.channels),
            'Incorrect number of archives'
        )

    @mock.patch('sh.Command')
    @mock.patch('sh.tar', create=True)
    def test_main_error_tarball(self, Command, tar):
        Command().side_effect = ['pass']
        Command().side_effect = [
            sh.ErrorReturnCode_1(
                'tar',
                ''.encode('utf-8'),
                ''.encode('utf-8')
            )
        ]
        with mock.patch('repo_mirror.mirror.Mirror.build_yaml'):
            with mock.patch('repo_mirror.mirror.Mirror.run_mirror'):
                with mock.patch('repo_mirror.pool.upload_files'):
                    pool.main()

        temp_archives = glob.glob('*.tar.gz')
        self.assertEqual(
            len(temp_archives),
            0,
            'Incorrect number of archives'
        )
