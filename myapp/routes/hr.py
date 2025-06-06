from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from myapp.auth.decorators import role_required, no_cache
from myapp.models.users import User
from myapp.models.applicants import Applicant
from myapp.models.recruitment_history import RecruitmentHistory
from myapp.models.interviews import Interview
from myapp.models.referrals import Referral
from myapp.models.jobrequirement import JobRequirement
from myapp.utils import validate_file, update_status, can_upload_applicant
from myapp.extensions import db
from werkzeug.utils import secure_filename
from datetime import date, datetime
import os

bp = Blueprint('hr', __name__, url_prefix='/hr')
HR_ROLES = ('hr', 'admin')

@bp.route('/dashboard')
@no_cache
@login_required
@role_required(*HR_ROLES)
def dashboard():
    return render_template('hr/dashboard.html')

@bp.route('/applicants')
@no_cache
@login_required
@role_required(*HR_ROLES)
def applicants():
    applicants = Applicant.query.options(joinedload(Applicant.uploader)).order_by(Applicant.last_applied.desc()).all()
    hrs = User.query.filter_by(role='hr').all()
    for applicant in applicants:
        update_status(applicant.id)
    return render_template('hr/applicants.html', applicants=applicants, users=hrs)
        

@bp.route('/upload_applicants', methods=['GET', 'POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def upload_applicants():
    if '_user_id' not in session:
        current_app.logger.warning(f"Session expired for user {current_user.username}")
        return {'error': 'Session expired. Please log in again.'}, 401

    referrer_names = [
        {'id': user.id, 'name': user.name} for user in User.query.filter_by(role='referrer').all()
    ]

    if request.method == 'POST':
        file = request.files.get('cv')
        
        if not validate_file(file):
            flash('File is corrupted.', 'warning')
            current_app.logger.warning(f"File is corrupted: {file.filename}")
            return render_template('hr/upload.html', form_data=request.form)

        # Get all form data
        name = request.form.get('name')
        email = request.form.get('email')

        if not can_upload_applicant(email):
            flash('This candidate is under a 6-month freeze period. Please try later.', 'error')
            return redirect(url_for('hr.upload_applicants'))
        
        applicant = Applicant.query.filter_by(email=email).first()
        if applicant:
            applicant.last_applied = date.today()
            applicant.status = 'Applied'

        phone_number = request.form.get('phone_number')
        dob = request.form.get('dob')
        # Convert dob to date object if it's a string
        if isinstance(dob, str):
            try:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                # fallback for other formats or None
                dob = None
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        native_place = request.form.get('native_place')
        current_location = request.form.get('current_location')
        work_location = request.form.get('work_location')
        
        # Professional Information
        is_fresher = bool(request.form.get('is_fresher'))
        is_referred = bool(request.form.get('is_referred'))
        referred_by = int(request.form.get('referred_by')) if is_referred else None
        qualification = request.form.get('qualification')
        graduation_year = request.form.get('graduation_year')
        if graduation_year:
            graduation_year = int(graduation_year)
            
        # Internship Information
        current_internship = bool(request.form.get('current_internship'))
        internship_duration = request.form.get('internship_duration')
        if internship_duration:
            internship_duration = int(internship_duration)
        paid_internship = bool(request.form.get('paid_internship'))
        stipend = request.form.get('stipend')
        if stipend:
            stipend = int(stipend)
            
        referenced_from = request.form.get('referenced_from')
        linkedin_profile = request.form.get('linkedin_profile')
        github_profile = request.form.get('github_profile')
        
        # Current Employment Information (if not fresher)
        experience = request.form.get('experience')
        is_kanaka_employee = bool(request.form.get('is_kanaka_employee'))
        current_company = request.form.get('current_company')
        designation = request.form.get('designation')
        current_job_position = request.form.get('current_job_position')
        current_ctc = request.form.get('current_ctc')
        if current_ctc:
            current_ctc = int(current_ctc)
        expected_ctc = request.form.get('expected_ctc')
        if expected_ctc:
            expected_ctc = int(expected_ctc)
        notice_period = request.form.get('notice_period')
        if notice_period:
            notice_period = int(notice_period)
        tenure_at_current_company = request.form.get('tenure_at_current_company')
        current_offers_yes_no = bool(request.form.get('current_offers_yes_no'))
        current_offers_description = request.form.get('current_offers_description')
        reason_for_change = request.form.get('reason_for_change')
        comments = request.form.get('comments')

        # Handle file upload
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'applicants')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Create new applicant
        new_applicant = Applicant(
            name=name.title(),
            email=email,
            phone_number=phone_number,
            dob=dob,
            gender=gender,
            marital_status=marital_status,
            native_place=native_place.title() if native_place else None,
            current_location=current_location.title() if current_location else None,
            work_location=work_location.title() if work_location else None,
            graduation_year=graduation_year,
            is_fresher=is_fresher,
            qualification=qualification,
            current_internship=current_internship,
            internship_duration=internship_duration,
            paid_internship=paid_internship,
            stipend=stipend,
            experience=experience,
            referenced_from=referenced_from,
            linkedin_profile=linkedin_profile if linkedin_profile else 'Not Provided',
            github_profile=github_profile if github_profile else 'Not Provided',
            is_kanaka_employee=is_kanaka_employee,
            current_company=current_company,
            designation=designation,
            current_job_position=current_job_position.title() if current_job_position else None,
            current_ctc=current_ctc,
            expected_ctc=expected_ctc,
            notice_period=notice_period,
            tenure_at_current_company=tenure_at_current_company,
            current_offers_yes_no=current_offers_yes_no,
            current_offers_description=current_offers_description if current_offers_description else None,
            reason_for_change=reason_for_change if reason_for_change else 'Not Provided',
            comments=comments if comments else 'No comments',
            last_applied=date.today(),
            current_stage='Need to schedule test',
            cv_file_path=file_path,
            uploaded_by=current_user.id,
            is_referred=is_referred,
            referred_by=referred_by
        )
        
        try:
            db.session.add(new_applicant)
            db.session.commit()
            
            history = RecruitmentHistory(
                applicant_id=new_applicant.id,
                applied_date=date.today()
            )

            db.session.add(history)
            db.session.commit()

            flash('New applicant successfully created!', 'success')
            current_app.logger.info(f"New applicant (Name: {new_applicant.name.title()}) added by {current_user.username}")
            return redirect(url_for('hr.upload_applicants'))
            
        except IntegrityError as e:
            db.session.rollback()
            if 'email' in str(e.orig):
                flash('This email is already registered. Please use a different one.', 'error')
            elif 'phone_number' in str(e.orig):
                flash('This phone number is already registered. Please use a different one.', 'error')
            else:
                flash('Database error. Please try again.', 'error')
            current_app.logger.error(f"IntegrityError creating applicant: {str(e)}")
            return render_template('hr/upload.html', referrer_names=referrer_names, form_data=request.form)

    return render_template('hr/upload.html', referrer_names=referrer_names)

@bp.route('/view_applicant/<int:id>')
@no_cache
@login_required
@role_required(*HR_ROLES)
def view_applicant(id):
    update_status(id)
    applicant = Applicant.query.get_or_404(id)
    interviewers = User.query.filter_by(role='interviewer').all()

    return render_template('hr/view_applicant.html', applicant=applicant, interviewers=interviewers)

@bp.route('/schedule_test/<int:id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def schedule_test(id):
    date = request.form['test_date']

    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            date = None

    history = RecruitmentHistory.query.filter_by(applicant_id=id).first()
    history.test_scheduled = date
    db.session.commit()
    flash('Test scheduled successfully', 'success')
    current_app.logger.info(f"Test scheduled for applicant {id} on {date} by {current_user.username}")
    return redirect(url_for('hr.view_applicant', id=id))

@bp.route('/reschedule_test/<int:id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def reschedule_test(id):
    date = request.form['test_date']
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            date = None
    
    history = RecruitmentHistory.query.filter_by(applicant_id=id).first()
    if history and history.test_result is None:
        history.test_scheduled = date
        db.session.commit()
        flash('Test rescheduled successfully', 'success')
        current_app.logger.info(f"Test rescheduled for applicant {id} to {date} by {current_user.username}")
    else:
        flash('Cannot reschedule test - test result already exists', 'error')
        
    return redirect(url_for('hr.view_applicant', id=id))

@bp.route('/filter_applicants')
@no_cache
@login_required
@role_required(*HR_ROLES)
def filter_applicants():
    hr_users = User.query.filter_by(role='hr').all()
    
    hr_id = request.args.get('hr_id', '')
    
    if hr_id:
        applicants = Applicant.query.filter_by(uploaded_by=hr_id).order_by(Applicant.last_applied.desc()).all()
    else:
        applicants = Applicant.query.order_by(Applicant.last_applied.desc()).all()
    
    return render_template('hr/applicants.html', applicants=applicants, users=hr_users)

@bp.route('/applicants/<int:id>/download_cv')
@no_cache
@login_required
@role_required(*HR_ROLES)
def download_cv(id):
    return f"Download CV for Applicant {id}"

@bp.route('/schedule_interview/<int:id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def schedule_interview(id):
    date = request.form.get('interview_date')
    time = request.form.get('interview_time')
    interviewer_id = request.form.get('interviewer_id')

    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            date = None

    if isinstance(time, str):
        try:
            time = datetime.strptime(time, '%H:%M').time()
        except ValueError:
            try:
                time = datetime.strptime(time, '%H:%M:%S').time()
            except ValueError:
                time = None
    
    history = RecruitmentHistory.query.filter_by(applicant_id = id).first()

    if not history.interview_round_1_date:
        round = 1
        interview = Interview(applicant_id=id, date=date, time=time, round_number=round, interviewer_id=interviewer_id)
        db.session.add(interview)
        db.session.commit()
        history.interview_round_1_date = date
        history.interview_round_1_time = time
        
    elif not history.interview_round_2_date:
        round = 2
        interview = Interview(applicant_id=id, date=date, time=time, round_number=round, interviewer_id=interviewer_id)
        db.session.add(interview)
        db.session.commit()
        history.interview_round_2_date = date
        history.interview_round_2_time = time
        
    else:
        round = 3
        interview = Interview(applicant_id=id, date=date, time=time, round_number=round, interviewer_id=interviewer_id)
        db.session.add(interview)
        db.session.commit()
        history.hr_round_date = date
        history.hr_round_time = time
        
    db.session.commit()
    flash('Interview scheduled successfully', 'success')
    current_app.logger.info(f"Interview round {round} scheduled for applicant {id} on {date} by {current_user.username}")
    return redirect(url_for('hr.view_applicant', id=id))

@bp.route('/reject_application/<int:id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def reject_application(id):
    history = RecruitmentHistory.query.filter_by(applicant_id=id).first()
    history.rejected = True
    applicant = Applicant.query.get_or_404(id)
    applicant.status = 'Rejected'
    db.session.commit()
    current_app.logger.info(f"Candidate {applicant.name} rejected")
    flash('Candidate rejected', 'error')
    return redirect(url_for('hr.view_applicant', id=id))

@bp.route('/view_referrals')
@no_cache
@login_required
@role_required(*HR_ROLES)
def view_referrals():
    referrals = Referral.query.all()
    return render_template('hr/view_referrals.html', referrals=referrals)

@bp.route('/onboarding')
@no_cache
@login_required
@role_required(*HR_ROLES)
def onboarding():
    return "Onboarding and Offer Letter Page"

@bp.route('/filter_interviews')
@no_cache
@login_required
@role_required(*HR_ROLES)
def filter_interviews():
    hr_users = User.query.filter_by(role='hr').all()
    
    hr_id = request.args.get('hr_id', '')
    
    if hr_id:
        interviews = Interview.query\
            .filter_by(completed=False, scheduler_id=hr_id)\
            .options(
                joinedload(Interview.applicant),
                joinedload(Interview.interviewer),
                joinedload(Interview.scheduler)
            )\
            .all()
    else:
        interviews = Interview.query\
            .filter_by(completed=False)\
            .options(
                joinedload(Interview.applicant),
                joinedload(Interview.interviewer),
                joinedload(Interview.scheduler)
            )\
            .all()
    
    return render_template('hr/view_interviews.html', interviews=interviews, users=hr_users)

@bp.route('/reschedule_interview/<int:id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def reschedule_interview(id):
    date = request.form.get('interview_date')
    time = request.form.get('interview_time')
    interviewer_id = request.form.get('interviewer_id')

    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            date = None
    
    if isinstance(time, str):
        try:
            time = datetime.strptime(time, '%H:%M').time()
        except ValueError:
            try:
                time = datetime.strptime(time, '%H:%M:%S').time()
            except ValueError:
                time = None
    
    interview = Interview.query.get_or_404(id)
    
    interview.date = date
    interview.time = time
    interview.interviewer_id = interviewer_id
    
    history = RecruitmentHistory.query.filter_by(applicant_id=interview.applicant_id).first()
    if interview.round_number == 1:
        history.interview_round_1_date = date
        history.interview_round_1_time = time
    elif interview.round_number == 2:
        history.interview_round_2_date = date
        history.interview_round_2_time = time
    else:
        history.hr_round_date = date
        history.hr_round_time = time
    
    db.session.commit()
    flash('Interview rescheduled successfully', 'success')
    current_app.logger.info(f"Interview round {interview.round_number} rescheduled for applicant {interview.applicant_id} to {date} by {current_user.username}")
    
    referrer = request.referrer
    if referrer and 'view_interviews' in referrer:
        return redirect(url_for('hr.view_interviews'))
    return redirect(url_for('hr.view_applicant', id=interview.applicant_id))


# Job Listing Routes
@bp.route('/uploadjoblistings', methods=['GET', 'POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def upload_joblistings():
    if '_user_id' not in session:
        current_app.logger.warning(f"Session expired for user {current_user.username}")
        return {'error': 'Session expired. Please log in again.'}, 401
        
        # Get all form data
    job_id = request.form.get('job_id')
    position_name = request.form.get('position_name')
    job_description = request.form.get('job_description')

        # Create new applicant
    new_jobrequirement = JobRequirement(
        job_id=job_id,
        position_name=position_name.title(),
        job_description=job_description
        )
        
    try:
        db.session.add(new_jobrequirement)
        db.session.commit()
            
        flash('New job listing successfully created!', 'success')
        current_app.logger.info(f"New job listing (Posting: {new_jobrequirement.position_name.title()}) added by {current_user.username}")
        return redirect(url_for('hr.upload_applicants'))
            
    except IntegrityError as e:
        db.session.rollback()
        if 'job_id' in str(e.orig):
            flash('This job role is already listed.', 'error')
        elif 'job_description' in str(e.orig):
            flash('This job role is already listed.', 'error')
        else:
            flash('Database error. Please try again.', 'error')
        current_app.logger.error(f"IntegrityError creating applicant: {str(e)}")
        return render_template('jobs/addjob.html', form_data=request.form)

    return render_template('jobs/addjob.html')

@bp.route('/joblisiting_update/<int:job_id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def joblisting_update(job_id):
    joblisting = JobRequirement.query.get_or_404(job_id)
    position_name = request.form.get('position_name')
    job_description = request.form.get('job_description')
    
    if not new_password or not confirm_password:
        flash('Both password fields are required', 'error')
        return redirect(url_for('admin.edit_user', user_id=user_id))
    
    joblisting.position_name = position_name
    joblisting.job_description = job_description
    db.session.commit()
    
    current_app.logger.info(f"Details updated for job listing {joblisting.position_name} by Admin {current_user.username}")
    flash('Job listing details updated successfully', 'success')

    if request.referrer.endswith(url_for('main.profile')):
        return redirect(url_for('main.profile', user=current_user))
    else:
        return redirect(url_for('admin.edit_user', user_id=user_id))


@bp.route('/delete_joblisting/<int:job_id>', methods=['POST'])
@no_cache
@login_required
@role_required(*HR_ROLES)
def delete_joblisting(job_id):
    joblisting = JobRequirement.query.get_or_404(job_id)
    db.session.delete(joblisting)
    db.session.commit()
    current_app.logger.info(f"Job listing {joblisting.position_name} deleted by Admin {current_user.username}")
    flash('Job listing deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))
