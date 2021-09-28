import openpyxl as px
import random
import getxl
import make
import calc_loss

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
                        b1 = make.rand_move(i, j, 0, teacher_indice, evacuation, schedule, students, teachers)
                        b2 = make.rand_move(i, j, 1, teacher_indice, evacuation, schedule, students, teachers)

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

                        b1 = make.rand_move(i, j, h, teacher_indice, lessons, schedule, students, teachers)
                        if b1:
                            make.place(evacuation, schedule, students, teachers)
                            moved = True
                        else:
                            intersection.remove((i, j))

            # end while

        if not moved:
            raise Exception("register failed! teachers are not found. " + evacuation[1] + " " + evacuation[2])

    # end for

# end while


loss = 0

loss1 = calc_loss.all_loss_hoperank(schedule, lessons)
loss2 = calc_loss.all_loss_student_sparse(students)
loss3 = calc_loss.all_loss_free_teacher_exist(teachers)

loss = loss1 + loss2 + loss3

print("loss from hope = " + str(loss1))
print("loss from sparse = " + str(loss2))
print("loss from free teacher = " + str(loss3))