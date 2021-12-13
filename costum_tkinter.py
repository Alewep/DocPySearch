import tkinter as tk
import re


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)
        self.is_placeholder = True
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def insert(self, index, string: str) -> None:
        self.delete(0, "end")
        super(EntryWithPlaceholder, self).insert(index, string)

    def delete(self, first, last) -> None:

        if self.is_placeholder:
            super(EntryWithPlaceholder, self).delete(0, "end")
            self['fg'] = self.default_fg_color
            self.is_placeholder = False

        super(EntryWithPlaceholder, self).delete(first, last)

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        self.is_placeholder = True

    def foc_in(self, *args):
        if self.is_placeholder:
            self.delete('0', 'end')

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class ScrollableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(ScrollableFrame, self).__init__(*args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)

        self.item = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox(tk.ALL)
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.item, width=e.width)
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


class HighlightText(tk.Text):
    def __init__(self, words="", highlight="#F4D03F", *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(words, str):
            self.words = words.split(" ")
        else:
            self.words = words
        self.highlight = highlight

    def highlight_words(self):
        for word in self.words:
            word = word.lower()
            lines = self.get("1.0", "end").lower().split("\n")
            for index, line in enumerate(lines):
                l = index + 1

                for e in re.finditer(r"\b(" + word + r")|" + r"\b(" + word.replace("*", r"[^\b]") + r")\b", line):
                    self.tag_add("h", f"{l}.{e.span()[0]}", f"{l}.{e.span()[1]}")

        self.tag_config("h", background=self.highlight)
