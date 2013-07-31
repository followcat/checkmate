import os
import os.path
import sys
import optparse
import docutils.core
import docutils.nodes


class Writer(docutils.writers.Writer):
  
    def __init__(self):
        docutils.writers.Writer.__init__(self)
        self.translator_class = TableNodeVisitor
  
    def translate(self):
        self.visitor = visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = ''.join(visitor.output)

class TableNodeVisitor(docutils.nodes.GenericNodeVisitor):
    """this visitor is visit table in restructure text

        >>> import os
        >>> f1 = open(os.getenv("CHECKMATE_HOME") + '/sample_app/exchanges.rst')
        >>> c = f1.read()
        >>> f1.close()
        >>> f2 = open('/tmp/exchanges_gen.rst', 'w')
        >>> import docutils.core
        >>> dt = docutils.core.publish_doctree(source=c)
        >>> import checkmate.parser.rst_writer 
        >>> wt = checkmate.parser.rst_writer.Writer()
        >>> wt.write(document=dt, destination=f2) # doctest: +ELLIPSIS
        1...
        >>> f2.close()
    """

    def __init__(self, document):
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.document = document
        self.output = []

    def get_title_marker(self, title_level):
        if title_level == 1:
            return '='
        if title_level == 2:
            return '-'
        if title_level == 3:
            return '+'
        if title_level == 4:
            return '*'
        if title_level == 5:
            return '^'
        if title_level == 6:
            return '$'


    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_document(self, node):
        self.inside_system_message = False
        self.inside_table = False
        self.highest_level = 5
        self.title_level = 1

    def depart_document(self, node):
        while self.output[-3:] == ['\n', '\n', '\n']:
            self.output.pop()

    def visit_section(self, node):
        self.title_level += 1

    def depart_section(self, node):
        self.title_level -= 1
        self.output.append('\n')

    def visit_title(self, node):
        title_marker = self.get_title_marker(self.title_level)
        if len(title_marker) <1 :
            title_marker = '$'
            print(self.title_level)
        title = node.astext()
        self.output.append(title)
        self.output.append('\n')
        self.output.append(title_marker*(len(title)+1) + '\n')
 
    def depart_title(self, node):
        pass

    def visit_subtitle(self, node):
        visit_title(node)
 
    def depart_subtitle(self, node):
        depart_title(node)

    def _bottom_line(self):
        return_text = list('-' * self.row_length )
        change_point = 0
        if len(self.column_width) > 0:
            for column_width in ([0] + self.column_width):
                change_point += column_width
                if change_point > 0:
                    change_point += 2
                if change_point < len(return_text):
                    return_text[change_point] = '+'
        return ''.join(return_text)

    def visit_table(self, node):
        self.column_width = []
        self.inside_table = True
        self.row_length = 0
        self.local_table = ''

    def depart_table(self, node):
        self.inside_table = False
        self.output += '\n' + self._bottom_line() + '\n'
        self.output += self.local_table + '\n'
        self.row_length = 0

    def visit_thead(self, node):
        pass

    def depart_thead(self, node):
        # get the buttum line of '===='
        r_index = self.local_table[:(len(self.local_table)-1)].rindex('\n')
        self.local_table = self.local_table[:r_index] + self.local_table[r_index:].replace('-', '=')

    def visit_row(self, node):
        self.local_table += '|'
        self.row_length = 1
        self.column = 0

    def depart_row(self, node):
        self.local_table += '\n'
        self.local_table += self._bottom_line() + '\n'

    def visit_entry(self, node):
        column_width = self.column_width[self.column]
        entry = node.astext()
        added_text = ' ' + entry.rstrip(os.linesep).ljust(column_width) + '|'
        self.row_length += len(added_text)
        self.local_table += added_text

    def depart_entry(self, node):
        self.column += 1

    def visit_system_message(self, node):
        self.inside_system_message = True

    def depart_system_message(self, node):
        self.inside_system_message = False

    def visit_paragraph(self, node):
        if self.inside_table or self.inside_system_message:
            return
        paragraph = node.astext()
        if node.parent == self.document:
            paragraph += '\n'
        self.output.append(paragraph + '\n')

    def visit_colspec(self, node):
        self.column_width.append(node.get('colwidth')-1)

    def depart_colspec(self, node):
        pass

class VisitorOptionParser(optparse.OptionParser):
    def set_options(self):
        self.add_option('-i', '--with-input-file', dest='input_file',
                        metavar='FILE', 
                        help="input rst filename")

        self.add_option('-o', '--with-output-file', dest='output_file',
                        metavar='FILE', 
                        help="output rst filename")
        usage = 'you can use "python rst_writer.py input_file output_file" to process directly'
        self.set_usage(usage)

def open_file(filename):
    try:
        return open(filename)
    except:
        if os.path.isfile(filename):
            print("Problem opening input file %s." %(filename))
        else:
            print("%s is not a file." %(filename))
        sys.exit(-1)

def call_visitor():
    option_parser = VisitorOptionParser()
    option_parser.set_options()
    try:
        option_parser.print_usage()
        (options, args) = option_parser.parse_args()
    except:
        option_parser.print_usage()
        sys.exit(-1)
    input_file = options.input_file
    output_file = options.output_file
    if len(args) >= 2:
        input_file = args[0]
        output_file = args[1]
    if input_file == None or output_file == None:
        print('need 2 args')
        sys.exit(-1)
    f1 = open_file(input_file)
    content = f1.read()
    f1.close()
    f2 = open(os.path.join(os.path.dirname(output_file),
                                   (os.path.basename(output_file).split(os.extsep)[0]
                                    + os.extsep + 'rst')), 'w')
    dt = docutils.core.publish_doctree(source=content)
    wt = Writer()
    wt.write(document=dt, destination=f2)
    f2.close()
    
def main():
    call_visitor()

if __name__ == '__main__':
    main()

