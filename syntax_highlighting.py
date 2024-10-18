import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

class SyntaxHighlighter:
    def __init__(self, text_widget, language="python"):
        self.text_widget = text_widget
        self.language = language
        self.lexer = self.get_lexer(language)
        self.setup_tags()

    def get_lexer(self, language):
        try:
            return get_lexer_by_name(language)
        except Exception:
            return get_lexer_by_name("text")

    def setup_tags(self):
        self.text_widget.tag_configure("Keyword", foreground="blue")
        self.text_widget.tag_configure("String", foreground="green")
        self.text_widget.tag_configure("Comment", foreground="gray")
        self.text_widget.tag_configure("Number", foreground="purple")
        self.text_widget.tag_configure("Operator", foreground="red")
        self.text_widget.tag_configure("Name", foreground="black")

    def highlight(self, event=None):
        code = self.text_widget.get("1.0", tk.END)
        tokens = lex(code, self.lexer)
        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, "1.0", tk.END)
        index = "1.0"
        for token_type, value in tokens:
            end_index = self.calculate_end_index(index, value)
            tag_name = self.get_tag_name(token_type)
            self.text_widget.tag_add(tag_name, index, end_index)
            index = end_index

    def calculate_end_index(self, start_index, value):
        lines = value.split('\n')
        line, column = map(int, start_index.split('.'))
        if len(lines) == 1:
            column += len(value)
        else:
            line += len(lines) - 1
            column = len(lines[-1])
        return f"{line}.{column}"

    def get_tag_name(self, token_type):
        if token_type in Token.Keyword:
            return "Keyword"
        elif token_type in Token.String:
            return "String"
        elif token_type in Token.Comment:
            return "Comment"
        elif token_type in Token.Number:
            return "Number"
        elif token_type in Token.Operator:
            return "Operator"
        else:
            return "Name"

# تطبيق اختباري
if __name__ == "__main__":
    root = TkinterDnD.Tk()  # استخدام TkinterDnD بدلاً من Tk
    root.title("Text Editor with Syntax Highlighting")

    text_area = tk.Text(root, wrap="word", undo=True)
    text_area.pack(expand=True, fill="both")

    highlighter = SyntaxHighlighter(text_area, language="python")

    def on_drop(event):
        filepaths = event.data.split()
        for filepath in filepaths:
            filepath = filepath.strip('{}')
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    text_area.insert(tk.END, content + "\n")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
        highlighter.highlight()

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    root.after(100, highlighter.highlight)
    text_area.bind("<KeyRelease>", highlighter.highlight)

    root.mainloop()
