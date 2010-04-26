#!/usr/bin/python2.5

import os, time
import texproc
import docbookproc as dbproc
import metadata

TEX_TMPL_NAME = "header.tex.tmpl"
TEX_TMPL_STD = os.path.join(os.path.dirname(__file__), "header_en.tex.tmpl")

def filelist(basepath="."):
    basepath = os.path.abspath(basepath)
    files = []
    for path, dirs, dirfiles in os.walk(basepath):
        for f in dirfiles:
            files.append(os.path.join(path, f))
    files = filter(lambda f: f.endswith(".mkd"), files)
    files.sort()
    return files

def db_cmd(files):
    """ DocBook Command """
    files_param = " ".join(files)
    return "pandoc -s -S -w docbook -o out.db %s" % files_param

def html_cmd():
    return "xmlto xhtml %s -o %s" % ("out.db", "html")

def get_tmpl():
    if os.path.isfile(TEX_TMPL_NAME):
        return TEX_TMPL_NAME 
    else:
        return TEX_TMPL_STD 
def tex_cmd(files):
    files_param = " ".join(files)
    out_path = "out.tex"
    args = (get_tmpl(), out_path, files_param)
    return "pandoc -C %s -s -S --toc -o %s %s" % args

def pdf_cmd():
    return "pdflatex out.tex"

def compile():
    meta = metadata.compile()

    files = filelist()
    os.system(db_cmd(files))
    dbproc.post_proc(meta)
    os.system(html_cmd())
    os.system(tex_cmd(files))
    texproc.post_process(meta)
    os.system(pdf_cmd())
    os.system(pdf_cmd()) #2nd time for toc

compile()
