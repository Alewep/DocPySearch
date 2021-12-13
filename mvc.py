import json
import math
import os
import tkinter as tk
from tkinter import filedialog
from lxml import etree
import costum_tkinter
import costum_tkinter as ctk
import indexer

BACKGROUND = "#E5E7E9"
MENU_COLOR = "#566573"

HEAD_COLOR = "#2471A3"
PERTINANCE_COLOR = "#F39C12"
RESUME_COLOR = "#424949"

NO_RESULT_COLOR = "#626567"
NO_RESULT = "No document found for this query"
CORRECTION = "Correction of request :"
TITLE_COLOR = "#5DADE2"

WORD_COLORING = "/AND /OR /*"


class Model:
    ERROR = "error"
    SUCCESS = "success"
    NOT_PATH = "not_path"

    def __init__(self):
        self.reponse = None
        self.old_query = None
        self.result = None
        self.index = None
        self.status = None
        self.folder_path = None
        with open("config.json") as file:
            config = json.loads(file.read())
            self.folder_path = config["folder_path"]
            self.index_path = config["index_path"]
        self.InitializeIndex()

    def InitializeIndex(self):

        if os.path.isdir(self.folder_path):
            try:
                self.index = indexer.Indexer(self.index_path)
                if not self.index.index:
                    self.index = indexer.indexer_xml(self.index, self.folder_path)
            except Exception as e:
                print(e)
                self.status = Model.ERROR
            finally:
                self.status = Model.SUCCESS

        else:
            self.status = Model.NOT_PATH

    def executeQuery(self, query, numpage):
        if self.old_query is None or self.old_query != query:
            self.old_query = query
            self.reponse = self.index.fuzzy(query)

        lenght = len(self.reponse)
        number_page = math.ceil(lenght / 20)
        first = 20 * numpage if (numpage < number_page) else 20 * (number_page - 1)
        last = first + 20 if (first + 20 < lenght) else lenght
        return {k: self.reponse[k] for k in list(self.reponse)[first:last]}, lenght, number_page

    def resume(self, docid):
        doc, id = docid.split("-")
        file_name = self.folder_path + doc
        tree = etree.parse(file_name)
        temp = tree.xpath(f"/DOCS/DOC/DOCNO[normalize-space()='{docid}']/../*"
                          f"[not(self::TEXT) and not(self::DOCNO) and not(self::NOTE)]")
        resume = ""
        for section in temp:
            resume += etree.tostring(section).decode("utf-8")
        return resume

    def get_document(self, docid):
        doc, id = docid.split("-")
        file_name = self.folder_path + doc
        tree = etree.parse(file_name)
        temp = tree.xpath(f"/DOCS/DOC/DOCNO[normalize-space()='{docid}']/..")
        if temp:
            return etree.tostring(temp[0]).decode("utf-8"), self.old_query.split(" ")
        return None, None


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.configure(bg=BACKGROUND)

        self.msg = tk.Label(self)
        self.msg.configure(font=("Courier", 12, "italic"))
        self.msg.pack(side=tk.TOP, anchor=tk.NE)

        self.label = tk.Label(self, text='DocPySearch')
        self.label.configure(font=("Courier", 100, "italic"), bg=BACKGROUND, fg=TITLE_COLOR)
        self.label.pack(side=tk.TOP, pady=(250, 10))

        self.entry = ctk.EntryWithPlaceholder(self,placeholder="Search document with a query")
        self.entry.configure(width=50, font=("Courier", 24, "italic"), bg=BACKGROUND)

        self.entry.pack(side=tk.TOP, pady=(0, 10))

        self.search = tk.Button(self, text="Search", font=("Courier", 24, "italic"), command=lambda: master.search(0))
        self.search.pack(side=tk.TOP)


class ShowResults(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.configure(bg=BACKGROUND)
        tk.Button(self, text="Return to start page",
                  command=lambda: master.switch_frame(StartPage)).pack(side=tk.TOP, anchor=tk.NE)

        # ---- Frame entry ----
        self.frame_entry = tk.Frame(self, bg=BACKGROUND)
        self.label = tk.Label(self.frame_entry, text='DocPySearch')
        self.label.configure(font=("Courier", 100, "italic"), bg=BACKGROUND, fg=TITLE_COLOR)

        self.entry = ctk.EntryWithPlaceholder(self.frame_entry, placeholder="Search document with a query")

        self.entry.configure(width=50, font=("Courier", 24, "italic"), bg=BACKGROUND)

        self.search = tk.Button(self.frame_entry, text="Search", font=("Courier", 18, "italic"),
                                command=lambda: master.search(0))

        self.label.pack(side=tk.TOP, pady=(10, 10), anchor=tk.NW)
        self.entry.pack(side=tk.LEFT, anchor=tk.NW)
        self.search.pack(side=tk.LEFT, anchor=tk.N, padx=50)
        self.frame_entry.pack(side=tk.TOP, anchor=tk.NW, pady=(0, 50), padx=50)
        # --- Frame entry -----
        # Page entry
        self.frame_page = tk.Frame(self, bg=BACKGROUND)
        self.label_page = tk.Label(self.frame_page, bg=BACKGROUND, text="Page :")
        self.page_entry = tk.Entry(self.frame_page, fg="black")
        self.page_entry.delete(0, "end")
        self.page_entry.insert(0, "0")
        self.label_page.pack(side=tk.LEFT, anchor=tk.NW, padx=10)
        self.page_entry.pack(side=tk.LEFT, anchor=tk.NW, padx=10)
        self.page_entry.bind("<FocusOut>", self.validation_page)
        self.frame_page.pack(side=tk.TOP, anchor=tk.NW)
        # ------
        self.results = None
        self.label_count = None
        self.redirection = None

    def add_results(self, head: str, resume: str, pertinance: str, query: str):
        new_frame = tk.Frame(self.results.scrollable_frame, borderwidth=3, relief="ridge", bg=BACKGROUND)
        new_frame.pack(side=tk.TOP, anchor=tk.NW, expand=True, fill=tk.X, padx=(50, 50), pady=(10, 0))

        label_head = tk.Button(new_frame, text=head, bg=BACKGROUND)
        label_head.configure(font=("Courier", 16), fg=HEAD_COLOR)
        label_head.pack(side=tk.TOP, anchor=tk.NW)
        label_head.bind("<Button-1>", lambda event: self.master.open_view_documents(head))

        label_pertinance = tk.Label(new_frame, text=f"score :{pertinance}", bg=BACKGROUND)
        label_pertinance.configure(font=("Courier", 9), fg=PERTINANCE_COLOR)
        label_pertinance.pack(side=tk.RIGHT, anchor=tk.NE, padx=(50, 50))

        label_resume = ctk.HighlightText(master=new_frame, height=10, words=query)
        label_resume.insert(1.0, resume)
        label_resume.highlight_words()
        label_resume.configure(state="disabled")
        label_resume.configure(font=("Courier", 12), fg=RESUME_COLOR, bg=BACKGROUND)
        label_resume.pack(side=tk.TOP, anchor=tk.NW, expand=True, fill=tk.BOTH)

    def have_results(self, number_results, number_page, query, result=True, correction=False):

        if result:
            self.results = costum_tkinter.ScrollableFrame(self, bg=BACKGROUND)
            self.results.scrollable_frame.configure(bg=BACKGROUND)
            self.label_count = tk.Label(self.frame_page,
                                        text=f"Number of results :{number_results}, nombre de page {number_page}")
            self.label_count.configure(font=("Courier", 12), fg=RESUME_COLOR, bg=BACKGROUND)
            self.results.pack(side=tk.TOP, anchor=tk.NW, padx=(50, 50), pady=(0, 0), expand=True, fill=tk.BOTH)
            self.label_count.pack(side=tk.LEFT, anchor=tk.NW, padx=(0, 200))
            if correction:
                self.redirection = tk.Label(self.frame_page, font=("Courier", 12), text=CORRECTION + query,
                                            bg=BACKGROUND,
                                            fg="#76448A")
                self.redirection.pack(side=tk.RIGHT, anchor=tk.NE)
        else:
            self.results = tk.Label(self, font=("Courier", 40), fg=NO_RESULT_COLOR, bg=BACKGROUND, text=NO_RESULT)
            self.results.pack(side=tk.BOTTOM, anchor=tk.S, padx=(50, 50), pady=(0, 0), expand=True, fill=tk.BOTH)

    def validation_page(self, event):
        try:
            self.master.search(int(self.page_entry.get()))
        except Exception as e:
            self.page_entry.delete(0, "end")


class Controller(tk.Tk):

    def __init__(self, ):
        tk.Tk.__init__(self)
        self.model = Model()
        self.view = None
        # define root
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))
        self.title("DocPySearch")
        self.configure(bg=TITLE_COLOR)

        self.menubar = tk.Menu(self, bg=MENU_COLOR, fg=BACKGROUND)
        self.config(menu=self.menubar)
        self.menufichier = tk.Menu(self.menubar, tearoff=0, fg=BACKGROUND)
        self.menubar.add_cascade(label="Parameters", menu=self.menufichier)

        self.bind_command()
        self.switch_frame(StartPage)
        self.model.InitializeIndex()
        self.updateStatus(self.model.status)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.view is not None:
            self.view.destroy()
        self.view = new_frame
        self.view.pack(fill=tk.BOTH, expand=1)
        try:
            self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        except:
            pass

    def browserFiles(self):
        filename = filedialog.askdirectory()
        self.model.folder_path = filename + "/"
        self.model.InitializeIndex()
        self.updateStatus(self.model.status)

    def search(self, page):
        query = self.view.entry.get()
        if isinstance(self.view, ShowResults):
            self.view.results.destroy()
            if self.view.label_count is not None:
                self.view.label_count.destroy()
            if self.view.redirection is not None:
                self.view.redirection.destroy()
        else:
            self.switch_frame(ShowResults)
            self.view.entry.delete(0, "end")
            self.view.entry.insert(0, query)

        reponse, number_result, number_page = self.model.executeQuery(query, page)
        if reponse == {}:
            self.view.have_results(0, 0, self.model.old_query, result=False)
            return

        self.view.have_results(number_result, number_page, self.model.old_query, correction=True)
        for key, value in reponse.items():
            self.view.add_results(key, self.model.resume(key), value, self.model.old_query)

    def open_view_documents(self, docid):
        window = tk.Tk()
        window.title(docid)
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        window.geometry("%dx%d" % (math.ceil(width / 2), math.ceil(height / 2)))
        text, words = self.model.get_document(docid)
        text_box = ctk.HighlightText(master=window, words=words)
        text_box.insert("1.0", text)
        text_box.highlight_words()
        text_box.configure(state="disabled")
        text_box.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=True)
        tk.mainloop()

    def updateStatus(self, status):
        if status == Model.ERROR:
            self.view.msg.configure(text="An error occurred while loading or creating the index ×", fg="red")
        if status == Model.NOT_PATH:
            self.view.msg.configure(text="The path to the corpus folder is invalid or does not exist ×", fg="red")
        if status == Model.SUCCESS:
            self.view.msg.configure(text="Index building successfully ✓", fg="green")

    def bind_command(self):
        self.menufichier.add_command(label="Define path", command=self.browserFiles)


if __name__ == "__main__":
    app = Controller()
    app.mainloop()
