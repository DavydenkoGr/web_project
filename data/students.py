import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    school_class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("school_classes.id"))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    background_color = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    school_class = orm.relation("SchoolClass")
    marks = orm.relation("Marks", back_populates='student')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
