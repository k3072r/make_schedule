import openpyxl as px
import lesson as le     #希望講師
import student as st    #生徒スケジュール
import teacher as te    #教室時間割
import schedule as sc   #教室時間割
import make
import random

filepath = "test.xlsm"
wb = px.load_workbook(filename=filepath, keep_vba=True)

schedule = sc.get_schedule(wb)
lessons = le.get_lessons(wb)
students = st.get_students(wb)
student_free_counts = st.student_free_count(students)
sorted_free_count = st.free_count_bubble_sort(student_free_counts)
teachers = te.get_teachers(wb)
attends = te.teachers_attend_count(schedule)

evacuations = []



#高3を最優先
#その後は希望講師が少ない授業から優先して配置
#lessonsを一周見て、変更がなければ（条件を満たすコマが全て割り振られていれば）flagはFalseになり、先へ進む
flag = True
while flag:
    flag = False
    for lesson in lessons:
        if lesson[0] == "高3" or lesson[0] == "新高3" or lesson[0] == "高３" or lesson[0] == "新高３":
            if lesson[3] > 0:
                (i, j, teacher_indice) = make.place(lesson, schedule, students, teachers, attends)
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
                (i, j, teacher_indice) = make.place(lesson, schedule, students, teachers, attends)
                if (i, j, teacher_indice) == (-1, -1, -1):
                    evacuations.append(lesson)
                    lessons.remove(lesson)
                flag = True
                break

#evacuationsの中身を配置していく
for evacuation in evacuations:

    name = evacuation[1]
    hopes = evacuation[4]

    high3 = False
    if evacuation[0] == "高3":
        high3 = True

    student_indice = make.get_index(name, students)
    student_free_list = make.get_student_free_list(students[student_indice][1])
        

    for hope in hopes:
        teacher_indice = make.get_index(hope, schedule)
        if high3:
            teacher_free_list = make.get_schedule_free_list_for_high3(schedule[teacher_indice][1])
        else:
            teacher_free_list = make.get_schedule_free_list(schedule[teacher_indice][1])

        rndm = random.random()
        k = int((rndm * 100000) % len(student_free_list))
        (i, j) = student_free_list[k]

        if high3:
            b1 = make.rand_move(i, j, 0, teacher_indice, evacuation, schedule, students, teachers)
            b2 = make.rand_move(i, j, 1, teacher_indice, evacuation, schedule, students, teachers)

            if b1 & b2:
                make.place(evacuation, schedule, students, teachers)

        else:
            if teachers[teacher_indice][1][i][j] != "lock":
                h = 0
                if schedule[teacher_indice][1][i][j][0] != ["free", "free", "free"]:
                    h = 1

                b1 = make.rand_move(i, j, h, teacher_indice, lessons, schedule, students, teachers)
                if b1:
                    make.place(evacuation, schedule, students, teachers)
                    



""" 
for te_num in range(1, 10):
    flag = True
    while flag:
        flag = False
        for lesson in lessons:
            if len(lesson[4]) == te_num:
                if lesson[3] > 0:
                    make.place(lesson, schedule, students, teachers, attends)
                    flag = True """

print(schedule)