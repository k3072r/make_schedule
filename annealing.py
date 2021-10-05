from make import *
from calc_loss import *
import random
from copy import deepcopy
from math import exp


#交換可能かの確認
#check_move2回でも代用可能
def check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule):

    #一つ目のコマの情報を取得
    t_name1 = schedule[t_indice1][0]
    s_name1 = frame1[1]
    subject1 = frame1[2]
    s_indice1 = get_index(s_name1, students)
    lesson_indice1 = search_lesson(s_name1, subject1, lessons)
    hopes1 = lessons[lesson_indice1][4]

    #二つ目のコマの情報を取得
    t_name2 = schedule[t_indice2][0]
    s_name2 = frame2[1]
    subject2 = frame2[2]
    s_indice2 = get_index(s_name2, students)
    lesson_indice2 = search_lesson(s_name2, subject2, lessons)
    hopes2 = lessons[lesson_indice2][4]

    #授業を交換可能か確認
    check1 = student_judge_free(i2, j2, s_indice1, students) and student_judge_free(i1, j1, s_indice2, students)
    check2 = (t_name1 in hopes2) and (t_name2 in hopes1)

    if check1 and check2:
        return (s_indice1, s_indice2)
    else:
        return (-1, -1)
    



#移動可能かの確認
def check_move(i2, j2, frame1, t_indice2, students, lessons, schedule):

    #一つ目のコマの情報を取得
    s_name1 = frame1[1]
    subject1 = frame1[2]
    s_indice1 = get_index(s_name1, students)
    lesson_indice1 = search_lesson(s_name1, subject1, lessons)
    hopes1 = lessons[lesson_indice1][4]

    #二つ目のコマの情報を取得
    t_name2 = schedule[t_indice2][0]
    
    #授業を移動可能か確認
    check1 = student_judge_free(i2, j2, s_indice1, students)
    check2 = t_name2 in hopes1
    #check3 = frame2 == ["free", "free", "free"] #ifのguardに移動

    if check1 and check2:
        return s_indice1
    else:
        return -1


#状態を変更する2コマをランダムに選択
@profile
def state_to_change(schedule, students, lessons):
    #要素数
    teacher_num = len(schedule)
    day_num = len(schedule[0][1])

    #returnする組が見つかるまでループ
    while True:

        #一つ目のコマをランダムに選択
        rndm = random.random()
        t_indice1 = int((rndm * 1000000000) % teacher_num)
        i1 = int((rndm * 1000000000) % day_num)
        j1 = int((rndm * 1000000000) % 7)
        h1 = int((rndm * 1000000000) % 2)

        #二つ目のコマをランダムに選択
        rndm = random.random()
        t_indice2 = int((rndm * 1000000000) % teacher_num)
        i2 = int((rndm * 1000000000) % day_num)
        j2 = int((rndm * 1000000000) % 7)
        h2 = int((rndm * 1000000000) % 2)

        

        #高3を含むか否かで場合分け
        #両方高3の場合
        if schedule[t_indice1][1][i1][j1][0][0] == "新高３" and schedule[t_indice2][1][i2][j2][0][0] == "新高３":

            frame1 = schedule[t_indice1][1][i1][j1][0]
            frame2 = schedule[t_indice2][1][i2][j2][0]

            s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)

            #交換可能ならそのコマを返す（タプルの最後の要素で1要素の交換であることを指定）
            if s_indice1 != -1:
                return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, s_indice2, 0)


        #片方が高3の場合1
        elif schedule[t_indice1][1][i1][j1][0][0] == "新高３":

            frame1 = schedule[t_indice1][1][i1][j1][0]
            frame2 = schedule[t_indice2][1][i2][j2][0]

            #高3でないコマも授業が入っている場合
            if exist_lesson(frame2):

                #frame2の下の授業
                frame3 = schedule[t_indice2][1][i2][j2][1]

                #授業がフルで入っている場合
                if exist_lesson(frame3):
                    s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)
                    s_indice3 = check_move(i1, j1, frame3, t_indice1, students, lessons, schedule)

                    #交換可能ならそのコマを返す（タプルの最後の要素で2要素の交換であることを指定）
                    if s_indice1 != -1 and s_indice3 != -1:
                        return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, s_indice2, 2)

                #上しか授業がない場合
                else:
                    s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)

                    #交換可能ならそのコマを返す（タプルの最後の要素で高3を含む1要素の交換であることを指定）
                    if s_indice1 != -1:
                        return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, s_indice2, 1)

            #高3側しか授業がない場合
            elif frame2 == ["free", "free", "free"]:
                s_indice1 = check_move(i2, j2, frame1, t_indice2, students, lessons, schedule)

                #交換可能ならそのコマを返す（タプルの最後の要素で高3の移動であることを指定）
                if s_indice1 != -1:
                    return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, -1, 4)
                

        #片方が高3の場合2
        elif schedule[t_indice2][1][i2][j2][0][0] == "新高３":

            frame1 = schedule[t_indice1][1][i1][j1][0]
            frame2 = schedule[t_indice2][1][i2][j2][0]

            #高3でないコマも授業が入っている場合
            if exist_lesson(frame1):

                #frame1の下の授業
                frame3 = schedule[t_indice1][1][i1][j1][1]

                #授業がフルで入っている場合
                if exist_lesson(frame3):
                    s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)
                    s_indice3 = check_move(i2, j2, frame3, t_indice2, students, lessons, schedule)

                    #交換可能ならそのコマを返す（タプルの最後の要素で2要素の交換であることを指定）
                    if s_indice1 != -1 and s_indice3 != -1:
                        return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, s_indice2, 2)

                #上しか授業がない場合
                else:
                    s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)

                    #交換可能ならそのコマを返す（タプルの最後の要素で高3を含む1要素の交換であることを指定）
                    if s_indice1 != -1:
                        return (i1, j1, 0, t_indice1, s_indice1, i2, j2, 0, t_indice2, s_indice2, 1)

            #高3側しか授業がない場合
            elif frame1 == ["free", "free", "free"]:
                s_indice2 = check_move(i1, j1, frame2, t_indice1, students, lessons, schedule)

                #交換可能ならそのコマを返す（タプルの最後の要素で高3の移動であることを指定）
                if s_indice2 != -1:
                    return (i2, j2, 0, t_indice2, s_indice2, i1, j1, 0, t_indice1, -1, 4)


        #どちらも高3でない場合
        else:

            #選択したコマ
            frame1 = schedule[t_indice1][1][i1][j1][h1]
            frame2 = schedule[t_indice2][1][i2][j2][h2]

            #どちらも授業が入っている場合
            if exist_lesson(frame1) and exist_lesson(frame2):
                
                s_indice1, s_indice2 = check_exchange(i1, j1, i2, j2, frame1, frame2, t_indice1, t_indice2, students, lessons, schedule)

                #交換可能ならそのコマを返す（タプルの最後の要素で1要素の交換であることを指定）
                if s_indice1 != -1:
                    return (i1, j1, h1, t_indice1, s_indice1, i2, j2, h2, t_indice2, s_indice2, 0)

            #frame1のみ授業が入っている場合
            elif exist_lesson(frame1) and frame2 == ["free", "free", "free"]:

                s_indice1 = check_move(i2, j2, frame1, t_indice2, students, lessons, schedule)

                #移動可能ならそのコマを返す（タプルの最後の要素で非高3の移動であることを指定）
                if s_indice1 != -1:
                    return (i1, j1, h1, t_indice1, s_indice1, i2, j2, h2, t_indice2, -1, 3)

            #frame2のみ授業が入っている場合
            elif frame1 == ["free", "free", "free"] and exist_lesson(frame2):

                s_indice2 = check_move(i1, j1, frame2, t_indice1, students, lessons, schedule)

                #移動可能ならそのコマを返す（タプルの最後の要素で非高3の移動であることを指定）
                if s_indice2 != -1:
                    return (i2, j2, h2, t_indice2, s_indice2, i1, j1, h1, t_indice1, -1, 3)

            #frame1, frame2共に授業でないなら状態遷移しないのでループ




#1, 2の各パラメータは、組み合わせが合っていれば逆でも大丈夫
def part_of_loss_for_exchange(lessons, frame1, t1_name, s1_day1, s1_day2, frame2, t2_name, s2_day1, s2_day2):
    
    s1_name = frame1[1]
    s1_subject = frame1[2]
    s2_name = frame2[1]
    s2_subject = frame2[2]

    loss = 0
    loss += loss_hoperank(t1_name, s1_name, s1_subject, lessons)
    loss += loss_hoperank(t2_name, s2_name, s2_subject, lessons)
    loss += loss_student_sparse(s1_day1)
    loss += loss_student_sparse(s1_day2)
    loss += loss_student_sparse(s2_day1)
    loss += loss_student_sparse(s2_day2)

    return loss


#こちらは、移動前なら前の、移動後なら後の、パラメータを正しく引数に取るよう注意
def part_of_loss_for_move(lessons, frame1, t1_name, s1_day1, s1_day2):

    s1_name = frame1[1]
    s1_subject = frame1[2]

    loss = 0
    loss += loss_hoperank(t1_name, s1_name, s1_subject, lessons)
    loss += loss_student_sparse(s1_day1)
    loss += loss_student_sparse(s1_day2)

    return loss



def part_of_loss_free_teacher(i1, j1, i2, j2, teachers):

    loss = 0
    loss += loss_free_teacher_exist(i1, j1, teachers)
    loss += loss_free_teacher_exist(i2, j2, teachers)

    return loss







def simulated_annealing(schedule, students, teachers, lessons):

    temp_max = 100
    temp_min = 10
    interation = 50
    temp_diff = 0.95
    temp = temp_max

    while temp >= temp_min:

        print(temp)

        for count in range(interation):

            #交換（移動）候補の取得
            (i1, j1, h1, t_indice1, s_indice1, i2, j2, h2, t_indice2, s_indice2, flag) = state_to_change(schedule, students, lessons)

            t_name1 = schedule[t_indice1][0]
            t_name2 = schedule[t_indice2][0]

            #1要素の交換
            if flag == 0:

                #scheduleの一部
                frame1 = schedule[t_indice1][1][i1][j1][h1]
                frame2 = schedule[t_indice2][1][i2][j2][h2]
                
                #遷移後のstudentsの一部
                st1_1 = students[s_indice1][1][i1]
                st1_2 = students[s_indice1][1][i2]
                next_st1_1 = deepcopy(st1_1)
                next_st1_2 = deepcopy(st1_2)
                next_st1_1[j1], next_st1_2[j2] = next_st1_2[j2], next_st1_1[j1]

                st2_1 = students[s_indice2][1][i1]
                st2_2 = students[s_indice2][1][i2]
                next_st2_1 = deepcopy(st2_1)
                next_st2_2 = deepcopy(st2_2)
                next_st2_1[j1], next_st2_2[j2] = next_st2_2[j2], next_st2_1[j1]

                #teachersは遷移後も変化なし

                #損失の差分のみ計算
                loss_cur = part_of_loss_for_exchange(lessons, frame1, t_name1, st1_1, st1_2, frame2, t_name2, st2_1, st2_2)
                loss_nex = part_of_loss_for_exchange(lessons, frame2, t_name1, next_st1_1, next_st1_2, frame1, t_name2, next_st2_1, next_st2_2)
                loss_diff = loss_cur - loss_nex

                #良化する場合は無条件に遷移
                if loss_diff >= 0:
                    frame1, frame2 = frame2, frame1
                    st1_1 = next_st1_1
                    st1_2 = next_st1_2
                    st2_1 = next_st2_1
                    st2_2 = next_st2_2

                #そうでなければ、遷移するか否か、tempに基づき確率的に決定
                else:
                    if exp(loss_diff / temp) > random.random():
                        frame1, frame2 = frame2, frame1
                        st1_1 = next_st1_1
                        st1_2 = next_st1_2
                        st2_1 = next_st2_1
                        st2_2 = next_st2_2

            #高3を含む1要素の交換
            elif flag == 1:

                #schedule
                frame1 = schedule[t_indice1][1][i1][j1][0]
                frame2 = schedule[t_indice2][1][i2][j2][0]
                
                #遷移後のstudentsの一部
                st1_1 = students[s_indice1][1][i1]
                st1_2 = students[s_indice1][1][i2]
                next_st1_1 = deepcopy(st1_1)
                next_st1_2 = deepcopy(st1_2)
                next_st1_1[j1], next_st1_2[j2] = next_st1_2[j2], next_st1_1[j1]

                st2_1 = students[s_indice2][1][i1]
                st2_2 = students[s_indice2][1][i2]
                next_st2_1 = deepcopy(st2_1)
                next_st2_2 = deepcopy(st2_2)
                next_st2_1[j1], next_st2_2[j2] = next_st2_2[j2], next_st2_1[j1]

                #teachersは遷移後も変化なし

                #損失の差分のみ計算
                loss_cur = part_of_loss_for_exchange(lessons, frame1, t_name1, st1_1, st1_2, frame2, t_name2, st2_1, st2_2)
                loss_nex = part_of_loss_for_exchange(lessons, frame2, t_name1, next_st1_1, next_st1_2, frame1, t_name2, next_st2_1, next_st2_2)
                loss_diff = loss_cur - loss_nex

                #良化する場合は無条件に遷移（lockとfreeの入れ替えも行う）
                if loss_diff >= 0:
                    frame1, frame2 = frame2, frame1
                    schedule[t_indice1][1][i1][j1][1], schedule[t_indice2][1][i2][j2][1] = schedule[t_indice2][1][i2][j2][1], schedule[t_indice1][1][i1][j1][1]
                    st1_1 = next_st1_1
                    st1_2 = next_st1_2
                    st2_1 = next_st2_1
                    st2_2 = next_st2_2

                #そうでなければ、遷移するか否か、tempに基づき確率的に決定
                else:
                    if exp(loss_diff / temp) > random.random():
                        frame1, frame2 = frame2, frame1
                        schedule[t_indice1][1][i1][j1][1], schedule[t_indice2][1][i2][j2][1] = schedule[t_indice2][1][i2][j2][1], schedule[t_indice1][1][i1][j1][1]
                        st1_1 = next_st1_1
                        st1_2 = next_st1_2
                        st2_1 = next_st2_1
                        st2_2 = next_st2_2

            #高3を含む2要素の交換
            elif flag == 2:

                #返り値にない、3人目の生徒の情報を取得
                s_name3 = schedule[t_indice2][1][i2][j2][1][1]
                s_indice3 = get_index(s_name3, students)

                #scheduleの一部
                frame1 = schedule[t_indice1][1][i1][j1][0]
                frame2 = schedule[t_indice2][1][i2][j2][0]
                frame3 = schedule[t_indice2][1][i2][j2][1]
                
                #遷移後のstudentsの一部
                st1_1 = students[s_indice1][1][i1]
                st1_2 = students[s_indice1][1][i2]
                next_st1_1 = deepcopy(st1_1)
                next_st1_2 = deepcopy(st1_2)
                next_st1_1[j1], next_st1_2[j2] = next_st1_2[j2], next_st1_1[j1]

                st2_1 = students[s_indice2][1][i1]
                st2_2 = students[s_indice2][1][i2]
                next_st2_1 = deepcopy(st2_1)
                next_st2_2 = deepcopy(st2_2)
                next_st2_1[j1], next_st2_2[j2] = next_st2_2[j2], next_st2_1[j1]

                st3_1 = students[s_indice3][1][i1]
                st3_2 = students[s_indice3][1][i2]
                next_st3_1 = deepcopy(st3_1)
                next_st3_2 = deepcopy(st3_2)
                next_st3_1[j1], next_st3_2[j2] = next_st3_2[j2], next_st3_1[j1]

                #teachersは遷移後も変化なし

                #損失の差分のみ計算
                loss_cur = part_of_loss_for_exchange(lessons, frame1, t_name1, st1_1, st1_2, frame2, t_name2, st2_1, st2_2)
                loss_cur += part_of_loss_for_move(lessons, frame3, t_name1, st3_1, st3_2)
                loss_nex = part_of_loss_for_exchange(lessons, frame2, t_name1, next_st1_1, next_st1_2, frame1, t_name2, next_st2_1, next_st2_2)
                loss_nex += part_of_loss_for_move(lessons, frame3, t_name2, next_st3_1, next_st3_2)
                loss_diff = loss_cur - loss_nex

                #良化する場合は無条件に遷移
                if loss_diff >= 0:
                    frame1, frame2 = frame2, frame1
                    schedule[t_indice1][1][i1][j1][1], frame3 = frame3, schedule[t_indice1][1][i1][j1][1]
                    st1_1 = next_st1_1
                    st1_2 = next_st1_2
                    st2_1 = next_st2_1
                    st2_2 = next_st2_2
                    st3_1 = next_st3_1
                    st3_2 = next_st3_2

                #そうでなければ、遷移するか否か、tempに基づき確率的に決定
                else:
                    if exp(loss_diff / temp) > random.random():
                        frame1, frame2 = frame2, frame1
                        schedule[t_indice1][1][i1][j1][1], frame3 = frame3, schedule[t_indice1][1][i1][j1][1]
                        st1_1 = next_st1_1
                        st1_2 = next_st1_2
                        st2_1 = next_st2_1
                        st2_2 = next_st2_2
                        st3_1 = next_st3_1
                        st3_2 = next_st3_2

            #非高3の移動
            elif flag == 3:

                #scheduleの一部
                frame1 = schedule[t_indice1][1][i1][j1][h1]
                frame2 = schedule[t_indice2][1][i2][j2][h2]
                
                #遷移後のstudentsの一部
                st1_1 = students[s_indice1][1][i1]
                st1_2 = students[s_indice1][1][i2]
                next_st1_1 = deepcopy(st1_1)
                next_st1_2 = deepcopy(st1_2)
                next_st1_1[j1], next_st1_2[j2] = next_st1_2[j2], next_st1_1[j1]

                #遷移後のteachers
                next_teachers = deepcopy(teachers)
                if h1 == 0:
                    next_teachers[t_indice1][1][i1][j1] = "free"
                if h2 == 0:
                    next_teachers[t_indice2][1][i2][j2] = "attend"
                

                #損失の差分のみ計算
                loss_cur = part_of_loss_for_move(lessons, frame1, t_name1, st1_1, st1_2)
                loss_cur += part_of_loss_free_teacher(i1, j1, i2, j2, teachers)
                loss_nex = part_of_loss_for_move(lessons, frame1, t_name2, next_st1_1, next_st1_2)
                loss_nex += part_of_loss_free_teacher(i1, j1, i2, j2, next_teachers)
                loss_diff = loss_cur - loss_nex

                #良化する場合は無条件に遷移
                if loss_diff >= 0:
                    frame1, frame2 = frame2, frame1
                    st1_1 = next_st1_1
                    st1_2 = next_st1_2
                    teachers = next_teachers

                #そうでなければ、遷移するか否か、tempに基づき確率的に決定
                else:
                    if exp(loss_diff / temp) > random.random():
                        frame1, frame2 = frame2, frame1
                        st1_1 = next_st1_1
                        st1_2 = next_st1_2
                        teachers = next_teachers

            #高3の移動
            elif flag == 4:

                #scheduleの一部
                frame1 = schedule[t_indice1][1][i1][j1][0]
                
                #遷移後のstudentsの一部
                st1_1 = students[s_indice1][1][i1]
                st1_2 = students[s_indice1][1][i2]
                next_st1_1 = deepcopy(st1_1)
                next_st1_2 = deepcopy(st1_2)
                next_st1_1[j1], next_st1_2[j2] = next_st1_2[j2], next_st1_1[j1]

                #遷移後のteachers
                next_teachers = deepcopy(teachers)
                next_teachers[t_indice1][1][i1][j1] = "free"
                next_teachers[t_indice2][1][i2][j2] = "attend"
                
                #損失の差分のみ計算
                loss_cur = part_of_loss_for_move(lessons, frame1, t_name1, st1_1, st1_2)
                loss_cur += part_of_loss_free_teacher(i1, j1, i2, j2, teachers)
                loss_nex = part_of_loss_for_move(lessons, frame1, t_name2, next_st1_1, next_st1_2)
                loss_nex += part_of_loss_free_teacher(i1, j1, i2, j2, next_teachers)
                loss_diff = loss_cur - loss_nex

                #良化する場合は無条件に遷移（高3の下のlockも移す）
                if loss_diff >= 0:
                    frame1, schedule[t_indice2][1][i2][j2][0] = schedule[t_indice2][1][i2][j2][0], frame1
                    schedule[t_indice1][1][i1][j1][1], schedule[t_indice2][1][i2][j2][1] = schedule[t_indice2][1][i2][j2][1], schedule[t_indice1][1][i1][j1][1]
                    st1_1 = next_st1_1
                    st1_2 = next_st1_2
                    teachers = next_teachers

                #そうでなければ、遷移するか否か、tempに基づき確率的に決定
                else:
                    if exp(loss_diff / temp) > random.random():
                        frame1, schedule[t_indice2][1][i2][j2][0] = schedule[t_indice2][1][i2][j2][0], frame1
                        schedule[t_indice1][1][i1][j1][1], schedule[t_indice2][1][i2][j2][1] = schedule[t_indice2][1][i2][j2][1], schedule[t_indice1][1][i1][j1][1]
                        st1_1 = next_st1_1
                        st1_2 = next_st1_2
                        teachers = next_teachers
            
            #end if

        #end for

        temp *= temp_diff
    
    #end while

    return (schedule, students)