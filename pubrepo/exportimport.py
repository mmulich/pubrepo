# -*- coding: utf-8 -*-
try:
    # NOTE io.StringIO does not work with ZipFile in Python <= 2.7.
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from zipfile import ZipFile
import lxml.html


_marker = object()

def rewrite_resource_paths(content, base=None):
    """Given the content and a new base reference, rewrite the source paths
    in the content.
    """
    html = lxml.html.fromstring(content)
    def repl(link):
        if link.startswith('#') or link.startswith('//'):
            return link
        if base is not None:
            return "{0}/{1}".format(base.rstrip('/'), link)
        else:
            return link
    html.rewrite_links(repl, resolve_base_href=False)
    return lxml.html.tostring(html)

def export_module(module, zip_file=_marker):
    """Export the given module and its resources to a new Zip file. Or if a
    zipfile.ZipFile object is supplied to the zip_file argument, it will
    be used to append the file to this zip.
    """
    # TODO Handle the case where a zip_file is given.
    content = rewrite_resource_paths(module.content, base='./resources')

    stream = StringIO()
    with ZipFile(stream, 'w') as zipfile:
        zipfile.writestr("{0}.html".format(module.id), content)
        for resource in module.resources:
            zipfile.writestr("resources/{0}".format(resource.filename),
                             resource.data)
    stream.seek(0)
    return stream
