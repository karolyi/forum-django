import os
import subprocess

from django.utils.encoding import smart_bytes

from pipeline.compilers import CompilerBase
from pipeline.conf import settings


class NodeSassCompiler(CompilerBase):
    output_extension = 'css'

    def match_file(self, filename):
        return filename.endswith(('.scss', '.sass'))

    def compile_file(self, infile, outfile, outdated=False, force=False):
        # We always recompile since the imported files can be changed
        self.verbose = settings.DEBUG
        extra_params = '--output-style compressed'
        if settings.DEBUG:
            output_path = os.path.dirname(outfile)
            extra_params = '--source-map "%s"' % output_path
        command = '{} {} "{}" "{}"'.format(
            getattr(
                settings, 'PIPELINE_NODE_SASS_BINARY',
                '/usr/bin/env node-sass'),
            extra_params,
            infile,
            outfile)
        return self.execute_command(command, cwd=os.path.dirname(infile))

    def execute_command(self, command, content=None, cwd=None):
        """
        Due to node-sass writing to stderr even when rendering CSS
        properly, simply show messages.
        """
        pipe = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        if content:
            content = smart_bytes(content)
        stdout, stderr = pipe.communicate(content)

        if self.verbose and stderr.strip():
            print(stderr)

        return stdout
