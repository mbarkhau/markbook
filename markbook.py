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

def db_cmd(files, basepath="."):
    """ DocBook Command """
    files_param = " ".join(files)
    outpath = os.path.abspath(basepath) + "/out.db" 
    return "pandoc -s -S -w docbook -o %s %s" % (outpath, files_param)

def html_cmd(basepath="."):
    outpath = os.path.abspath(basepath) + "/out.db" 
    return "xmlto xhtml %s -o %s" % (outpath, basepath +"/html")

def get_tmpl(basepath="."):
    local_tmpl = "%s/%s" % (os.path.abspath(basepath), TEX_TMPL_NAME)
    if os.path.isfile(local_tmpl):
        return local_tmpl
    else:
        return TEX_TMPL_STD 

def tex_cmd(files, basepath="."):
    files_param = " ".join(files)
    args = (get_tmpl(basepath), "out.tex", files_param)
    return "pandoc -C %s -s -S --toc -o %s %s" % args

def pdf_cmd(basepath="."):
    return "pdflatex out.tex"

def compile(files, basepath="."):
    meta = metadata.compile(basepath)

    os.system(db_cmd(files, basepath))
    dbproc.post_proc(meta, basepath)
    os.system(html_cmd(basepath))
    os.system(tex_cmd(files, basepath))
    texproc.post_process(meta, basepath)
    os.system(pdf_cmd(basepath))
    os.system(pdf_cmd(basepath)) #2nd time for toc

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
           files = filelist(p)
           compile(files, p)
    else:
        print "Please specify the path of your markbook files"
