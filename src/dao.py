#!/usr/bin/env python
__author__ = 'Holger Bast'
import argparse,sys
import logging
from lxml import etree

logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

namespaces = {'fo': 'http://www.w3.org/1999/XSL/Format'}


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy. http://stackoverflow.com/a/26853961/2153744"""
    if not isinstance(x, dict):
        x = dict()
    elif not isinstance(y, dict):
        y = dict()

    z = x.copy()
    z.update(y)
    return z


def reduce_block(node):
    logger.debug("reduce_block() with node: %s %s", node.tag, node.attrib)
    count_all_children = len(node.findall('./', namespaces))
    count_fob_children = len(node.findall('./fo:block', namespaces))
    count_fom_children = len(node.findall('./fo:marker', namespaces))
    logger.debug("amount of children:     %s", count_all_children)
    logger.debug("amount of fob children: %s", count_fob_children)
    logger.debug("node contains any text: %s", "None" if node.text is None else "yes")

    if (count_all_children == 1 and count_fob_children == 1 and node.text is None) or \
            (count_all_children == 2 and count_fob_children == 1 and count_fom_children == 1 and node.text is None):
        logger.debug("merge possible:         yes")

        child = node.find('fo:block', namespaces)
        marker = node.find('fo:marker', namespaces)
        parent = node.getparent()
        # contains the position of the current node in the parent tree
        pos = parent.index(node)

        # merging attributes
        # child attributes overwrite parent attributes
        merged_attrib = merge_two_dicts(dict(node.attrib), dict(child.attrib))
        logger.debug("child attribs:          %s %s", len(child.attrib), child.attrib)
        logger.debug("node attribs:           %s %s", len(node.attrib), node.attrib)
        logger.debug("merged attribs          %s %s", len(merged_attrib), merged_attrib)

        # merging
        # 1) move child to the position of node in parent tree
        # 2) replace child's attributes with the merged attribs
        # 3) remove node from parent tree
        parent.insert(pos, child)
        etree.strip_attributes(child, '*')
        for k, v in merged_attrib.iteritems():
            child.set(k, v)
        parent.remove(node)

        # if there is a fo:marker block, it has also to be moved (in front of fo:block)
        if marker is not None:
            parent.insert(pos, marker)

        # because the node order has changed (node was replaced by child)
        # the child must be analyzed also, so we call reduce_block with child from the new position
        reduce_block(parent[pos])

    else:
        logger.debug("merge possible:         no")
        logger.debug("children: ")
        for child in node.findall('./fo:block', namespaces):
            logger.debug("%s %s", child.tag, child.attrib)

        for child in node.findall('./fo:block', namespaces):
            reduce_block(child)

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='DAO - DocBook Accessibility Optimizer for Apache FOP')
    parser.add_argument('-i', '--input', help='Input file name', required=True)
    parser.add_argument('-o', '--output', help='Output file name', required=True)
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true', required=False)
    parser.add_argument('-p', '--pretty', help='pretty xml output', action='store_true', required=False)
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.pretty:
        pretty_print = True
    else:
        pretty_print = False

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(args.input, parser=parser)

    fob_count_start = len(tree.findall('.//fo:block', namespaces))

    # first: remove empty fo:blocks <fo:blocks/> in the document body
    #
    # fob_count_empty = 0
    # for node in tree.findall('./fo:page-sequence//fo:block', namespaces):
    #     # no text, no attributes, no children
    #     if node.text is None and len(node.attrib) == 0 and len(node.findall('./', namespaces)) == 0:
    #         if "flow" in node.getparent().tag or "block" in node.getparent().tag:
    #             logger.debug("removing empty <fo:block/>")
    #             node.getparent().remove(node)
    #             fob_count_empty += 1
    #
    # fob_count_before_optimizing = len(tree.findall('.//fo:block', namespaces))

    # marking header and footer as artifacts
    for node in tree.findall('./fo:page-sequence/fo:static-content', namespaces):
        node.set('role', 'artifact')

    # optimizing nested fo:blocks
    for node in tree.findall('.//fo:flow/fo:block', namespaces):
        reduce_block(node)

    fob_count_end = len(tree.findall('.//fo:block', namespaces))

    logger.info("reading from:              %s", args.input)
    logger.info("fo:block count:            %s", fob_count_start)
    #logger.info("empty fo:block deleted:    %s", fob_count_empty)
    logger.info("optimized fo:block:        %s", fob_count_start - fob_count_end)
    #logger.info("overall fo:blocks removed: %s", fob_count_empty + (fob_count_before_optimizing - fob_count_end))
    logger.info("overall optimization:      %s%%", 100.0 / fob_count_start * (fob_count_start - fob_count_end))
    logger.info("saving to:                 %s", args.output)
    tree.write(args.output, xml_declaration=True, encoding='utf-8', pretty_print=pretty_print)
