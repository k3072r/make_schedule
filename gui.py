import os,sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog




# 実行ボタン押下時の実行関数
def conductMain():
    text = ""

    filePath = entry1.get()
    if filePath:
        text += "ファイルパス：" + filePath

    if text:
        messagebox.showinfo("info", text)
    else:
        messagebox.showerror("error", "パスの指定がありません。")

