import os

from lxml import etree

_d = lambda s: s.decode("utf-8")
_e = lambda s: s.encode("utf-8")

HEADER = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE book PUBLIC "-//OASIS//DTD DocBook XML V4.4//EN"
               "http://www.oasis-open.org/docbook/xml/4.4/docbookx.dtd">

"""
def add_title(meta, node):
    if meta.has_key("title"):
        title = etree.Element("title")
        title.text = _d(meta["title"])
        node.append(title)
    if meta.has_key("subtitle"):
        subtitle = etree.Element("subtitle")
        subtitle.text = _d(meta["subtitle"])
        node.append(subtitle)

def add_meta(meta, info):
    if meta.has_key("date"):
        date = etree.Element("date")
        date.text = _d(meta["date"])
        info.append(date)
    if meta.has_key("author"):
        authors = [a.strip() for a in meta["author"].split(",")]
        authgroup = etree.Element("authorgroup")
        info.append(authgroup)
        for a in authors:
            author = etree.Element("author")
            firstname = etree.Element("firstname")
            surname = etree.Element("surname")
            firstname.text = _d(a.split(" ")[0])
            surname.text = _d(" ".join(a.split(" ")[1:]))
            author.append(firstname)
            author.append(surname)
            authgroup.append(author)

def post_proc_parts(parts, xml):
    partkeys = parts.keys()
    children = xml.getchildren()
    xml.clear()
    cur = xml
    for c in children:
        if c.tag == "chapter":
            title = c.xpath("title")[0].text
            if title in partkeys:
                meta = parts[title]
                part = etree.Element("part")
                xml.append(part)
                cur = part
                info = etree.Element("partinfo")
                part.append(info)
                add_meta(meta, info)
                add_title(meta, part)
            
        cur.append(c)


def post_proc(meta, basepath="."):
    """ Post processing for DocBook File (adds title/author/chapter)"""
    outpath = os.path.abspath(basepath) + "/out.db"
    xml = etree.fromstring(open(outpath).read())
    xml.tag = "book"
    info = xml.xpath("articleinfo")[0]
    info.tag = "bookinfo"
    info.clear()

    for e in xml.xpath("section"):
        e.tag = "chapter"
    
    if meta.has_key("parts"):
        post_proc_parts(meta["parts"], xml)

    if meta.has_key("lang"):
        xml.set("lang", meta["lang"])

    add_title(meta, info)
    add_meta(meta, info)
            
    out = open("out.db", "w")
    out.write(HEADER)
    out.write(etree.tostring(xml))
    out.close()
