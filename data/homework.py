import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Homework(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'homeworks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.id"))
    class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("school_classes.id"))
    task = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date_info = sqlalchemy.Column(sqlalchemy.String, nullable=True)


    subject = orm.relation("Subject")
    school_class = orm.relation("SchoolClass")