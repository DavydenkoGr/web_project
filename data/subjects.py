import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


association_table2 = sqlalchemy.Table(
    'class_to_subject',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('school_class', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('school_classes.id')),
    sqlalchemy.Column('subject', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('subjects.id'))
)


class Subject(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'subjects'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    teachers = orm.relation("Teacher", back_populates='subject')
    marks = orm.relation("Marks", back_populates='subject')
