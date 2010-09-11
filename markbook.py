#!/usr/bin/python2.5
import sys 
import os, time
import texproc
import docbookproc as dbproc
import metadata

TEX_TMPL_NAME = "header.tex.tmpl"
TEX_TMPL_STD = os.path.join(os.path.dirname(__file__), "header_en.tex.tmpl")
FILE_ENDINGS = (".txt", ".mkd", ".markdown")

def filelist(basepath="."):
    basepath = os.path.abspath(basepath)
    files = []
    for path, dirs, dirfiles in os.walk(basepath):
        for f in dirfiles:
            files.append(os.path.join(path, f))
    mkd = []
    for e in FILE_ENDINGS:
        mkd.extend(filter(lambda f: f.endswith(e), files))

    mkd.sort()
    return mkd 

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

def compile(files):
    meta = metadata.compile()

    os.system(db_cmd(files))
    dbproc.post_proc(meta)
    os.system(html_cmd())
    os.system(tex_cmd(files))
    texproc.post_process(meta)
    os.system(pdf_cmd())
    os.system(pdf_cmd()) #2nd time for toc

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
           files = filelist(p)
           compile(files)
    else:
        print "Please specify the path of your markbook files"
