from make import not_lock_and_free
import openpyxl as px

def set_students(wb, students):

    ws_student = wb["生徒スケジュール"]

    row = 4

    for student in students:

        i = 0

        for day in student[1]:

            j = 0

            for frame in day:

                if frame != "free" and frame != "lock":
                    ws_student.cell(row = row, column = 6 + j + (7 * i)).value = frame

                j += 1            
            #end for
            i += 1
        #end for
    #end for

    wb.save




def set_schedule(wb, schedule):

    ws_schedule = wb["教室時間割"]

    row = 4

    for teacher in schedule:

        i = 0

        for day in teacher[1]:

            j = 0

            for frames in day:

                [[grade1, name1, subject1], [grade2, name2, subject2]] = frames
                cell = ws_schedule.cell(row= row + (120*i), column= 4 + (3*j))

                if not_lock_and_free(grade1):
                    cell.value = grade1                
                if not_lock_and_free(name1):
                    cell.offset(0,1).value = name1
                if not_lock_and_free(subject1):
                    cell.offset(0,2).value = subject1

                if not_lock_and_free(grade2):
                    cell.offset(1,0).value = grade2                
                if not_lock_and_free(name2):
                    cell.offset(1,1).value = name2
                if not_lock_and_free(subject2):
                    cell.offset(1,2).value = subject2

                j += 1

            #end for
            i += 1
        #end for
        row += 2
    #end for

    wb.save