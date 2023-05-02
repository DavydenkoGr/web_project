import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Marks(SqlAlchemyBase, SerializerMixin):
    """mark list model"""
    __tablename__ = 'marks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"))
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.id"))
    marks = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    student = orm.relation('Student')
    subject = orm.relation('Subject')
