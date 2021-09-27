import random
import copy
import teacher as te

#index number取得
def get_index(name, lists):
    indice = -1
    for list in lists:
        if name == list[0]:
            indice = lists.index(list)
            break
    return indice

#i日目j番目のコマがstudentから見て空いているか確認
def student_judge(i, j, indice, students):
    if students[indice][1][i][j] == "free":
        return True
    elif students[indice][1][i][j] == "lock":
        return False
    else:
        return False

#freeのコマをタプル(i,j)のリストにして返す
def get_student_free_list(days):
    free_list = []
    for i in range(0, len(days)):
        for j in range(0, 7):
            if days[i][j] == "free":
                free_list.append((i, j))
    return free_list

#同上（schedule版）
#ほぼ同じなので気が向いたらabstractionする…かも
def get_schedule_free_list(days):
    free_list = []
    for i in range(0, len(days)):
        for j in range(0, 7):
            if days[i][j][0] == ["free", "free", "free"] or days[i][j][1] == ["free", "free", "free"]:
                free_list.append((i, j))
    return free_list

#高3用に上のと使い分け
def get_schedule_free_list_for_high3(days):
    free_list = []
    for i in range(0, len(days)):
        for j in range(0, 7):
            if days[i][j] == [["free", "free", "free"], ["free", "free", "free"]]:
                free_list.append((i, j))
    return free_list

#i日目j番目のコマを出勤状態に（attendは変更しない）
def teacher_attend(i, j, indice, teachers):
    if teachers[indice][1][i][j] == "free":
        teachers[indice][1][i][j] = "attend"
    elif teachers[indice][1][i][j] == "lock":
        raise ValueError("locked cell! In schedule, this cell is supposed to free")

#名前と科目からlessons内を検索してインデックス番号を返す
def search_lesson(name, subject, lessons):
    for lesson in lessons:
        if lesson[1] == name & lesson[2] == subject:
            indice = lessons.index(lesson)
            return indice



#lessonを1コマ登録
def place(lesson, schedule, students, teachers):
    #lesson = [学年, 生徒名, 科目名, コマ数, [希望講師1, 希望講師2, ...]]

    #生徒のインデックス取得
    student_indice = get_index(lesson[1], students)

    #生徒の空きコマ取得
    student_free_list = get_student_free_list(students[student_indice][1])

    if lesson[3] <= 0:
        raise Exception("throw failed")

    flag = True

    #希望講師を前から見ていく
    hope = lesson[4]
    for teacher in hope:
        
        """ #講師に空きがあるか確認、ついでにインデックス取得(要最適化)
        teacher_indice = 0
        for attend in attends:
            if attend[0] == teacher:
                teacher_indice = attends.index(attend)
                break 
        #空きがなければcontinue
        if attends[teacher_indice][1] <= 0:
            continue """

        #講師のインデックス取得
        teacher_indice = get_index(teacher, schedule)

        #講師の空きコマを取得
        teacher_free_list = get_schedule_free_list(schedule[teacher_indice][1])

        #講師と生徒の空きコマの積集合（授業入れられるとこ）
        intersection = list(set(student_free_list) & set(teacher_free_list))

        #被っている空きコマがなければcontinue
        intersec_num = len(intersection)
        if intersec_num == 0:
            continue

        #intersectionのうちランダムな要素を取得
        rndm = random.random()
        k = int((rndm * 1000000) % intersec_num)
        (i, j) = intersection[k]

        #上のコマから優先で登録
        #i日目のj番目の上のコマが空
        if schedule[teacher_indice][1][i][j][0] == ["free", "free", "free"]:
            #登録し諸々のデータを書き換え
            schedule[teacher_indice][1][i][j][0][0] = lesson[0]
            schedule[teacher_indice][1][i][j][0][1] = lesson[1]
            schedule[teacher_indice][1][i][j][0][2] = lesson[2]
            teacher_attend(i, j, teacher_indice, teachers)
            students[student_indice][1][i][j] = lesson[2]
            lesson[3] -= 1
            flag = False
            return (i, j, teacher_indice)

        #i日目のj番目の下のコマが空
        elif schedule[teacher_indice][1][i][j][1] == ["free", "free", "free"]:
            #登録し諸々のデータを書き換え
            schedule[teacher_indice][1][i][j][0][0] = lesson[0]
            schedule[teacher_indice][1][i][j][0][1] = lesson[1]
            schedule[teacher_indice][1][i][j][0][2] = lesson[2]
            teacher_attend(i, j, teacher_indice, teachers)
            students[student_indice][1][i][j] = lesson[2]
            lesson[3] -= 1
            flag = False
            return (i, j, teacher_indice)


    return (-1, -1, -1)    

#    raise Exception("register failed! teachers are not found. " + lesson[1] + " " + lesson[2])


def move(cur_i, cur_j, cur_h, cur_t_i, nex_i, nex_j, nex_h, nex_t_i, student_indice, schedule, students, teachers):
    #lesson = [grade, name, subject]
    lesson = copy.copy(schedule[cur_t_i][1][cur_i][cur_j][cur_h])

    #現在のデータを削除
    schedule[cur_t_i][1][cur_i][cur_j][cur_h] = ["free", "free", "free"]
    if cur_h == 0:
        teachers[cur_t_i][1][cur_i][cur_j] = "free"
    students[student_indice][1][cur_i][cur_j] = None

    #データを移す
    schedule[nex_t_i][1][nex_i][nex_j][nex_h] = lesson
    if nex_h == 0:
        teachers[nex_t_i][1][nex_i][nex_j] = "attend"
    students[student_indice][1][cur_i][cur_j] = lesson[1]



def move_for_high3(cur_i, cur_j, cur_t_i, nex_i, nex_j, nex_t_i, student_indice, schedule, students, teachers):
    lesson = copy.copy(schedule[cur_t_i][1][cur_i][cur_j][0])

    #現在のデータを削除
    schedule[cur_t_i][1][cur_i][cur_j] = [["free", "free", "free"], ["free", "free", "free"]]
    teachers[cur_t_i][1][cur_i][cur_j] = "free"
    students[student_indice][1][cur_i][cur_j] = None

    #データを移す
    schedule[nex_t_i][1][nex_i][nex_j] = [lesson, ["lock", "lock", "lock"]]
    teachers[nex_t_i][1][nex_i][nex_j] = "attend"
    students[student_indice][1][cur_i][cur_j] = lesson[1]




def rand_move(cur_i, cur_j, cur_h, cur_t_i, lessons, schedule, students, teachers):
    #lesson = [学年, 生徒名, 科目名, コマ数, [希望講師1, 希望講師2, ...]]

    name = schedule[cur_t_i][1][cur_i][cur_j][cur_h][1]
    subject = schedule[cur_t_i][1][cur_i][cur_j][cur_h][2]

    high3 = False
    if schedule[cur_t_i][1][cur_i][cur_j][cur_h][0] == "高3":
        high3 = True

    moved = False

    #生徒のインデックス取得
    student_indice = get_index(name, students)

    #生徒の空きコマ取得
    student_free_list = get_student_free_list(students[student_indice][1])

    lesson = search_lesson(name, subject, lessons)
    hope = lesson[4]
    for teacher in hope:

        #講師のインデックス取得
        teacher_indice = get_index(teacher, schedule)
        
        #講師の空きコマ取得
        if high3:
            teacher_free_list = get_schedule_free_list_for_high3(schedule[teacher_indice][1])
        else:
            teacher_free_list = get_schedule_free_list(schedule[teacher_indice][1])

        #講師と生徒の空きコマの積集合（授業入れられるとこ）
        intersection = list(set(student_free_list) & set(teacher_free_list))

        #被っている空きコマがなければcontinue
        intersec_num = len(intersection)
        if intersec_num == 0:
            continue

        #intersectionのうちランダムな要素を取得
        rndm = random.random()
        k = int((rndm * 1000000) % intersec_num)
        (i, j) = intersection[k]

        #上下どちらのセルに入れるか
        height = 1
        if schedule[teacher_indice][1][i][j][0] == ["free", "free", "free"]:
            height = 0

        #move
        if high3:
            move_for_high3(cur_i, cur_j, cur_t_i, i, j, teacher_indice, student_indice, schedule, students, teachers)
        else:
            move(cur_i, cur_j, cur_h, cur_t_i, i, j, height, teacher_indice, student_indice, schedule, students, teachers)
        moved = True
        break

    return moved