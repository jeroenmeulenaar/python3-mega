# -*- coding: utf-8 -*-
import os
import sys
import unittest
import tempfile

from mega import Mega
from mega.exceptions import MegaIncorrectPasswordExcetion

class TestMega(unittest.TestCase):    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self._email = os.environ.get('MEGAEMAIL')
        self._password = os.environ.get('MEGAPASSWORD')

    def _check_file_exists(self, file_name, files):
        uploaded = False
        for f in files['f']:
            if isinstance(f['a'], dict):
                if f['a'].get('n') == file_name:
                    uploaded = True
        return uploaded

    def _test_upload_file(self, api):
        # Create temp file
        uFile, uFilePath = tempfile.mkstemp()
        os.write(uFile, b"Does it work?")
        os.close(uFile)
        data = api.uploadfile(uFilePath)  # inception
        files = api.get_files()
        
        uFileName = os.path.basename(uFilePath)
        uploaded = self._check_file_exists(uFileName, files)
        self.assertEqual(uploaded, True)
        
        return (uFilePath, data)

    def _test_download_file(self, api, uFilePath, data):
        os.rename(uFilePath, uFilePath + ".org")
    
        files = api.get_files()['f']
        uFileName = os.path.basename(uFilePath)
        relevant_files = [x for x in files if x["t"] == 0 and x["a"]["n"] == uFileName]
        self.assertEqual(len(relevant_files), 1)

        relevant_file = relevant_files[0]
        
        file_id = relevant_file["h"]
        file_key = relevant_file["k"]
        store_path = tempfile.gettempdir()
        api.download_file(file_id=file_id, file_key=file_key, store_path=store_path)  # inception
        files = api.get_files()
        
        uFileName = os.path.basename(uFilePath)
        uploaded = self._check_file_exists(uFileName, files)
        self.assertEqual(uploaded, True)
        
        return uFilePath

    def test_login_fail(self):
        with self.assertRaises(MegaIncorrectPasswordExcetion):
            Mega.from_credentials("valid@email.com", "test");
    
    def test_login_valid(self):
        Mega.from_credentials(self._email, self._password)
    
    def test_upload_file_logged(self):
        api = Mega.from_credentials(self._email, self._password)
        (uFilePath, data) = self._test_upload_file(api)
        self._test_download_file(api, uFilePath, data)
    
    def test_upload_file_ephemeral(self):
        self._test_upload_file(Mega.from_ephemeral())

if __name__ == '__main__':
    unittest.main()
