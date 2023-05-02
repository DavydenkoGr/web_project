import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


association_table1 = sqlalchemy.Table(
    'teacher_to_class',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('teacher', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('teachers.id')),
    sqlalchemy.Column('school_class', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('school_classes.id'))
)


class SchoolClass(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'school_classes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    letter = sqlalchemy.Column(sqlalchemy.CHAR, nullable=False)

    students = orm.relation("Student", back_populates='school_class')
    subjects = orm.relation("Subject",
                            secondary="class_to_subject",
                            backref="school_classes")
