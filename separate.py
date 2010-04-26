#!/usr/bin/python2.5
import getopt, sys, os

from subprocess import Popen, PIPE
from os import path

from django.template import Context
from django.template.loader import get_template
from django.conf import settings

settings.configure(
    DEBUG = False,
    TEMPLATE_DEBUG = False,
    TEMPLATE_DIRS = []
)

TOC_TMPL = "toc.html"
TITLEPAGE_TMPL = "titlepage.html"
SECTION_TMPL = "section.html"

PROJ_CODE = "projectcode"
TITLE = "title"
SUBTITLE = "subtitle"
AUTHORS = "authors"
CONTRIBS = "contributors"
DATE = "date"

CHAPTER = "chapter"
CONTENTS = "contents"

SECT_ID = "section_id"
PREV_ID = "prev_id"
NEXT_ID = "next_id"
SECT_TITLE = "section_title"

TOC = "toc"
TEXT = "text"
MKD = "markdown"

SPLITDEPTH = 2

def usage():
    print "help"


def filelist(proj_dir):
    files = os.listdir(proj_dir)
    files = [f for f in files if f.endswith(".mkd")]
    files = [os.path.join(proj_dir, f) for f in files]
    files.sort()
    return files


def assert_valid_project(proj_dir=os.path.abspath(".")):
    if not os.path.isdir(proj_dir):
        print "Directory not found: %s" % proj_dir
        sys.exit(2)

    if len(filelist(proj_dir)) == 0:
        print "No .mkd files in %s" % proj_dir
        usage()
        sys.exit(2)


def is_heading(line, prev_line):
    """ Returns level, heading, if it is a heading, otherwise False."""

    if line.startswith("#"):
        level = line.count("#")
        return level, line[level:].strip()
    
    l = line.strip()
    if len(l) > 0 and len(l) in (l.count("-"), l.count("=")):
        level = 1 if line.count("=") else 2
        return level, prev_line.strip()

    return False


def parse(mkd):
    """ Splits the markdown into tuples of headings and paragraphs. """
    # parse and remove metadata
    chapter = {}
    new_mkd = []
    for line in mkd.splitlines(True):
        if not new_mkd and line.startswith("%"):
            key, _, val = line.replace("%","").partition(":")
            chapter[key.strip()] = val.strip()
        else:
            # append if we have already started the post-metadata block
            # or if the line starts with the metadate char
            new_mkd.append(line)
    
    mkd = "".join(new_mkd)

    # find headings and associate them with following text
    prev_line = ""
    heading = ""
    lvl = 0
    text = []
    contents = [] # elems (lvl, heading, text)

    for line in mkd.splitlines(True):
        h = is_heading(line, prev_line)
        if h:
            text = "".join(text).strip()
            if text or heading:
                contents.append((lvl, heading, text))
            text = []
            prev_line = ""
            lvl, heading = h
        else:
            text.append(prev_line)
            prev_line = line

    # add the final paragraph (usually triggered by following one, which
    # doesn't exist in this case)
    contents.append((lvl, heading, "".join(text)))

    chapter[CONTENTS] = contents 
    return chapter


def parsefiles(filenames):
    parts = []
    for f in filenames:
        fp = open(f)
        mkd = fp.read()
        fp.close()
        parts.append(parse(mkd))

    return parts


def gen_titlepage(doc):
    pass

def gen_section(id, chapter, title, text):
    pass

def gen_mkd(text):
    return text

mk_id = lambda lvl: ".".join([str(l) for l in lvl])

def compile(parts):
    ctxs = []
    toc = []

    lvl = [0]   # expands to e.g [1, 2] for chapter 1 section 2
    ctx = {}
    prev_ctx = {TEXT: ""}
    cur_depth = 0

    for part in parts:

        if len(part.keys()) > 1 or not part.has_key(CONTENTS):
            lvl = lvl[0:1]
            cur_depth = 0
            for k in part.keys():
                if k is CONTENTS:
                    continue
                ctx[k] = part[k]

            toc.append({ SECT_ID: "", SECT_TITLE: part[TITLE] })

        for depth, heading, text in part[CONTENTS]:
            depth -= 1
            if cur_depth < depth:
                cur_depth += 1
                lvl.append(1)
            elif cur_depth > depth:
                lvl = lvl[:-1]
                cur_depth -= 1
                lvl[cur_depth] += 1
            else:
                lvl[-1] += 1

            toc.append({ SECT_ID: mk_id(lvl), SECT_TITLE: heading })

            if depth == 0:
                ctx[CHAPTER] = heading

            if depth < SPLITDEPTH:
                ctx[SECT_ID] = mk_id(lvl)
                ctx[SECT_TITLE] = heading
                ctx[TEXT] = text
                prev_ctx = ctx.copy()
                ctxs.append(prev_ctx)

            if depth > (SPLITDEPTH - 1):
                sub_heading = "\n\n%s %s\n\n" % (("#" * (depth+1)), heading)
                prev_ctx[TEXT] += sub_heading
                prev_ctx[TEXT] += text
            
    prev = TOC
    for i, ctx in enumerate(ctxs):
        ctx[NEXT_ID] = ctxs[i+1][SECT_ID] if i < (len(ctxs) - 1) else TOC
        ctx[PREV_ID] = prev 
        ctx[TOC] = toc
        prev = ctx[SECT_ID]

    return toc, ctxs


def main(argv):                         
    try:
        optkeys = ["help", "verbose", "output=", "project_dir="]
        opts, args = getopt.getopt(argv, "hop:v", optkeys)
    except getopt.GetoptError, err:
        print "Error: %s\n" % err
        usage()
        sys.exit(2)

    files = args
    output = None
    verbose = False
    proj_dir = "."

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-p", "--project_dir"):
            proj_dir = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ('-o', "--output"):
            output = arg
        else:
            assert False, "unhandled option type"
    
    proj_dir = os.path.abspath(proj_dir)
    assert_valid_project(proj_dir)

    settings.TEMPLATE_DIRS = (
        os.path.abspath(os.path.join(proj_dir, "templates")),
        os.path.abspath(os.path.join(".", "templates")),
    )

    filenames = filelist(proj_dir)
    parts = parsefiles(filenames)
    toc, ctxs = compile(parts)
    toc = {
            "splitdepth": SPLITDEPTH,
            "toc": toc,
          }

    generate(TOC_TMPL, toc, "toc.html")

    for ctx in ctxs:
        out_file = ctx[SECT_ID] + ".html"
        ctx[MKD] = mkd_to_html(ctx[TEXT])
        if not ctx[TEXT].strip():
            generate(TITLEPAGE_TMPL, ctx, out_file)
        else:
            generate(SECTION_TMPL, ctx, out_file)

def mkd_to_html(mkd):
    #"pandoc --toc -o web/%s.html %s" % (refname, files)
    proc = Popen(["pandoc"], stdout=PIPE, stdin=PIPE)
    out, err = proc.communicate(mkd)
    return out


def generate(tmpl_name, ctx, filename):
    tmpl = get_template(tmpl_name)
    out = tmpl.render(Context(ctx))
    fp = open(os.path.join("web", "out", filename), 'w')
    fp.write(out.encode('utf-8'))
    fp.close()


if __name__ == "__main__":
    main(sys.argv[1:])


"""
os.system(html_cmd)

#pdf_cmd = "markdown2pdf --custom-header=header_%s.template --toc -o IE_%s.pdf %s" % (lang, lang, files)
#os.system(pdf_cmd)
"""
