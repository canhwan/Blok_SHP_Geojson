#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import geopandas as gpd
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys

# =============================
# FUNGSI: generate_d_blok
# =============================
def generate_d_blok(filename, d_blok_value):
    filename_base = Path(filename).stem[:10]
    d_blok_str = str(d_blok_value).strip()

    if d_blok_str == "" or d_blok_str.lower() == "nan":
        return f"{filename_base}001"

    if len(d_blok_str) >= 13:
        return d_blok_str[:13]

    if len(d_blok_str) > 2:
        suffix = d_blok_str[-2:]
        new_val = f"{filename_base}{suffix}"
        return new_val[:13]

    urutan = str(d_blok_str).zfill(3)
    new_val = f"{filename_base}{urutan}"
    return new_val[:13]

# =============================
# FUNGSI KONVERSI
# =============================
def konversi_shp_ke_geojson(root_path, progress_bar, status_label):
    output_root = root_path / "OUTPUT_GEOJSON_4326"
    output_root.mkdir(exist_ok=True)

    shp_files = [p for p in root_path.rglob("*.shp") if "bl" in p.name.lower()]
    total_files = len(shp_files)

    if total_files == 0:
        messagebox.showinfo("Info", "Tidak ada file SHP dengan 'bl' ditemukan.")
        return

    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0

    for idx, shp_path in enumerate(shp_files, start=1):
        status_label.config(text=f"Mengonversi: {shp_path.name}")
        try:
            gdf = gpd.read_file(shp_path)

            blok_col = None
            for col in gdf.columns:
                if col.lower() == "d_blok":
                    blok_col = col
                    break

            if blok_col is None:
                continue

            gdf["d_blok_fix"] = gdf[blok_col].apply(lambda x: generate_d_blok(shp_path.name, x))
            gdf = gdf.rename(columns={blok_col: "blok"})
            gdf["blok"] = gdf["d_blok_fix"]
            gdf = gdf.drop(columns=["d_blok_fix"])
            gdf["nop"] = gdf["blok"].astype(str) + "0   0"

            if gdf.crs is None:
                gdf = gdf.set_crs(epsg=23849, allow_override=True)
            gdf_4326 = gdf.to_crs(epsg=4326)

            folder1 = shp_path.parents[0].name if len(shp_path.parents) >= 1 else ""
            folder2 = shp_path.parents[1].name if len(shp_path.parents) >= 2 else ""
            extra_name = f"_{folder2}_{folder1}" if folder2 and folder1 else (f"_{folder1}" if folder1 else "")

            output_file = output_root / f"{shp_path.stem}{extra_name}_4326.geojson"
            gdf_4326.to_file(output_file, driver="GeoJSON")

        except Exception as e:
            print(f"❌ Error di {shp_path.name}: {e}")
        finally:
            progress_bar["value"] = idx
            progress_bar.update()

    status_label.config(text="Selesai ✅")
    messagebox.showinfo("Selesai", f"Konversi selesai!\nFile tersimpan di:\n{output_root}")

# =============================
# FUNGSI EVENT GUI
# =============================
def pilih_folder(entry_field):
    folder_selected = filedialog.askdirectory(title="Pilih folder root SHP")
    if folder_selected:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, folder_selected)

def mulai_proses(entry_field, progress_bar, status_label):
    folder_path = entry_field.get().strip()
    if not folder_path:
        messagebox.showwarning("Peringatan", "Silakan pilih folder SHP terlebih dahulu.")
        return

    root_path = Path(folder_path)
    if not root_path.exists():
        messagebox.showerror("Error", "Folder tidak ditemukan.")
        return

    # Jalankan di thread terpisah agar GUI tidak freeze
    thread = threading.Thread(target=konversi_shp_ke_geojson, args=(root_path, progress_bar, status_label))
    thread.start()

# =============================
# GUI SETUP
# =============================
def main_gui():
    app = tk.Tk()
    app.title("Konversi SHP ➜ GEOJSON (WGS84)")
    app.geometry("520x250")
    app.resizable(False, False)

    # JUDUL
    tk.Label(app, text="KONVERSI SHP ➜ GEOJSON", font=("Arial", 14, "bold")).pack(pady=10)

    # FRAME INPUT
    frame = tk.Frame(app)
    frame.pack(pady=10)

    tk.Label(frame, text="Pilih Folder SHP BLOK:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
    folder_entry = tk.Entry(frame, width=45)
    folder_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(frame, text="Pilih", command=lambda: pilih_folder(folder_entry)).grid(row=0, column=2, padx=5, pady=5)

    # PROGRESS BAR
    progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=15)

    # STATUS LABEL
    status_label = tk.Label(app, text="", font=("Arial", 9), fg="gray")
    status_label.pack()

    # TOMBOL MULAI
    tk.Button(app, text="Mulai Konversi", bg="#2e7d32", fg="white", width=20,
              command=lambda: mulai_proses(folder_entry, progress, status_label)).pack(pady=15)

    app.mainloop()

# =============================
# JALANKAN PROGRAM
# =============================
if __name__ == "__main__":
    main_gui()


# In[ ]:




