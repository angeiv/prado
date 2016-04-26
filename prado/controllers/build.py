import os
import tempfile

from shutil import copyfile

from pecan import expose, response, conf, abort
from pecan.secure import secure
from webob.static import FileIter
from prado.util import render, tar_czf
from prado.auth import basic_auth


class BuildController(object):

    def __init__(self, name):
        self.name = name

    @secure(basic_auth)
    @expose(content_type='application/octet-stream')
    def index(self, **kw):
        try:
            conf.build_map[self.name]
        except (AttributeError, KeyError):
            abort(404)

        playbook = conf.build_map[self.name]['playbook']
        playbook_path = conf.build_map[self.name]['playbook_path']

        files_to_compress = []
        tmp_dir = tempfile.mkdtemp()
        yml_file = os.path.join(tmp_dir, 'main.yml')
        copyfile(playbook, yml_file)
        files_to_compress.append(playbook_path)
        files_to_compress.append(yml_file)

        playbook = tar_czf(files_to_compress)

        response.headers['Content-Disposition'] = 'attachment; filename=playbook.tar.gz'
        f = open(playbook, 'rb')
        response.app_iter = FileIter(f)


class BuildsController(object):

    @expose()
    def _lookup(self, name, *remainder):
        return BuildController(name), remainder
