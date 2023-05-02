import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Teacher(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("subjects.id"))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    background_color = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    subject = orm.relation("Subject")
    school_classes = orm.relation("SchoolClass",
                                  secondary="teacher_to_class",
                                  backref="teachers")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
