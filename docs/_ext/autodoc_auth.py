from typing import Any, Optional

from docutils.statemachine import StringList

from sphinx.application import Sphinx
from sphinx.ext.autodoc import MethodDocumenter

def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")
    app.add_autodocumenter(AuthDocumenter)

class AuthDocumenter(MethodDocumenter):
    objtype = "auth"
    directivetype = "method"
    priority = 1 + MethodDocumenter.priority
    option_spec = dict(MethodDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        x = super().can_document_member(member, membername, isattr, parent)
        
        return x and member.__name__ == "_method" and hasattr(member, "__nested_annotations__")

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        #self.add_line('', self.get_sourcename())

    def add_content(self, more_content: Optional[StringList], no_docstring: bool = False) -> None:
        super().add_content(more_content, no_docstring)

    def get_method_path(self, method) -> str:
        if not hasattr(method, "__name__"):
            return str(method).replace("typing.", "")
        elif method.__module__ == "builtins":
            return method.__name__

        return method.__module__ + "." + method.__name__

    def format_args(self, **kwargs: Any) -> str:
        x = super().format_args(**kwargs)

        if x == "(*args, **kwargs)":
            annotations = self.object.__nested_annotations__

            r = None
            if "return" in annotations:
                r = annotations["return"]
                del annotations["return"]

            f_args = "(" + ", ".join([ann + ": " + self.get_method_path(annotations[ann]) for ann in annotations]) + ")"

            if r is not None:
                f_args += " -> " + self.get_method_path(r)

            return f_args
        return x