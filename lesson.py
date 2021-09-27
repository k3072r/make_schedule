import openpyxl as px
from openpyxl import cell
from openpyxl.xml.constants import MIN_ROW

def get_lessons(wb):

    ws_teacher = wb["希望講師"]

    # max_row don't work correctly.
    # I suppose that formats made by VBA (by someone other than me) do bad.
    lastrow = ws_teacher.max_row

    lessons = []

    for row in ws_teacher.iter_rows(min_row=4, min_col=2):

        grade = row[0].value
        name = row[2].value
        #flag = 0

        if name is None:
            break

        #既に該当生徒の授業が登録されている
        """ for lesson in lessons:
            if name == lesson[0]:

                alesson = []
                for cell in row[1:2]:
                    alesson.append(cell.value)

                teachers = []
                for cell in row[3:]:
                    if cell.value is None:
                        break
                    teachers.append(cell.value)

                alesson.append(teachers)
                lesson.append(alesson)

                flag = 1
                break """

        #その生徒の授業の追加が初
        """ if flag == 1 :
            continue """

        lesson = [grade, name]
        for cell in row[3:5]:
            lesson.append(cell.value)

        teachers = []
        for cell in row[5:]:
            if cell.value is None:
                break
            teachers.append(cell.value)

        lesson.append(teachers)
        lessons.append(lesson)

    return lessons




#"希望講師"ワークシートの情報を以下のような形式で保存する
# lessons = [
#               [学年, 生徒名, 科目名, コマ数, [希望講師1, 希望講師2, ...]], 
#               [学年, 生徒名, ...],
#               ... ,
#           ]
#
#
#
# BNF風に書くとこう
# lessons = [
#               [grade, name1, subject, num, teachers],
#               [grade, name2, subject, num, teachers],
#               ... ,
#           ]
# teachers = [teacher1, teacher2, ...]