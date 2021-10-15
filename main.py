import openpyxl as px
import random
import os
import time
import threading
import getxl
import setxl
import make
from annealing import simulated_annealing
import calc_loss
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


def main():

    t1 = time.time()

    global bar_value

    filepath = "test.xlsm"
    wb = px.load_workbook(filename=filepath, keep_vba=True)
    schedule = getxl.get_schedule(wb)
    lessons = getxl.get_lessons(wb)
    students = getxl.get_students(wb)
    student_free_counts = getxl.student_free_count(students)
    sorted_free_count = getxl.free_count_bubble_sort(student_free_counts)
    teachers = getxl.get_teachers(wb)
    evacuations = []

    #講師の出勤可能なコマを取得
    teachers_free_days = []
    for teacher in schedule:
        name = teacher[0]
        days = teacher[1]
        free_list = make.get_schedule_free_list(days)
        teachers_free_days.append([name, free_list])
    
    bar_value += 1




    #高3を最優先
    #その後は希望講師が少ない授業から優先して配置
    #lessonsを一周見て、変更がなければ（条件を満たすコマが全て割り振られていれば）flagはFalseになり、先へ進む
    flag = True
    while flag:
        flag = False
        for lesson in lessons:
            if lesson[0] == "高3" or lesson[0] == "新高3" or lesson[0] == "高３" or lesson[0] == "新高３":
                if lesson[3] > 0:
                    (i, j, teacher_indice) = make.place(lesson, schedule, students, teachers)
                    if (i, j, teacher_indice) == (-1, -1, -1):
                        evacuations.append(lesson)
                        lessons.remove(lesson)
                    else:
                        schedule[teacher_indice][1][i][j][1] = ["lock", "lock", "lock"]
                    flag = True
        
    #高3以外を、スケジュールに余裕のない者から配置
    #入れられるコマが見つからない場合は、そのlessonを一旦evacuationsに退避
    for student in sorted_free_count:        
        flag = True
        while flag:
            flag = False
            for lesson in lessons:
                if lesson[3] > 0 and lesson[1] == student[0]:
                    (i, j, teacher_indice) = make.place(lesson, schedule, students, teachers)
                    if (i, j, teacher_indice) == (-1, -1, -1):
                        evacuations.append(lesson)
                        lessons.remove(lesson)
                    flag = True
                    break

    #evacuationsの中身を配置していく
    loop = True
    while loop:
        #evacuationsが空になったらループ脱出
        if evacuations == []:
            break

        for evacuation in evacuations:

            #割り振った授業はevacuationsから削除
            if evacuation[3] <= 0:
                lessons.append(evacuation)
                evacuations.remove(evacuation)
                continue

            name = evacuation[1]
            hopes = evacuation[4]

            high3 = False
            if evacuation[0] == "高3":
                high3 = True

            student_indice = make.get_index(name, students)
            student_free_list = make.get_student_free_list(students[student_indice][1])
                
            moved = False

            #希望講師を見ていく
            for hope in hopes:

                if moved:
                    break

                teacher_indice = make.get_index(hope, schedule)
                teacher_free_list = teachers_free_days[teacher_indice][1]

                #講師と生徒の（attendを加えた）空きコマの積集合（授業入れられるとこ）
                intersection = list(set(student_free_list) & set(teacher_free_list))

                while len(intersection) > 0:

                    #生徒の空きコマをランダムに取得（そこに割り当てる）
                    rndm = random.random()
                    k = int((rndm * 100000) % len(intersection))
                    (i, j) = intersection[k]

                    #高3の場合の処理
                    if high3:
                        #attendかfreeのコマにのみ割り当て可能
                        if teachers[teacher_indice][1][i][j] == "attend" or teachers[teacher_indice][1][i][j] == "free":
                            #割り当て先のコマの授業を移動
                            b1 = make.random_move(i, j, 0, teacher_indice, student_indice, evacuation, schedule, students, teachers)
                            b2 = make.random_move(i, j, 1, teacher_indice, student_indice, evacuation, schedule, students, teachers)

                            #移動完了したら、そこにevacuationを割り当て
                            if b1 & b2:
                                make.place(evacuation, schedule, students, teachers)
                                moved = True
                            else:
                                intersection.remove((i, j))

                    #高3以外の場合の処理
                    else:
                        if teachers[teacher_indice][1][i][j] == "attend" or teachers[teacher_indice][1][i][j] == "free":
                            #上下の選択（後で変えるかも）
                            h = 0
                            if schedule[teacher_indice][1][i][j][0] != ["free", "free", "free"]:
                                h = 1

                            if schedule[teacher_indice][1][i][j][h] == ["free", "free", "free"]:
                                b1 = True
                            elif schedule[teacher_indice][1][i][j][h] == ["lock", "lock", "lock"]:
                                b1 = False
                            else:
                                b1 = make.random_move(i, j, h, teacher_indice, student_indice, lessons, schedule, students, teachers)
                            if b1:
                                make.place(evacuation, schedule, students, teachers)
                                moved = True
                                break
                            else:
                                intersection.remove((i, j))

                # end while

            if not moved:
                raise Exception("register failed! teachers are not found. " + evacuation[1] + " " + evacuation[2])

        # end for

    # end while
    bar_value += 1

    setxl.set_schedule(wb, schedule)
    setxl.set_students(wb, students)

    loss1 = calc_loss.all_loss_hoperank(schedule, lessons)
    loss2 = calc_loss.all_loss_student_sparse(students)
    loss3 = calc_loss.all_loss_free_teacher_exist(teachers)
    loss4 = calc_loss.all_loss_student_count(students)

    print("loss hoperank = " + str(loss1))
    print("loss sparse = " + str(loss2))
    print("loss count = " + str(loss4))
    print("loss free_t = " + str(loss3))

    temp_max = 2000
    temp_min = 0.05
    iteration = 5
    temp_diff = 0.97
    temp = temp_max
    candidates = make.get_not_locked_frames(schedule)

    while temp >= temp_min:

        (schedule, students, teachers) = simulated_annealing(schedule, students, teachers, lessons, candidates, iteration, temp)
        temp *= temp_diff
        bar_value += 1
        bar_var.set(bar_value)

    #end while

    print("-----------------")

    loss1 = calc_loss.all_loss_hoperank(schedule, lessons)
    loss2 = calc_loss.all_loss_student_sparse(students)
    loss3 = calc_loss.all_loss_free_teacher_exist(teachers)
    loss4 = calc_loss.all_loss_student_count(students)

    print("loss hoperank = " + str(loss1))
    print("loss sparse = " + str(loss2))
    print("loss count = " + str(loss4))
    print("loss free_t = " + str(loss3))

    print("time = " + str(time.time() - t1) + "sec")

    setxl.set_schedule(wb, schedule)
    setxl.set_students(wb, students)

    root_main.destroy()




# progressbarの表示用変数の値を変える関数
def getxl_progress_increment():
    global getxl_progress
    getxl_progress.set(getxl_progress.get() + 1)

def sa_progress_increment():
    global sa_progress
    sa_progress.set(sa_progress.get() + 1)




#実行押下後のGUIの処理
def gui_execute():
    #既存のフレームの消去
    frame1.destroy()
    frame2.destroy()
    frame3.tkraise()

    #プログレスバー
    bar = ttk.Progressbar(frame3, orient="horizontal", length=500, mode="determinate", variable=getxl_progress, maximum=8)
    bar.pack()

    #ラベル
    label = Label(frame3, textvariable="Excelの情報を取得中…")
    label.pack()



    



#エクセル取得から初期解生成への切り替え
def gui_toInitial():

    frame3.destroy()
    frame4.grid(row=2, column=1, sticky=E)

    #プログレスバー
    bar = ttk.Progressbar(frame4, orient="horizontal", length=500, mode="indeterminate", maximum=8)
    bar.pack()

    #ラベル
    label = Label(frame4, textvariable="初期解を生成中…")
    label.pack()


#初期解生成からSimulated Annealingへの切り替え
def gui_toSA():

    frame4.destroy()
    frame5.grid(row=2, column=1, sticky=E)

    #プログレスバー
    bar = ttk.Progressbar(frame5, orient="horizontal", length=500, mode="determinate", variable= sa_progress, maximum= 348)
    bar.pack()

    #温度を表すラベル
    temp_label = Label(frame5, textvariable=str(sa_progress.get()))
    temp_label.pack()









def show_gui2():

    global root2, frame3, frame4, frame5, getxl_progress, sa_progress, now_show_gui

    # rootの作成
    root2 = Tk()
    root2.title("サンプル")

    # プログレスバーの進捗を表すグローバル変数
    getxl_progress = IntVar(value=0)
    sa_progress = IntVar(value=0)

    #getxl中に表示するフレーム
    frame3 = ttk.Frame(root, padding=10)
    frame3.grid(row=2, column=1, sticky=E)

    #初期解生成中に表示するフレーム
    frame4 = ttk.Frame(root, padding=10)
    frame4.grid(row=2, column=1, sticky=E)

    #Simulated Annealing中に表示するフレーム
    frame5 = ttk.Frame(root, padding=10)
    frame5.grid(row=2, column=1, sticky=E)

    root.mainloop()

    now_show_gui = True

# ファイル指定の関数
def filedialog_clicked():
    fTyp = [("", "*")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    entry1.set(iFilePath)

# 実行ボタン押下時の実行関数
def conductMain():
    text = ""

    filePath = entry1.get()
    if filePath:
        text += "ファイルパス：" + filePath

    if text:
        root.quit()

    root.destroy()

#プログレスバーの進捗更新用関数
def refresh_bar():
    global bar_var
    bar_var.set(bar_value)
    root_main.after(50, refresh_bar)


# rootの作成
root = Tk()
root.title("ファイル選択")

# Frame1の作成
frame1 = ttk.Frame(root, padding=10)
frame1.grid(row=2, column=1, sticky=E)

# 「ファイル参照」ラベルの作成
IFileLabel = ttk.Label(frame1, text="ファイル参照＞＞", padding=(5, 2))
IFileLabel.pack(side=LEFT)

# 「ファイル参照」エントリーの作成
entry1 = StringVar()
IFileEntry = ttk.Entry(frame1, textvariable=entry1, width=30)
IFileEntry.pack(side=LEFT)

# 「ファイル参照」ボタンの作成
IFileButton = ttk.Button(frame1, text="参照", command=filedialog_clicked)
IFileButton.pack(side=LEFT)

# Frame2の作成
frame2 = ttk.Frame(root, padding=10)
frame2.grid(row=5,column=1,sticky=W)

# 実行ボタンの設置
button1 = ttk.Button(frame2, text="実行", command=conductMain)
button1.pack(fill = "x", padx=30, side = "left")

# キャンセルボタンの設置
#button2 = ttk.Button(frame2, text=("閉じる"), command=quit)
#button2.pack(fill = "x", padx=30, side = "left")

#getxl中に表示するフレーム
frame3 = ttk.Frame(root, padding=10)


root.mainloop()

thread1 = threading.Thread(target=main)
thread1.start()

#実行中のroot
root_main = Tk()
root_main.title("探索中...")

# プログレスバーの進捗を表すグローバル変数
bar_value = 0
bar_var = IntVar(value= bar_value)

#プログレスバー
bar = ttk.Progressbar(root_main, orient="horizontal", length=500, mode="determinate", variable=bar_var, maximum=350)
bar.pack()

#refresh_bar()

root_main.mainloop()