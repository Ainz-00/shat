import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from bidi.algorithm import get_display
from syntax_highlighting import SyntaxHighlighter


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Note--MAT")
        self.root.geometry("800x600")

        # تحويل النافذة لدعم DnD
        self.text_area = tk.Text(self.root, wrap='word', undo=True, font=('Helvetica', 14))
        self.text_area.pack(expand=1, fill='both', padx=10, pady=10)
        
        self.highlighter = SyntaxHighlighter(self.text_area, language="python")
        self.text_area.bind("<KeyRelease>", self.highlighter.highlight)
        
        # تعريف متغير الحالة
        self.status_var = tk.StringVar()
        
        # إنشاء شريط الحالة
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # إعداد القيمة الافتراضية لمتغير الحالة
        self.status_var.set("String matching functions: 0")

        # شريط التمرير
        self.scrollbar = tk.Scrollbar(self.text_area)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)

        # إنشاء شريط القائمة
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        

        # قائمة File
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_file_as)
        self.file_menu.add_command(label="Rename", command=self.rename_file)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # قائمة Edit
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        self.edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        self.edit_menu.add_separator()
        #self.edit_menu.add_command(label="Search", command=self.Search, accelerator="Ctrl+F")
        #self.edit_menu.add_command(label="replace", command=self.replace, accelerator="Ctrl+H")
        
        
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        self.file_path = None

        # ربط الأحداث الخاصة بالاختصارات
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-a>', lambda event: self.select_all())
        self.root.bind('<Control-f>', lambda event: self.search_window())  # لفتح نافذة البحث
        self.root.bind('<Control-h>', lambda event: self.open_replace_window())  # لفتح نافذة الاستبدال
        
        # إنشاء إطار علوي يحتوي على زري البحث والاستبدال
        #top_frame = tk.Frame(self.root)
        #top_frame.pack(side=tk.TOP, anchor='ne', pady=5, padx=5)  # محاذاة الإطار لأعلى يمين الشاشة

        # زر البحث (Search) داخل الإطار
        #search_btn = tk.Button(top_frame, text="Search", command=self.search_window)
        #search_btn.pack(side=tk.LEFT, padx=5)

    


        # دعم السحب والإفلات
        self.text_area.drop_target_register(DND_FILES)
        self.text_area.dnd_bind('<<Drop>>', self.on_file_drop)
        
        # ضبط البروتوكول لإغلاق التطبيق
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        #self.text_area = tk.Text(root)
        #self.text_area.pack()
        # قائمة العرض
        # إضافة قائمة العرض إلى شريط القائمة
        self.display_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.display_menu.add_command(label="RTL", command=self.set_rtl)
        self.display_menu.add_command(label="LTR", command=self.set_ltr)
        self.menu_bar.add_cascade(label="Display", menu=self.display_menu)

        
        self.text_area.bind("<<Selection>>", self.highlight_similar_words)
        
    
    
    def set_rtl(self):
        # إعداد علامة للنص ليتناسب مع الاتجاه من اليمين لليسار
        self.text_area.tag_remove('ltr', 1.0, 'end')  # إزالة العلامة المقابلة
        self.text_area.tag_configure('rtl', justify='right')
        self.text_area.tag_add('rtl', 1.0, 'end')  # إضافة العلامة للنص الحالي

    def set_ltr(self):
        # إعداد علامة للنص ليتناسب مع الاتجاه من اليسار لليمين
        self.text_area.tag_remove('rtl', 1.0, 'end')  # إزالة العلامة المقابلة
        self.text_area.tag_configure('ltr', justify='left')
        self.text_area.tag_add('ltr', 1.0, 'end')  # إضافة العلامة للنص الحالي
       



    def highlight_similar_words(self, event):
        try:
            selection = self.text_area.tag_ranges(tk.SEL)

            if selection:
                start_index, end_index = selection
                selected_word = self.text_area.get(start_index, end_index).strip()

                if selected_word:
                    self.text_area.tag_remove('highlight', '1.0', tk.END)
                    start = '1.0'
                    count = 0  # عداد الكلمات المتشابهة

                    while True:
                        start = self.text_area.search(selected_word, start, stopindex=tk.END)
                        if not start:
                            break
                        end = f"{start}+{len(selected_word)}c"
                        self.text_area.tag_add('highlight', start, end)
                        start = end
                        count += 1  # زيادة العداد

                    self.text_area.tag_config('highlight', background='lightblue')
                    
                    # تحديث العداد في شريط الحالة
                    self.status_var.set(f"String matching functions: {count}")
        except tk.TclError:
            pass






    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_path = None

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)

    def save_file(self):
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*")])
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))

    def rename_file(self):
        if self.file_path:
            new_name = filedialog.asksaveasfilename(defaultextension=".txt")
            if new_name:
                os.rename(self.file_path, new_name)
                self.file_path = new_name
        else:
            messagebox.showerror("Error", "No file to rename")

    def select_all(self):
        self.text_area.tag_add('sel', '1.0', 'end')

        
    def search_window(self):
        # إنشاء نافذة البحث كنافذة فرعية (Toplevel)
        self.search_win = tk.Toplevel(self.root)
        self.search_win.title("Search")
        self.search_win.geometry("400x150")
        self.search_win.attributes('-topmost', True)  # إبقاء النافذة في المقدمة

        # شريط الإدخال مع نص شفاف
        search_var = tk.StringVar()
        self.search_entry = ttk.Combobox(self.search_win, textvariable=search_var, font=('Helvetica', 12))
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)
        self.search_entry.insert(0, "Search...")  # النص الشفاف

        # إذا كان هناك نص محدد، نضعه في شريط الإدخال
        try:
            selected_text = self.text_area.selection_get()
            self.search_entry.set(selected_text)
        except:
            pass

        # ربط حدث التركيز لإزالة النص الشفاف
        self.search_entry.bind("<FocusIn>", lambda event: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Search..." else None)

        # قائمة منسدلة للكلمات التي تم البحث عنها مسبقًا
        if not hasattr(self, 'search_history'):
            self.search_history = []  # قائمة لحفظ الكلمات السابقة
        self.search_entry['values'] = self.search_history  # ربط القائمة المنسدلة بالتاريخ

        # زران للبحث السابق واللاحق (مثلثان)
        prev_button = tk.Button(self.search_win, text="▲", command=lambda: self.search_direction(search_var.get(), -1))
        next_button = tk.Button(self.search_win, text="▼", command=lambda: self.search_direction(search_var.get(), 1))
        prev_button.grid(row=1, column=0, padx=5, pady=5)
        next_button.grid(row=2, column=0, padx=5, pady=5)

        # زر "Search All" للبحث عن جميع التطابقات
        search_all_btn = tk.Button(self.search_win, text="Search All", command=lambda: self.search_all(search_var.get()))
        search_all_btn.grid(row=1, column=2, padx=10)

        # تحديث سجل البحث عند البحث
        def update_search_history(query):
            if query not in self.search_history:
                self.search_history.append(query)
                self.search_entry['values'] = self.search_history

        # إضافة الوظيفة لتحديث سجل البحث
        prev_button.config(command=lambda: [self.search_direction(search_var.get(), -1), update_search_history(search_var.get())])
        next_button.config(command=lambda: [self.search_direction(search_var.get(), 1), update_search_history(search_var.get())])
        search_all_btn.config(command=lambda: [self.search_all(search_var.get()), update_search_history(search_var.get())])

        # ربط اختصار Ctrl + F بفتح نافذة البحث
        self.root.bind('<Control-f>', lambda event: self.search_window())

    # تأكد من تعريف الوظيفة search_direction
    def search_direction(self, query, direction):
        # هنا يجب تعريف كيفية البحث عن النص في الاتجاه المطلوب
        pass

    # تأكد من تعريف الوظيفة search_all
    def search_all(self, query):
        # هنا يجب تعريف كيفية البحث عن كل التطابقات
        pass


    
    def search_direction(self, query, direction):
        content = self.text_area.get(1.0, tk.END)
        pos = self.text_area.search(query, tk.INSERT, backwards=(direction == -1))
    
        if pos:
            end_pos = f"{pos}+{len(query)}c"
            self.text_area.tag_remove('highlight', 1.0, tk.END)
            self.text_area.tag_add('highlight', pos, end_pos)
            self.text_area.tag_config('highlight', background='yellow')
            self.text_area.mark_set(tk.INSERT, end_pos)
        else:
            messagebox.showinfo("Not Found", "No more occurrences found.")
            
    def search_all(self, query):
        content = self.text_area.get(1.0, tk.END)
        start = 1.0
        found = False

        self.text_area.tag_remove('highlight', 1.0, tk.END)
        while True:
            pos = self.text_area.search(query, start, tk.END)
            if not pos:
                break
            found = True
            end_pos = f"{pos}+{len(query)}c"
            self.text_area.tag_add('highlight', pos, end_pos)
            start = end_pos

        self.text_area.tag_config('highlight', background='yellow')

        if not found:
            messagebox.showinfo("Not Found", "No occurrences found.")
            
    def open_replace_window(self):
        # تحقق مما إذا كانت نافذة الاستبدال موجودة بالفعل
        if hasattr(self, 'replace_window') and self.replace_window.winfo_exists():
            self.replace_window.lift()
            return

        # إنشاء نافذة جديدة
        self.replace_window = tk.Toplevel(self.root)
        self.replace_window.title("Replace")
        self.replace_window.geometry("400x200")
        self.replace_window.attributes('-topmost', True)

        # إعداد شريطي البحث والاستبدال
        self.search_var = tk.StringVar()
        self.replace_var = tk.StringVar()

        # شريط البحث
        self.search_entry = ttk.Combobox(self.replace_window, textvariable=self.search_var, font=('Helvetica', 12))
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)
        self.search_entry.set("Search...")
        self.search_entry.bind("<FocusIn>", lambda event: self.search_entry.set("") if self.search_entry.get() == "Search..." else None)
        self.search_entry.bind("<FocusOut>", lambda event: self.search_entry.set("Search...") if self.search_entry.get() == "" else None)

        # شريط الاستبدال
        self.replace_entry = ttk.Combobox(self.replace_window, textvariable=self.replace_var, font=('Helvetica', 12))
        self.replace_entry.grid(row=1, column=1, padx=10, pady=10)
        self.replace_entry.set("Replace...")
        self.replace_entry.bind("<FocusIn>", lambda event: self.replace_entry.set("") if self.replace_entry.get() == "Replace..." else None)
        self.replace_entry.bind("<FocusOut>", lambda event: self.replace_entry.set("Replace...") if self.replace_entry.get() == "" else None)


        # زر لعكس المدخلات
        swap_button = ttk.Button(self.replace_window, text="⇆", command=self.swap_inputs)
        swap_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5)

        # زر لاستبدال الكلمة المحددة
        replace_button = ttk.Button(self.replace_window, text="Replace", command=self.replace_one)
        replace_button.grid(row=2, column=0, padx=10, pady=10)

        # زر لاستبدال جميع التطابقات
        replace_all_button = ttk.Button(self.replace_window, text="Replace All", command=self.replace_all)
        replace_all_button.grid(row=2, column=1, padx=10, pady=10)

        # إضافة قائمة منسدلة لعرض الكلمات السابقة
        if not hasattr(self, 'previous_searches'):
            self.previous_searches = []
        self.search_entry['values'] = self.previous_searches
        self.replace_entry['values'] = self.previous_searches


    def update_search_history(self, text):
        if text and text not in self.previous_searches:
            self.previous_searches.append(text)
            self.search_entry['values'] = self.previous_searches
            self.replace_entry['values'] = self.previous_searches

    def swap_inputs(self):
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        self.search_var.set(replace_text)
        self.replace_var.set(search_text)
        
            # زر لاستبدال الكلمة المحددة
        replace_button = ttk.Button(self.replace_window, text="Replace", command=self.replace_one)
        replace_button.grid(row=2, column=0, padx=10, pady=10)

        # زر لاستبدال جميع التطابقات
        replace_all_button = ttk.Button(self.replace_window, text="Replace All", command=self.replace_all)
        replace_all_button.grid(row=2, column=1, padx=10, pady=10)
        
    def replace_one(self):
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        content = self.text_area.get(1.0, tk.END)

        index = content.find(search_text)
        if index != -1:
            start = f"1.0+{index}c"
            end = f"{start}+{len(search_text)}c"
            self.text_area.delete(start, end)
            self.text_area.insert(start, replace_text)
            self.update_search_history(search_text)  # استدعاء مع النص المطلوب
            # تحديث عداد الاستبدالات
            self.status_var.set(f"One word has been replaced.'{search_text}' In a word '{replace_text}'")
        else:
            messagebox.showinfo("Not Found", f"'{search_text}' not found.")


    def replace_all(self):
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        content = self.text_area.get(1.0, tk.END)
        
        count = content.count(search_text)
        # استبدال جميع التطابقات
        if search_text in content:
            new_content = content.replace(search_text, replace_text)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, new_content)
            self.update_search_history(search_text)
            # تحديث عداد الاستبدالات
            self.status_var.set(f"Replaced{count} Words '{search_text}' In a word '{replace_text}'")
        else:
            messagebox.showinfo("Not Found", f"'{search_text}' not found.")
            
            


    def on_file_drop(self, event):
        files = self.root.tk.splitlist(event.data)  # دعم سحب عدة ملفات
        for file_path in files:
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.insert(tk.END, f"\n\n--- {file_path} ---\n{content}")
                self.file_path = file_path


    def undo(self):
        try:
            self.text_area.edit_undo()
        except:
            pass

    def redo(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit without saving?"):
            self.root.destroy()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = TextEditor(root)
    root.mainloop()
    
