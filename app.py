
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------- Global Variables ----------------

df = pd.DataFrame()
chart_canvas = None


# ---------------- Load Dataset ----------------

def load_file():
    global df

    file_path = filedialog.askopenfilename(
        title="Select a dataset",
        filetypes=[
            ("CSV and Excel files", "*.csv *.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
        ],
    )

    if not file_path:
        return

    try:
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        if df.empty:
            messagebox.showwarning(
                "Empty Dataset",
                "The selected file contains no data."
            )
            return

        show_data()
        show_summary()

        status_label.config(
            text=f"Loaded: {file_path.split('/')[-1]}"
        )

    except Exception as e:
        messagebox.showerror("File Error", str(e))


# ---------------- Display Dataset ----------------

def show_data():
    tree.delete(*tree.get_children())

    cols = list(df.columns)
    tree["columns"] = cols
    tree["show"] = "headings"

    for col in cols:
        tree.heading(col, text=str(col))
        tree.column(
            col,
            width=120,
            minwidth=80,
            anchor="w"
        )

    for _, row in df.head(100).iterrows():
        values = [
            "" if pd.isna(value) else str(value)
            for value in row
        ]
        tree.insert("", "end", values=values)


# ---------------- Dataset Summary ----------------

def show_summary():
    summary_text.config(state="normal")
    summary_text.delete("1.0", tk.END)

    summary_text.insert(tk.END, "DATASET SUMMARY\n")
    summary_text.insert(tk.END, "=" * 40 + "\n")
    summary_text.insert(tk.END, f"Rows: {df.shape[0]}\n")
    summary_text.insert(tk.END, f"Columns: {df.shape[1]}\n\n")

    summary_text.insert(tk.END, "DATA TYPES\n")
    summary_text.insert(tk.END, "-" * 40 + "\n")
    summary_text.insert(tk.END, df.dtypes.to_string())

    summary_text.insert(tk.END, "\n\nMISSING VALUES\n")
    summary_text.insert(tk.END, "-" * 40 + "\n")
    summary_text.insert(
        tk.END,
        df.isnull().sum().to_string()
    )

    summary_text.insert(tk.END, "\n\nSTATISTICAL SUMMARY\n")
    summary_text.insert(tk.END, "-" * 40 + "\n")
    summary_text.insert(
        tk.END,
        df.describe(include="all").to_string()
    )

    summary_text.config(state="disabled")


# ---------------- Data Visualization ----------------

def plot_chart():
    global chart_canvas

    if df.empty:
        messagebox.showwarning(
            "No Data",
            "Please import a dataset first."
        )
        return

    # Case-insensitive column matching
    column_lookup = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    sales_col = column_lookup.get("sales")
    profit_col = column_lookup.get("profit")

    if sales_col is None and profit_col is None:
        messagebox.showwarning(
            "Columns Not Found",
            "The dataset must contain a Sales or Profit column."
        )
        return

    chart_data = df.copy()
    available = []

    for name, col in [
        ("Sales", sales_col),
        ("Profit", profit_col),
    ]:
        if col is not None:
            chart_data[col] = pd.to_numeric(
                chart_data[col],
                errors="coerce"
            )

            if chart_data[col].notna().any():
                available.append((name, col))

    if not available:
        messagebox.showwarning(
            "Invalid Data",
            "No numeric values found in Sales or Profit."
        )
        return

    # Remove the previous graph
    if chart_canvas is not None:
        chart_canvas.get_tk_widget().destroy()
        chart_canvas = None

    # Create the graph
    fig = Figure(figsize=(9, 4.5), dpi=100)
    ax = fig.add_subplot(111)

    for name, col in available:
        ax.plot(
            range(len(chart_data)),
            chart_data[col],
            marker="o",
            markersize=3,
            linewidth=1.8,
            label=name
        )

    ax.set_title(
        "Sales and Profit Analysis",
        fontsize=14,
        pad=12
    )
    ax.set_xlabel("Row Index")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.35)

    fig.tight_layout()

    chart_canvas = FigureCanvasTkAgg(
        fig,
        master=chart_frame
    )

    chart_canvas.draw()

    chart_canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )


# ---------------- Main Window ----------------

root = tk.Tk()
root.title("Python Data Analytics App")
root.geometry("1100x750")
root.minsize(800, 550)


# ---------------- Scrollable Container ----------------

outer_frame = ttk.Frame(root)
outer_frame.pack(fill="both", expand=True)

main_canvas = tk.Canvas(
    outer_frame,
    highlightthickness=0
)

main_scrollbar = ttk.Scrollbar(
    outer_frame,
    orient="vertical",
    command=main_canvas.yview
)

main_canvas.configure(
    yscrollcommand=main_scrollbar.set
)

main_scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

content_frame = ttk.Frame(main_canvas, padding=10)

content_window = main_canvas.create_window(
    (0, 0),
    window=content_frame,
    anchor="nw"
)


def update_scroll_region(event=None):
    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )


def resize_content(event):
    main_canvas.itemconfigure(
        content_window,
        width=event.width
    )


content_frame.bind(
    "<Configure>",
    update_scroll_region
)

main_canvas.bind(
    "<Configure>",
    resize_content
)


# Mouse-wheel scrolling

def mousewheel_scroll(event):
    if event.delta:
        main_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


def linux_scroll_up(event):
    main_canvas.yview_scroll(-1, "units")


def linux_scroll_down(event):
    main_canvas.yview_scroll(1, "units")


main_canvas.bind_all(
    "<MouseWheel>",
    mousewheel_scroll
)

main_canvas.bind_all(
    "<Button-4>",
    linux_scroll_up
)

main_canvas.bind_all(
    "<Button-5>",
    linux_scroll_down
)


# ==================================================
# IMPORTANT: ALL DASHBOARD WIDGETS USE content_frame
# AND ARE CREATED IN THE DESIRED DISPLAY ORDER.
# ==================================================


# 1. Dashboard Title

title_label = ttk.Label(
    content_frame,
    text="Data Analytics Dashboard",
    font=("Arial", 20, "bold")
)

title_label.pack(pady=10)


# 2. Import and Visualization Buttons

button_frame = ttk.Frame(content_frame)
button_frame.pack(fill="x", pady=5)

ttk.Button(
    button_frame,
    text="Import CSV / Excel",
    command=load_file
).pack(side="left", padx=5)

ttk.Button(
    button_frame,
    text="Show Sales & Profit Chart",
    command=plot_chart
).pack(side="left", padx=5)


# 3. Dataset Status

status_label = ttk.Label(
    content_frame,
    text="Please import a CSV or Excel dataset."
)

status_label.pack(anchor="w", padx=5, pady=5)


# 4. Dataset Preview

preview_frame = ttk.LabelFrame(
    content_frame,
    text="Dataset Preview (First 100 Rows)"
)

preview_frame.pack(
    fill="both",
    expand=True,
    pady=5
)

tree = ttk.Treeview(
    preview_frame,
    show="headings",
    height=8
)

tree_scroll_y = ttk.Scrollbar(
    preview_frame,
    orient="vertical",
    command=tree.yview
)

tree_scroll_x = ttk.Scrollbar(
    preview_frame,
    orient="horizontal",
    command=tree.xview
)

tree.configure(
    yscrollcommand=tree_scroll_y.set,
    xscrollcommand=tree_scroll_x.set
)

tree.grid(row=0, column=0, sticky="nsew")
tree_scroll_y.grid(row=0, column=1, sticky="ns")
tree_scroll_x.grid(row=1, column=0, sticky="ew")

preview_frame.rowconfigure(0, weight=1)
preview_frame.columnconfigure(0, weight=1)


# 5. Dataset Insights and Statistics

summary_frame = ttk.LabelFrame(
    content_frame,
    text="Dataset Insights and Statistics"
)

summary_frame.pack(
    fill="both",
    expand=True,
    pady=5
)

summary_text = tk.Text(
    summary_frame,
    height=12,
    wrap="none",
    font=("Consolas", 10)
)

summary_scroll = ttk.Scrollbar(
    summary_frame,
    orient="vertical",
    command=summary_text.yview
)

summary_text.configure(
    yscrollcommand=summary_scroll.set
)

summary_text.pack(
    side="left",
    fill="both",
    expand=True
)

summary_scroll.pack(
    side="right",
    fill="y"
)

summary_text.config(state="disabled")


# 6. Data Visualization -- ALWAYS BELOW SUMMARY

chart_frame = ttk.LabelFrame(
    content_frame,
    text="Data Visualization"
)

chart_frame.pack(
    fill="both",
    expand=True,
    pady=5
)

chart_frame.configure(height=450)

# Keep the chart frame at its configured height
chart_frame.pack_propagate(False)

chart_canvas = None


# ---------------- Start Application ----------------

root.mainloop()
