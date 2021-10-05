from random import random
import make

def loss_hoperank(t_name, s_name, subject, lessons):
    lesson_indice = make.search_lesson(s_name, subject, lessons)
    losses = 0
    loss = 1
    for hope in lessons[lesson_indice][4]:
        if t_name == hope:
            return losses
        else:
            losses += loss
            loss += 1



def all_loss_hoperank(schedule, lessons):

    losses = 0

    for teacher in schedule:
        t_name = teacher[0]

        for day in teacher[1]:
            for frames in day:
                #上と下
                for frame in frames:
                    #授業が入っていれば希望講師順位による損失を計算
                    if not (frame[1] == "free" or frame[1] == "lock"):
                        s_name = frame[1]
                        subject = frame[2]
                        losses += loss_hoperank(t_name, s_name, subject, lessons)
                    #end if
                #end for
            #end for
        #end for
    #end for

    return losses




def loss_student_sparse(day):
    
    a = -1
    b = -1
    flag = False #その日最初の授業をaに入れたか否か（aがNoneか否か）
    loss = 1
    losses = 0

    for i in range(7):
        if not (day[i] == "free" or day[i] == "lock"):
            if flag:
                b = i
                if b - a == 1:
                    a = b
                else:
                    losses += loss
                    break
            else:
                a = i
                flag = True
            # end if
        # end if
    #end for
    return losses

def all_loss_student_sparse(students):

    losses = 0

    for student in students:
        for day in student[1]:
            losses += loss_student_sparse(day)

    return losses





def loss_free_teacher_exist(i, j, teachers):

    loss = 1

    teacher_num = len(teachers)

    flag_all_lock = True

    for indice in range(0, teacher_num):
        if teachers[indice][1][i][j] == "free":
            return 0
        if teachers[indice][1][i][j] != "lock":
            flag_all_lock = False

    #end for

    if flag_all_lock:
        return 0
    else:
        return loss


def all_loss_free_teacher_exist(teachers):

    losses = 0

    day_num = len(teachers[0][1])

    for i in range(0, day_num):
        for j in range(0, 7):

            losses += loss_free_teacher_exist(i, j, teachers)

    return losses