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

    global bar_var, bar_value, text, label_var

    wb = px.load_workbook(filename=text, keep_vba=True)
    bar_var.set(70)
    schedule = getxl.get_schedule(wb)
    bar_var.set(140)
    lessons = getxl.get_lessons(wb)
    bar_var.set(210)
    students = getxl.get_students(wb)
    bar_var.set(280)
    student_free_counts = getxl.student_free_count(students)
    sorted_free_count = getxl.free_count_bubble_sort(student_free_counts)
    teachers = getxl.get_teachers(wb)
    bar_var.set(350)
    evacuations = []

    #講師の出勤可能なコマを取得
    teachers_free_days = []
    for teacher in schedule:
        name = teacher[0]
        days = teacher[1]
        free_list = make.get_schedule_free_list(days)
        teachers_free_days.append([name, free_list])
    
    

    bar_var.set(0)
    label_var.set("初期解を生成中...")


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
    iteration = 1000
    temp_diff = 0.97
    temp = temp_max
    candidates = make.get_not_locked_frames(schedule)

    sum_time = 0

    while temp >= temp_min:

        t1 = time.time()

        (schedule, students, teachers) = simulated_annealing(schedule, students, teachers, lessons, candidates, iteration, temp)
        temp *= temp_diff
        bar_value += 1
        bar_var.set(bar_value)

        t2 = time.time() - t1
        sum_time += t2
        prediction = int((sum_time / bar_value) * (348 - bar_value))
        label_var.set("最適解を探索中...　残り時間：" + str(prediction) + "sec")

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

    label_var.set("Excelファイルに書き出し中...")
    bar_var.set(0)

    setxl.set_schedule(wb, schedule)
    bar_var.set(175)
    setxl.set_students(wb, students)
    bar_var.set(350)

    root_main.quit()





# ファイル指定の関数
def filedialog_clicked():
    fTyp = [("", "*")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    entry1.set(iFilePath)

# 実行ボタン押下時の実行関数
def conductMain():
    global text

    #text = entry1.get()

    if text != "":
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
text = "test.xlsm"   # 参照したパス

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

if text != "":

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

    #ラベル
    label_var = StringVar()
    label_var.set("Excelデータを取得中...")
    label = ttk.Label(root_main, textvariable= label_var)
    label.pack()

    #refresh_bar()

    root_main.mainloop()