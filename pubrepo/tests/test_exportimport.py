# -*- coding: utf-8 -*-
import os
import tempfile
import unittest
import zipfile
import transaction
from pyramid import testing

from ..models import DBSession


HERE = os.path.abspath(os.path.dirname(__file__))
HTML_CONTENT = """\
<html>
<head><title>Module</title></head>
<body>
  <h1>Module</h1>
  <p>A module with text... text... text...</p>
  <p>And an image:</p>
  <!-- see also data/image.png -->
  <img src="image.png">
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
            Resource,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            module = Module(title='Module 1.1', content=HTML_CONTENT)
            DBSession.add(module)
            module = DBSession.query(Module).first()
            image_path = os.path.join(HERE, 'data/image.png')
            resource = Resource('image.png',
                                open(image_path).read(),
                                module)
            DBSession.add(resource)
        # Create the directory where the export can be temporarily
        # stored.
        self.export_path = tempfile.mkdtemp()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def _get_module(self, id=1):
        """Grab the specified module out of the DB"""
        from ..models import Module
        module = DBSession.query(Module).filter_by(id=1).first()
        return module

    def _write_export_to_filesystem(self, stream, filename='export.zip'):
        """Write the export stream to the filesystem."""
        zipfile_path = os.path.join(self.export_path, filename)
        with open(zipfile_path, 'wb') as file:
            file.write(stream.getvalue())
        return zipfile_path

    def test_export_is_a_zip_file(self):
        # Export a specific module and ensure the file is a valid zip
        # file.
        module = self._get_module()
        # By default, the export_module function outputs a bytestream,
        # so we need to push that stream on to the filesystem to read
        # from it more than once.
        from ..exportimport import export_module
        export_stream = export_module(module)
        zipfile_path = self._write_export_to_filesystem(export_stream)

        # Check that the file is a valid .zip.
        self.assertTrue(zipfile.is_zipfile(zipfile_path))

    def test_exporting_a_module_w_resources(self):
        # Export a specific module and its resource(s).
        from ..models import Module
        module = DBSession.query(Module).filter_by(id=1).first()
        # By default, the export_module function outputs a bytestream,
        # so we need to push that stream on to the filesystem to read
        # from it more than once.
        from ..exportimport import export_module
        export_stream = export_module(module)
        zipfile_path = self._write_export_to_filesystem(export_stream)

       # Expand the contents of the zip file.
        with zipfile.ZipFile(zipfile_path) as file:
            file_list = file.namelist()
        self.assertIn("{0}.html".format(module.id), file_list)
        self.assertIn("resources/image.png", file_list)

    def test_exported_module_contents_r_accurate(self):
        # Export a specific module and its resource(s) to the
        # filesystem for detailed inspection.
        from ..models import Module
        module = DBSession.query(Module).filter_by(id=1).first()
        # By default, the export_module function outputs a bytestream,
        # so we need to push that stream on to the filesystem to read
        # from it more than once.
        from ..exportimport import export_module
        export_stream = export_module(module)
        zipfile_path = self._write_export_to_filesystem(export_stream)

        with zipfile.ZipFile(zipfile_path) as file:
            file.extractall(self.export_path)
        # Check resource(s) is present and matches the information we
        # have stored.
        resources = module.resources
