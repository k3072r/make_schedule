from getxl import student_free_count
import random
import copy

#index number取得
def get_index(name, lists):
    indice = -1
    for list in lists:
        if name == list[0]:
            indice = lists.index(list)
            break
    return indice

#i日目j番目のコマがstudentから見て空いているか確認
def student_judge_free(i, j, indice, students):
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
            if days[i][j][0] == ["free", "free", "free"] or days[i][j][1] == ["free", "free", "free"]: #1だけで良いと思う
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
        if lesson[1] == name and lesson[2] == subject:
            indice = lessons.index(lesson)
            return indice

#コマに授業が入っていればTrue
def exist_lesson(frame):
    return not (frame == ["free", "free", "free"] or frame == ["lock", "lock", "lock"])


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
        k = int((rndm * 1000000000) % intersec_num)
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
            schedule[teacher_indice][1][i][j][1][0] = lesson[0]
            schedule[teacher_indice][1][i][j][1][1] = lesson[1]
            schedule[teacher_indice][1][i][j][1][2] = lesson[2]
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




def random_move(cur_i, cur_j, cur_h, cur_t_i, student_indice, lessons, schedule, students, teachers):
    #lesson = [学年, 生徒名, 科目名, コマ数, [希望講師1, 希望講師2, ...]]

    name = schedule[cur_t_i][1][cur_i][cur_j][cur_h][1]
    subject = schedule[cur_t_i][1][cur_i][cur_j][cur_h][2]

    high3 = False
    if schedule[cur_t_i][1][cur_i][cur_j][cur_h][0] == "高3" or schedule[cur_t_i][1][cur_i][cur_j][cur_h][0] == "新高3":
        high3 = True

    moved = False

    #生徒の空きコマ取得
    student_free_list = get_student_free_list(students[student_indice][1])

    lesson_indice = search_lesson(name, subject, lessons)
    hopes = lessons[lesson_indice][4]
    for teacher in hopes:

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
        k = int((rndm * 1000000000) % intersec_num)
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




def exchange(i1, j1, h1, t_indice1, s_indice1, i2, j2, h2, t_indice2, s_indice2, schedule, students):
    students[s_indice1][1][i1][j1], students[s_indice1][1][i2][j2] = students[s_indice1][1][i2][j2], students[s_indice1][1][i1][j1]
    students[s_indice2][1][i1][j1], students[s_indice2][1][i2][j2] = students[s_indice2][1][i2][j2], students[s_indice2][1][i1][j1]

    schedule[t_indice1][1][i1][j1][h1], schedule[t_indice2][1][i2][j2][h2] = schedule[t_indice2][1][i2][j2][h2], schedule[t_indice1][1][i1][j1][h1]



#片方のみ高3（両方高3ならexchangeを使えばいいので）（1が高3）
def exchange_for_high3(i1, j1, t_indice1, s_indice1, i2, j2, t_indice2, s_indice2, schedule, students):
    students[s_indice1][1][i1][j1], students[s_indice1][1][i2][j2] = students[s_indice1][1][i2][j2], students[s_indice1][1][i1][j1]
    students[s_indice2][1][i1][j1], students[s_indice2][1][i2][j2] = students[s_indice2][1][i2][j2], students[s_indice2][1][i1][j1]



def get_not_locked_frames(schedule):

    teacher_num = len(schedule)
    day_num = len(schedule[0][1])
    not_locked_frames = []

    for t_indice in range(teacher_num):
        for i in range(day_num):
            for j in range(7):
                if schedule[t_indice][1][i][j][0] != ["lock", "lock", "lock"]:
                    not_locked_frames.append((t_indice, i, j))

    return not_locked_frames


def not_lock_and_free(string):

    if string != "free" and string != "lock":
        return True
    else:
        return False