# -*- coding: utf-8 -*-
import os
import tempfile
import unittest
import zipfile
import transaction
from pyramid import testing

from ..models import DBSession


HTML_CONTENT = """\
<html>
<head><title>Module</title></head>
<body>
  <h1>Module</h1>
  <p>A module with text... text... text...</p>
  <p>And an image:</p>
  <img src="">
</body>
</html>
"""


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from ..models import (
            Base,
            Module,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = Module(title='Module 1.1', content=HTML_CONTENT)
            DBSession.add(model)
        # Create the directory where the export can be temporarily
        # stored.
        self.export_path = tempfile.mkdtemp()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_exporting_a_module_w_resources(self):
        # Export a specific module and its resource(s) to the
        # filesystem.
        from ..models import Module
        module = DBSession.query(Module).filter_by(id=1).first()
        # By default, the export_module function outputs a bytestream,
        # so we need to push that stream on to the filesystem to read
        # from it more than once.
        export_filename = 'module_export.zip'
        zipfile_path = os.path.join(self.export_path, export_filename)

        from ..exportimport import export_module
        with open(zipfile_path, 'wb') as file:
            file.write(export_module(module).getvalue())

        # Check that the file is a valid .zip.
        self.assertTrue(zipfile.is_zipfile(zipfile_path))
        # Expand the contents of the zip file.
        with zipfile.ZipFile(zipfile_path) as file:
            file_list = file.namelist()
            file.extractall(self.export_path)
        self.assertIn('{0}.html'.format(module.id), file_list)
        self.assertIn('resources/image.jpg', file_list)
        # Check the html content and resource(s).
