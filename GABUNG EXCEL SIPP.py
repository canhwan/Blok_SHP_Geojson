#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplikasi GUI sederhana untuk menggabungkan semua file XLSX
di dalam satu folder DHKP menjadi satu file: hasil_gabungan.xlsx
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
import traceback
import sys


class DHKPMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GABUNG EXCEL")
        self.geometry("650x230")
        self.resizable(False, False)

        # Simpan folder terpilih
        self.folder_path: Path | None = None

        # Variabel untuk status bar
        self.status_var = tk.StringVar(value="Silakan pilih root folder yang akan digabung (berisi file-file .xlsx)")

        self._build_widgets()
        self._center_window()

    def _build_widgets(self):
        # Frame utama
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Judul
        title_label = ttk.Label(
            main_frame,
            text="GABUNG DOKUMEN EXCEL - BAPENDA KAB. MALANG",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

        # Label deskripsi
        desc_label = ttk.Label(
            main_frame,
            text="Pilih folder yang berisi beberapa file EXCEL (.xlsx) yang akan digabung:",
            font=("Segoe UI", 9)
        )
        desc_label.grid(row=1, column=0, columnspan=3, sticky="w")

        # Input folder (read-only) + tombol browse
        self.folder_entry_var = tk.StringVar(value="Belum ada folder yang dipilih")

        folder_entry = ttk.Entry(
            main_frame,
            textvariable=self.folder_entry_var,
            state="readonly",
            width=70
        )
        folder_entry.grid(row=2, column=0, columnspan=2, pady=(8, 8), sticky="we")

        browse_btn = ttk.Button(
            main_frame,
            text="Pilih Folder...",
            command=self.choose_folder
        )
        browse_btn.grid(row=2, column=2, padx=(8, 0), sticky="e")

        # Tombol proses
        self.process_btn = ttk.Button(
            main_frame,
            text="Proses Gabung",
            command=self.process_merge
        )
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=(10, 5))

        # Status bar
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
        status_label.grid(row=4, column=0, columnspan=3, sticky="we", pady=(15, 0))

        # Atur grid agar entry bisa melar
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)

    def _center_window(self):
        """Supaya window muncul di tengah layar."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def set_status(self, text: str):
        self.status_var.set(text)
        self.update_idletasks()

    def choose_folder(self):
        folder_selected = filedialog.askdirectory(
            title="Pilih root folder dokumen Excel (berisi file-file .xlsx)"
        )
        if not folder_selected:
            return

        self.folder_path = Path(folder_selected)
        self.folder_entry_var.set(str(self.folder_path))
        self.set_status("Folder dipilih. Siap proses gabung.")

    def process_merge(self):
        if self.folder_path is None:
            messagebox.showwarning(
                "Folder belum dipilih",
                "Silakan pilih dulu root folder yang berisi file EXCEL (.xlsx)."
            )
            return

        try:
            self.process_btn.config(state="disabled")
            self.set_status("Mencari file .xlsx di folder terpilih...")

            xlsx_files = list(self.folder_path.glob("*.xlsx"))

            if not xlsx_files:
                messagebox.showinfo(
                    "Tidak ada file",
                    "Tidak ditemukan file .xlsx di folder tersebut."
                )
                self.set_status("Tidak ada file .xlsx yang bisa digabung.")
                return

            df_all = []
            for f in xlsx_files:
                self.set_status(f"Membaca: {f.name}")
                self.update_idletasks()

                # Kalau ingin log di console juga:
                print(f"Membaca: {f}", file=sys.stdout)

                df = pd.read_excel(f)
                df_all.append(df)

            self.set_status("Menggabungkan semua data...")
            df_merge = pd.concat(df_all, ignore_index=True)

            output_file = self.folder_path / "hasil_gabungan.xlsx"

            self.set_status("Menyimpan hasil ke Excel...")
            df_merge.to_excel(output_file, index=False)

            self.set_status("Penggabungan selesai.")
            messagebox.showinfo(
                "Selesai",
                f"Penggabungan selesai!\n\nFile hasil:\n{output_file}"
            )

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(
                "Terjadi Kesalahan",
                f"Terjadi error saat proses penggabungan:\n{e}"
            )
            self.set_status("Terjadi kesalahan. Lihat pesan error.")

        finally:
            self.process_btn.config(state="normal")


def main():
    app = DHKPMergerApp()
    app.mainloop()


if __name__ == "__main__":
    main()


# In[1]:


get_ipython().system('jupyter nbconvert --to script')
GABUNG EXCEL SIPP.ipynb


# In[ ]:




