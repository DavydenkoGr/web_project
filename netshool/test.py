@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    form = RegisterTeacherForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first() or \
                db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   message="Данная почта уже зарегистрирована в системе")
        subject = db_sess.query(Subject).filter(Subject.name == form.subject.data
                                                ).first()
        # В зависимости от цифры у некоторых классов присутсвуют одни уроки и отсутствуют другие.
        # Проверяем есть ли у данноко класса данный урок.
        # Заодно проверяем, нет ли уже у какого-то из выбранных классов учителя по заданному предмету.
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            if subject not in school_class.subjects:
                return render_template('register_teacher.html', title='Регистрация учителя',
                                       form=form,
                                       message=f'У {number} класса отсутствует предмет'
                                               f' {form.subject.data}')
            for teacher in db_sess.query(Teacher).all():
                if school_class in teacher.school_classes and teacher.subject_id == subject.id:
                    return render_template('register_teacher.html', title='Регистрация учителя',
                                           form=form,
                                           message=f'У {number}{letter} класса уже есть учитель'
                                                   f' по предмету {subject.name}')
        teacher = Teacher(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            subject_id=subject.id
        )
        teacher.set_password(form.password.data)
        # Очень страшная проверка пересечения уроков в расписании
        # Делим выбранные классы на 2 смены и попарно сравниваем каждый урок каждого дня,
        # чтоб не получилось ситуаций, в которых учитель ведет уроки у 2 классов одновременно
        list_of_tables1 = list()
        names1 = list()
        list_of_tables2 = list()
        names2 = list()
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            if number % 2 == 1:
                list_of_tables1.append(get_class_schedule(number, letter))
                names1.append(f"{number}{letter}")
            else:
                list_of_tables2.append(get_class_schedule(number, letter))
                names2.append(f"{number}{letter}")
        for i, first_table in enumerate(list_of_tables1):
            for j, second_table in enumerate(list_of_tables1):
                if i == j:
                    continue
                for day in range(min(len(first_table), len(second_table))):
                    for lesson in range(min(len(first_table[day]), len(second_table[day]))):
                        if first_table[day][lesson] == second_table[day][lesson] and\
                                first_table[day][lesson] == subject.name:
                            return render_template('register_teacher.html',
                                                   title='Регистрация учителя',
                                                   form=form,
                                                   message=f'У классов {names1[i]} и {names1[j]}'
                                                           f' совпадают расписания,'
                                                           f' уберите один из классов или'
                                                           f' измените расписание.')
        for i, first_table in enumerate(list_of_tables2):
            for j, second_table in enumerate(list_of_tables2):
                if i == j:
                    continue
                for day in range(min(len(first_table), len(second_table))):
                    for lesson in range(min(len(first_table[day]), len(second_table[day]))):
                        if first_table[day][lesson] == second_table[day][lesson] and\
                                first_table[day][lesson] == subject.name:
                            return render_template('register_teacher.html',
                                                   title='Регистрация учителя',
                                                   form=form,
                                                   message=f'У классов {names2[i]} и {names2[j]}'
                                                           f' совпадают расписания,'
                                                           f' уберите один из классов или'
                                                           f' измените расписание.')
        # Если все проверки пройдены, добавляем учителю каждый выбранный класс
        db_sess.add(teacher)
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            teacher.school_classes.append(school_class)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_teacher.html', title='Регистрация учителя', form=form)