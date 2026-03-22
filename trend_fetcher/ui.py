from __future__ import annotations

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .downloader import TARGET_BARS, download_ticker_csv, normalize_ticker


class TrendFetcherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("GA-ML Trend Fetcher")
        self.root.geometry("620x320")
        self.root.minsize(520, 280)

        self.ticker_var = tk.StringVar()
        self.folder_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.status_var = tk.StringVar(value=f"Exports the latest {TARGET_BARS} trading bars for one ticker.")
        self.is_busy = False

        self._build_layout()

    def _build_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        title = ttk.Label(frame, text="GA-ML Trend Fetcher", font=("Helvetica", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        description = ttk.Label(
            frame,
            text="Enter one ticker and choose a save folder. The app creates a CSV for the GA-ML web trend analyzer.",
            wraplength=560,
            justify="left",
        )
        description.grid(row=1, column=0, sticky="w", pady=(8, 18))

        form = ttk.Frame(frame)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)

        ttk.Label(form, text="Ticker").grid(row=0, column=0, sticky="w")
        ticker_entry = ttk.Entry(form, textvariable=self.ticker_var)
        ticker_entry.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        ticker_entry.focus_set()

        ttk.Label(form, text="Save folder").grid(row=2, column=0, sticky="w")

        folder_row = ttk.Frame(form)
        folder_row.grid(row=3, column=0, sticky="ew", pady=(6, 18))
        folder_row.columnconfigure(0, weight=1)

        folder_entry = ttk.Entry(folder_row, textvariable=self.folder_var)
        folder_entry.grid(row=0, column=0, sticky="ew")

        browse_button = ttk.Button(folder_row, text="Choose folder", command=self.pick_folder)
        browse_button.grid(row=0, column=1, padx=(10, 0))

        action_row = ttk.Frame(frame)
        action_row.grid(row=3, column=0, sticky="w")

        self.download_button = ttk.Button(action_row, text="Download CSV", command=self.start_download)
        self.download_button.grid(row=0, column=0, sticky="w")

        note = ttk.Label(
            frame,
            text="Output columns: symbol, date, open, high, low, close, adj_close, volume",
            wraplength=560,
            justify="left",
        )
        note.grid(row=4, column=0, sticky="w", pady=(16, 10))

        status = ttk.Label(frame, textvariable=self.status_var, wraplength=560, justify="left")
        status.grid(row=5, column=0, sticky="w")

    def pick_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder_var.get() or str(Path.home()))
        if selected:
            self.folder_var.set(selected)

    def start_download(self) -> None:
        if self.is_busy:
            return

        ticker = normalize_ticker(self.ticker_var.get())
        folder = self.folder_var.get().strip()

        if not ticker:
            messagebox.showerror("Missing ticker", "Enter a ticker first.")
            return
        if not folder:
            messagebox.showerror("Missing folder", "Choose a save folder first.")
            return

        self.is_busy = True
        self.download_button.state(["disabled"])
        self.status_var.set(f"Downloading {ticker} daily data...")

        worker = threading.Thread(target=self._run_download, args=(ticker, folder), daemon=True)
        worker.start()

    def _run_download(self, ticker: str, folder: str) -> None:
        try:
            result = download_ticker_csv(ticker, folder)
            self.root.after(0, lambda: self._finish_success(result.output_path, result.row_count, result.latest_date))
        except Exception as error:  # noqa: BLE001
            self.root.after(0, lambda: self._finish_error(str(error)))

    def _finish_success(self, output_path: Path, row_count: int, latest_date: str) -> None:
        self.is_busy = False
        self.download_button.state(["!disabled"])
        self.status_var.set(f"Saved {row_count} rows. Latest market date: {latest_date}")
        messagebox.showinfo("Download complete", f"CSV saved to:\n{output_path}")

    def _finish_error(self, message: str) -> None:
        self.is_busy = False
        self.download_button.state(["!disabled"])
        self.status_var.set("Download failed. Check the error message and try again.")
        messagebox.showerror("Download failed", message)


def launch() -> None:
    root = tk.Tk()
    root.configure(bg="#f5f2e8")
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    app = TrendFetcherApp(root)
    root.mainloop()
