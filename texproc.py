import os 

def get_part_tex(part):
    res = []
    res.append("\\part")
    if part.has_key("title"):
        res.append("[" + part["title"] + "]")
        res.append("{" + part["title"])
    if part.has_key("subtitle"):
        res.append(": " + part["subtitle"])
    if part.has_key("author") or part.has_key("date"):
        res.append("\\linebreak \\newline \\normalsize ")
    if part.has_key("author"):
        res.append(part["author"])
    if part.has_key("author") and part.has_key("date"):
        res.append(", ")
    if part.has_key("date"):
        res.append(part["date"])

    res.append("}\n")

    return "".join(res)

def post_process(meta):
    """ Post processing for Tex File (adds title/author/chapter)"""
    old_lines = open("out.tex").readlines()
    new_lines = []
    part_keys = meta["parts"].keys()
    for i, line in enumerate(old_lines):
        if "\\begin{document}" in line:
            res = []
            if meta.has_key("title"):
                res.append("\\title{\\Huge \\bf " + meta["title"])
                if meta.has_key("subtitle"):
                    res.append("\\linebreak \\Large " + meta["subtitle"])
                res.append("}\n")

            if meta.has_key("author"):
                authors = meta["author"].split(",")
                res.append("\\author{\\Large " + "\\\\ \\Large ".join(authors) + "}\n")
            if meta.has_key("date"):
                res.append("\\date{" + meta["date"] + "}\n")
            new_lines.append("".join(res))
            new_lines.append(line)
            new_lines.append("\\maketitle\n")

        elif "section" in line:
            for p_key in part_keys:
                if p_key in line:
                    part = meta["parts"][p_key]
                    new_lines.append(get_part_tex(part))
            if "subsection" in line:
                new_lines.append(line.replace("subsection", "section"))
            else:
                new_lines.append(line.replace("section", "chapter"))
        else:
            new_lines.append(line)
    open("out.tex", "w").writelines(new_lines)
