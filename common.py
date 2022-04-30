# https://en.wikipedia.org/wiki/Wikipedia:Namespace
WIKIPEDIA_NAMESPACES = {
    "Talk",
    "User",
    "User talk",
    "Wikipedia",
    "Wikipedia talk",
    "File",
    "File talk",
    "MediaWiki",
    "MediaWiki talk",
    "Template",
    "Template talk",
    "Help",
    "Help talk",
    "Category",
    "Category talk",
    "Portal",
    "Portal talk",
    "Draft",
    "Draft talk",
    "TimedText",
    "TimedText talk",
    "Module",
    "Module talk",
    "Deprecated",
    "Gadget",
    "Gadget talk",
    "Gadget definition",
    "Gadget definition talk",
    "Virtual namespaces",
    "Special",
    "Media",
}


def is_namespace_title(title: str):
    return title.find(":") != -1 and title.split(":")[0] in WIKIPEDIA_NAMESPACES
