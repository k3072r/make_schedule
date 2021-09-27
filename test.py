import openpyxl as px
import lesson as le     #希望講師
import student as st    #生徒スケジュール
import teacher as te    #教室時間割
import schedule as sc   #教室時間割

def remake(lessons):
    lessons[0][3] -= 5

filepath = "test.xlsm"
wb = px.load_workbook(filename=filepath, keep_vba=True)

#schedule = sc.get_schedule(wb)
#lessons = le.get_lessons(wb)
students = st.get_students(wb)
#teachers = te.get_teachers(wb)
#attends = te.teachers_attend_count(schedule)

free_counts = st.student_free_count(students)

print(free_counts)

sorted_free_counts = st.free_count_bubble_sort(free_counts)

print(sorted_free_counts)