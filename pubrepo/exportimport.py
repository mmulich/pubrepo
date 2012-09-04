# -*- coding: utf-8 -*-
try:
    # NOTE io.StringIO does not work with ZipFile in Python <= 2.7.
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from zipfile import ZipFile


_marker = object()

def export_module(module, zip_file=_marker):
    """Export the given module and its resources to a new Zip file. Or if a
    zipfile.ZipFile object is supplied to the zip_file argument, it will
    be used to append the file to this zip.
    """
    stream = StringIO()
    # TODO Export resources...
    # TODO Handle the case where a zip_file is given.
    with ZipFile(stream, 'w') as zipfile:
        zipfile.writestr("{0}.html".format(module.id), module.content)
        for resource in module.resources:
            zipfile.writestr("resources/{0}".format(resource.filename),
                             resource.data)
    stream.seek(0)
    return stream
