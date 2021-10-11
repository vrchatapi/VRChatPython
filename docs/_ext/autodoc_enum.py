############################################
## Made following tutorials:
##      https://www.sphinx-doc.org/en/master/development/tutorials/todo.html
##      https://www.sphinx-doc.org/en/master/development/tutorials/autodoc_ext.html
############################################

from enum import Enum
from typing import Any, Optional

from docutils.statemachine import StringList

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter

def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")
    app.add_autodocumenter(EnumDocumenter)

class EnumDocumenter(ClassDocumenter):
    objtype = "enum"
    directivetype = "class"
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        return isinstance(member, Enum)

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        #self.add_line('', self.get_sourcename())

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False) -> None:
        super().add_content(more_content, no_docstring)

        source_name = self.get_sourcename()
        enum_object: Enum = self.object
        self.add_line('', source_name)

        for enum_value in enum_object:
            val_name = enum_value.name
            val_value = enum_value.value
            
            self.add_line(
                f"**{val_name}**: {val_value}", source_name)
            self.add_line("", source_name)