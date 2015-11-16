from __future__ import print_function

import sys
import os
import shutil
import inspect
import getopt
from collections import defaultdict

if __name__ == '__main__':
    # Equivalent of sys.path[0]/../..
    throot = os.path.abspath(
        os.path.join(sys.path[0], os.pardir, os.pardir))

    options = defaultdict(bool)
    opts, args = getopt.getopt(
        sys.argv[1:],
        'o:f:',
        ['rst', 'help', 'nopdf', 'cache', 'test'])
    options.update(dict([x, y or True] for x, y in opts))
    if options['--help']:
        print('Usage: %s [OPTIONS] [files...]' % sys.argv[0])
        print('  -o <dir>: output the html files in the specified dir')
        print('  --cache: use the doctree cache')
        print('  --rst: only compile the doc (requires sphinx)')
        print('  --nopdf: do not produce a PDF file from the doc, only HTML')
        print('  --test: run all the code samples in the documentaton')
        print('  --help: this help')
        print('If one or more files are specified after the options then only '
              'those files will be built. Otherwise the whole tree is '
              'processed. Specifying files will implies --cache.')
        sys.exit(0)

    if options['--rst'] or options['--test']:
        # Default is now rst
        options['--rst'] = True

    def mkdir(path):
        try:
            os.mkdir(path)
        except OSError:
            pass

    outdir = options['-o'] or (throot + '/html')
    files = None
    if len(args) != 0:
        files = [os.path.abspath(f) for f in args]
    mkdir(outdir)
    os.chdir(outdir)

    # Make sure the appropriate 'theano' directory is in the PYTHONPATH
    pythonpath = os.environ.get('PYTHONPATH', '')
    pythonpath = os.pathsep.join([throot, pythonpath])
    sys.path[0:0] = [throot]  # We must not use os.environ.

    # if options['--all']:
    #     mkdir("api")

        #Generate HTML doc

        ## This causes problems with the subsequent generation of sphinx doc
        #from epydoc.cli import cli
        #sys.argv[:] = ['', '--config', '%s/doc/api/epydoc.conf' % throot,
        #               '-o', 'api']
        #cli()
        ## So we use this instead
        #os.system("epydoc --config %s/doc/api/epydoc.conf -o api" % throot)

        # Generate PDF doc
        # TODO

    def call_sphinx(builder, workdir, extraopts=None):
        import sphinx
        if extraopts is None:
            extraopts = []
        if not options['--cache'] and files is None:
            extraopts.append('-E')
        docpath = os.path.join(throot, 'doc')
        inopt = [docpath, workdir]
        if files is not None:
            inopt.extend(files)
        sphinx.build_main(['', '-b', builder] + extraopts + inopt)

    if options['--all'] or options['--rst']:
        mkdir("doc")
        sys.path[0:0] = [os.path.join(throot, 'doc')]
        call_sphinx('html', '.')

        if not options['--nopdf']:
            # Generate latex file in a temp directory
            import tempfile
            workdir = tempfile.mkdtemp()
            call_sphinx('latex', workdir)
            # Compile to PDF
            os.chdir(workdir)
            os.system('make')
            try:
                shutil.copy(os.path.join(workdir, 'theano.pdf'), outdir)
                os.chdir(outdir)
                shutil.rmtree(workdir)
            except OSError as e:
                print('OSError:', e)
            except IOError as e:
                print('IOError:', e)

    if options['--test']:
        mkdir("doc")
        sys.path[0:0] = [os.path.join(throot, 'doc')]
        call_sphinx('doctest', '.')
