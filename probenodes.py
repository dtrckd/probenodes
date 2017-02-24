#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals


import sys, os
import numpy as np
from functools import partial
from multiprocessing import Pool # TODO: parallelize the looping probe
try:
    import spur
except ImportError:
    print('Import Error: please install spur package : pip3 install --user spur')
    exit(2)
try:
    from tabulate import tabulate
except ImportError:
    print('Import Error: please install tabulate package : pip3 install --user tabulate')
    exit(2)

conf = dict(
    username = 'adulac',
    private_key = os.path.join(os.path.expanduser('~'), '.ssh/id_rsa'),
    hosts = ['racer', 'tiger', 'victory', 'fuzzy', 'zombie', 'corona', 'macks', 'hertog'], # Could'n use racer.imag.fr ?
)

_md_ext = [ 'headerid', 'sane_lists', 'smart_strong', 'extra', 'footnotes',
    'smarty', 'codehilite', 'wikilinks', 'fenced_code', 'admonition',
    'nl2br', 'abbr', 'toc', 'attr_list', 'def_list', 'tables', 'meta',
]


class ProbeNodes(object):

    default_script = './bin/amaburn1.sh'

    def __init__(self, conf):
        self.conf = conf
        for k, v in conf.items():
            setattr(self, k, v)

    def task_setup(self, task):
        if task == 'cpu':
            self.headers = ['users/#cores'] + self.hosts
            self.op_load = lambda x : x / 100
        elif task == 'mem':
            self.headers = ['users/%memory'] + self.hosts
            self.op_load = lambda x : x
        else:
            raise ValueError('What task ? %s' % (task))

        self.script = [self.default_script, task]
        self.task = task
        return

    # How to keep the connection open ?
    def probe_hosts(self, task):
        self.task_setup(task)
        results = {}
        self.shells = {}
        for host in self.hosts:
            if host ==  'zombie':
                # ssh/.config is ignored !!!
                _host = 'zombie-dust'
            else:
                _host = host
            try:
                shell = spur.SshShell(hostname=_host,
                                      username=self.username,
                                      private_key_file=self.private_key,
                                      missing_host_key=spur.ssh.MissingHostKey.auto_add)
                with shell:
                    mesg = shell.run(self.script).output
                    self.shells[host] = shell
            except spur.ssh.ConnectionError as error:
                print(error.original_traceback)
                mesg = 'null'
            finally:
                results[host] = {'output':mesg}
        return results

    def format_probes(self, r, sort=True):
        hosts = self.hosts
        headers = self.headers
        task = self.task
        self.users = [u.split()[0] for u in list(filter(None, r[hosts[0]]['output'].decode('utf8').split('\n')))]
        # __remove extras information__
        self.users = self.users[:-1]
        table = np.zeros((len(self.users), len(hosts)))
        _ont = ['user',self.task]
        for _col, _h in enumerate(r.items()):
            h, res = _h
            mesg = res['output']
            col = hosts.index(h)
            if isinstance(mesg, bytes):
                mesg = mesg.decode('utf8')
            users = mesg.split('\n')
            users = list(filter(None, users))
            load_avg = users.pop(-1) # -> self.resulst
            headers[col+1] = headers[col+1] + '(%s)'%(load_avg)
            for _row, elt in enumerate(users):
                u = elt.split()
                uname = u[0]
                row = self.users.index(uname)
                try:
                    load = self.op_load(float(u[_ont.index(task)]))
                except:
                    load = 0
                table[row, col] = load

        if sort is True:
            sort_load = table.sum(1).argsort()[::-1]
            table = table[sort_load]
            self.users = np.asarray(self.users)[sort_load]

        table = np.column_stack((self.users, table))
        return table

    # don't work
    def probe(self):
        results = {}
        for host, shell in self.shells.items():
            results[host] = shell.run(self.script).output

        table = self.format_probes(results)
        return self.show(table)

    def dump(self, task=None,  file=sys.stdout, wrap=None):
        task = task or self.task
        table = self.format_probes(self.probe_hosts(task))
        table = tabulate(table, headers=self.headers)
        if wrap:
            table = wrap(table)
        if isinstance(file , str):
            with open(file, 'w') as _f:
                _f.write(table+'\n')
        else:
            print(table, file=sys.stdout)

    def loop(self, ts=None):
        from markdown import markdown
        markdown_extra = partial(lambda p, x: markdown(x, p), [ 'markdown.extensions.%s'%(ext) for ext in _md_ext])
        tasks = ['cpu', 'mem']
        while True:
            for t in tasks:
                self.dump(task=t, file='pb_%s'%t)
                #self.dump(task=t, file='pb_%s'%t, wrap=markdown_extra)

    @staticmethod
    def html():
        t1 = open('pb_cpu', 'r').read()
        t2 = open('pb_mem', 'r').read()
        scr = '''<script type="text/javascript">
        setTimeout(function () { location.reload(true); }, %s);
        </script>''' % (2000)

        t = 'HTTP/1.1 200 OK\n\n'
        m = '''<!DOCTYPE html><html><body>
        <pre>%s \n %s \n %s</pre>
        </body></html>''' % (t1, t2, scr)

        html = t+m
        print(html, file=sys.stdout)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        conf['task'] = sys.argv[1]

    if conf.get('task') == 'html':
        ProbeNodes.html()
        exit()

    pb = ProbeNodes(conf)

    if conf.get('task'):
        pb.dump(conf['task'])
    else:
        pb.loop()


