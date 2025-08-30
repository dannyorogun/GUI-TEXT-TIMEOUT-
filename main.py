import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('dangerous writer')
        self.geometry('500x500')
        self.minsize(700, 500)
        self.timeout_seconds = 5
        status = ttk.Frame(self)
        status.pack(side="bottom", fill="x")
        self.words_label = ttk.Label(status, text="0 words", anchor="w")
        self.words_label.pack(side="left", padx=(10, 0))
        self.timer_label = ttk.Label(status, text="⏳ 0.0s", width=12, anchor="w")
        self.timer_label.pack(side="left")
        self.last_type_time = time.time()
        self.grace_enabled = tk.BooleanVar(value=True)
        self._start_timer_loop()



        # Container for editor + scrollbar
        editor_wrap = ttk.Frame(self)
        editor_wrap.pack(side="top", fill="both", expand=True)

        self.text = tk.Text(
            editor_wrap,
            wrap="word",
            font=("TkFixedFont", 14),
            padx=16, pady=16
        )
        self.text.pack(side="left", fill="both", expand=True)
        self.text.focus_set()
        self.text.bind("<Key>", self._on_keypress, add="+")
        # Start with a small intro text and move cursor to end
        self.text.insert("1.0", "Start typing. If you stop for 5s, everything gets erased.\n\n")
        self.text.mark_set("insert", "end")
        self._reset_last_type()

        scroll = ttk.Scrollbar(editor_wrap, command=self.text.yview)
        scroll.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scroll.set)



        # Update word count when text changes
        self.text.bind("<<Modified>>", self._on_modified, add="+")
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=(6, 0))
        ttk.Label(top, text="Idle Timeout (sec):").pack(side="left")
        self.timeout_var = tk.IntVar(value=5)
        self.timeout_spin = ttk.Spinbox(
            top, from_=3, to=60, textvariable=self.timeout_var, width=4, command=self._update_timeout
        )
        self.timeout_spin.pack(side="left", padx=(6, 12))
        self.export_btn = ttk.Button(top, text="Export…", command=self._export_text)
        self.export_btn.pack(side="right")
        self.new_btn = ttk.Button(top, text="New Session", command=self._new_session)
        self.new_btn.pack(side="right", padx=(0, 8))

        self.warn_threshold = 2.0

        # Add a checkbox in the top bar:
        self.grace_check = ttk.Checkbutton(top, text="1s grace after typing resumes", variable=self.grace_enabled)
        self.grace_check.pack(side="left", padx=(0, 12))



    def _start_timer_loop(self):
        self._tick()
        self.after(100, self._start_timer_loop)  # 10 times/sec


    def _obliterate(self):
        self.text.delete("1.0", "end")
        self.last_type_time = time.time()  # reset so it doesn't loop-wipe

    def _on_keypress(self, event):
        # ignore modifier-only keys if you like, but simple works too
        self._reset_last_type()



    def _on_modified(self, event):
        # Reset the modified flag so this event keeps firing
        self.text.edit_modified(False)

        # Update word count
        content = self.text.get("1.0", "end-1c")
        words = len([w for w in content.split() if w.strip()])
        self.words_label.config(text=f"{words} word{'s' if words != 1 else ''}")


    def _update_timeout(self):
        try:
            val = int(self.timeout_var.get())
            if not (3 <= val <= 60):
                raise ValueError
            self.timeout_seconds = val
        except Exception:
            self.timeout_var.set(5)
            self.timeout_seconds = 5

    def _new_session(self):
        if messagebox.askyesno("New Session", "Clear text and restart?"):
            self.text.delete("1.0", "end")
            self._reset_last_type()

    def _export_text(self):
        content = self.text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showinfo("Nothing to export", "There's no text to export yet.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Text",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown", "*.md"), ("All files", "*.*")],
            initialfile="dangerous_writer_export.txt"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _reset_last_type(self):
        self.last_type_time = time.time()
        if self.grace_enabled.get():
            self.last_type_time += 1.0  # tiny buffer after resuming

    def _tick(self):
        remaining = self.timeout_seconds - (time.time() - self.last_type_time)
        self.timer_label.config(text=f"⏳ {max(0.0, remaining):.1f}s")
        if remaining <= 0:
            self._obliterate()


if __name__ == '__main__':
    App().mainloop()


