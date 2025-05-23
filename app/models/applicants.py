from app.extensions import db

class Applicant(db.Model):
    __tablename__ = 'applicants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.Integer)
    age = db.Column(db.Integer)
    experience = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    location = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    is_kanaka_employee = db.Column(db.Boolean, default = False)
    is_referred = db.Column(db.Boolean, default = False)
    applied_date = db.Column(db.Date)
    current_stage = db.Column(db.String(100))
    cv_file_path = db.Column(db.String(255))
    comments = db.Column(db.Text)
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    history_entries = db.relationship("RecruitmentHistory", back_populates="applicant", cascade="all, delete-orphan")
    referrer = db.relationship("User", back_populates="referred_applicants")