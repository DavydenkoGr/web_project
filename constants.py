CLASSES = ['А', 'Б', 'В', 'Г']
# Additional constant, which may help to create base schedule
SUBJECT_DICT = {
    1: [
        ['Окружающий мир', 'Литература', 'Русский язык', 'Технология'],
        ['Литература', 'Русский язык', 'Математика', 'Окружающий мир'],
        ['Литература', 'Математика', 'Русский язык', 'ИЗО'],
        ['Математика', 'Литература', 'Физкультура', 'Русский язык'],
        ['Русский язык', 'Физкультура', 'Математика', 'Музыка']
    ],
    2: [
        ['Русский язык', 'Математика', 'Литература', 'Физкультура'],
        ['Математика', 'Музыка', 'Русский язык', 'Английский язык', 'Окружающий мир'],
        ['Английский язык', 'Окружающий мир', 'Русский язык', 'Литература', 'ИЗО'],
        ['Русский язык', 'Математика', 'Литература', 'Технология'],
        ['Русский язык', 'Математика', 'Литература', 'Физкультура']
    ],
    3: [
        ['Русский язык', 'Литература', 'Математика', 'ИЗО', 'Физкультура'],
        ['Английский язык', 'Математика', 'Русский язык', 'Окружающий мир', 'Информатика'],
        ['Русский язык', 'Музыка', 'Математика', 'Литература', 'Физкультура'],
        ['Литература', 'Русский язык', 'Математика', 'Физкультура', 'Технология'],
        ['Русский язык', 'Литература', 'Окружающий мир', 'Английский язык']
    ],
    4: [
        ['Русский язык', 'Математика', 'Физкультура', 'Информатика'],
        ['Окружающий мир', 'Русский язык', 'Математика', 'ИЗО', 'Английский язык'],
        ['Литература', 'Русский язык', 'Математика', 'Физкультура', 'Английский язык'],
        ['Литература', 'Русский язык', 'Математика', 'Технология', 'Информатика'],
        ['Окружающий мир', 'Литература', 'Русский язык', 'Музыка', 'Физкультура']
    ],
    5: [
        ['Биология', 'Математика', 'Русский язык', 'Литература', 'Музыка'],
        ['Английский язык', 'Русский язык', 'Математика', 'Физкультура', 'История'],
        ['Обществознание', 'Русский язык', 'Математика', 'Физкультура', 'Литература', 'ИЗО'],
        ['ОБЖ', 'Русский язык', 'Математика', 'Английский язык', 'История', 'Информатика'],
        ['Английский язык', 'Русский язык', 'Математика', 'Литература', 'Физкультура'],
        ['Информатика', 'Русский язык', 'География', 'Технология']
    ],
    6: [
        ['Русский язык', 'Биология', 'Математика', 'Физкультура', 'Литература'],
        ['Информатика', 'Математика', 'Русский язык', 'История', 'Физкультура', 'Музыка'],
        ['Русский язык', 'Математика', 'Литература', 'География', 'Обществознание', 'Технология'],
        ['Английский язык', 'География', 'Русский язык', 'Русский язык', 'Физкультура', 'ИЗО',],
        ['Русский язык', 'Математика', 'Литература', 'Английский язык', 'ОБЖ'],
        ['Биология', 'Английский язык', 'Математика', 'История']
    ],
    7: [
        ['Математика', 'Русский язык', 'Физика', 'География', 'Технология'],
        ['Математика', 'Русский язык', 'Биология', 'Литература', 'Музыка', 'История'],
        ['Математика', 'Русский язык', 'Обществознание', 'Черчение', 'География', 'История'],
        ['Математика', 'Русский язык', 'Английский язык', 'Физика', 'ОБЖ', 'Физкультура'],
        ['Математика', 'Биология', 'Английский язык', 'Литература', 'Информатика', 'Физкультура'],
        ['Русский язык', 'География', 'Английский язык', 'Математика']
    ],
    8: [
        ['Английский язык', 'Русский язык', 'ОБЖ', 'Математика', 'География', 'Биология'],
        ['Химия', 'Информатика', 'История', 'Математика', 'Литература', 'Физкультура'],
        ['Биология', 'Физика', 'Русский язык', 'История', 'Математика', 'Физкультура'],
        ['Обществознание', 'Химия', 'Русский язык', 'Математика', 'Физика', 'Музыка'],
        ['Русский язык', 'Английский язык', 'Литература', 'Математика', 'Математика', 'География'],
        ['Английский язык', 'Информатика', 'География', 'Физкультура']
    ],
    9: [
        ['Математика', 'Обществознание', 'ОБЖ', 'Английский язык', 'Физкультура', 'Физика'],
        ['Математика', 'История', 'Информатика', 'География', 'Химия', 'Английский язык'],
        ['Математика', 'Русский язык', 'Физика', 'Биология', 'Информатика', 'Литература'],
        ['Химия', 'Математика', 'История', 'География', 'Физкультура', 'Биология'],
        ['Математика', 'Математика', 'Русский язык', 'Литература', 'Литература', 'Английский язык'],
        ['Математика', 'История',  'Русский язык', 'Физкультура', 'География']
    ],
    10: [
        ['Математика', 'Математика', 'Информатика', 'Информатика', 'Русский язык', 'Литература'],
        ['Физика', 'Физика', 'Английский язык', 'Биология', 'История', 'История'],
        ['ОБЖ', 'Физика', 'Химия', 'Английский язык', 'Математика', 'Математика'],
        ['Математика', 'Математика', 'Литература', 'Литература', 'Физика', 'Физика'],
        ['Физкультура', 'Физика', 'Информатика', 'Информатика', 'Математика', 'Математика'],
        ['Обществознание', 'Обществознание',  'Физкультура', 'Математика', 'Английский язык', 'Русский язык']
    ],
    11: [
        ['Обществознание', 'Английский язык', 'Биология', 'Математика', 'Математика', 'Литература'],
        ['Физика', 'Математика', 'Английский язык', 'Биология', 'Русский язык', 'ОБЖ'],
        ['Математика', 'Химия', 'Английский язык', 'Математика', 'Литература', 'Физика'],
        ['Математика', 'История', 'Химия', 'Физкультура', 'Русский язык', 'Литература'],
        ['Астрономия', 'Физика', 'История', 'Физкультура', 'Русский язык', 'Обществознание'],
        ['Математика', 'Биология',  'Информатика', 'Русский язык', 'Литература', 'Математика']
    ]
}
