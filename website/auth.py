from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Parameters
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # second email is the one we are comparing
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    return render_template("about.html", user=current_user)

@auth.route('/view_egram', methods=['GET', 'POST'])
@login_required
def view_egram():
    return render_template("view_egram_data.html", user=current_user)

@auth.route('/bradycardia-therapy', methods=['GET', 'POST'])
@login_required
def bradycardia_therapy():
    # Retrieve the current user's parameter record
    parameter = Parameters.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # Retrieving values from the form
        lrl = request.form.get('lrl')
        url = request.form.get('url')
        max_sensor_rate = request.form.get('max_sensor_rate')
        fixed_av_delay = request.form.get('fixed_av_delay')
        dynamic_av_delay = request.form.get('dynamic_av_delay')
        sensed_av_delay_offset = request.form.get('sensed_av_delay_offset')
        atrial_amp = request.form.get('atrial_amp')
        ventricular_amp = request.form.get('ventricular_amp')
        atrial_pulse_width = request.form.get('atrial_pulse_width')
        ventricular_pulse_width = request.form.get('ventricular_pulse_width')
        atrial_sensitivity = request.form.get('atrial_sensitivity')
        ventricular_sensitivity = request.form.get('ventricular_sensitivity')
        vrp = request.form.get('vrp')
        arp = request.form.get('arp')
        pvarp = request.form.get('pvarp')
        pvarp_ext = request.form.get('pvarp_ext')
        hysteresis = request.form.get('hysteresis')
        rate_smoothing = request.form.get('rate_smoothing')
        atr_duration = request.form.get('atr_duration')
        atr_fallback_mode = request.form.get('atr_fallback_mode')
        atr_fallback_time = request.form.get('atr_fallback_time')
        activity_threshold = request.form.get('activity_threshold')
        reaction_time = request.form.get('reaction_time')
        response_factor = request.form.get('response_factor')
        recovery_time = request.form.get('recovery_time')

        # Update or create parameter record
        if parameter:
            # Update existing parameters
            parameter.lrl = lrl
            parameter.url = url
            parameter.max_sensor_rate = max_sensor_rate
            parameter.fixed_av_delay = fixed_av_delay
            parameter.dynamic_av_delay = dynamic_av_delay
            parameter.sensed_av_delay_offset = sensed_av_delay_offset
            parameter.atrial_amp = atrial_amp
            parameter.ventricular_amp = ventricular_amp
            parameter.atrial_pulse_width = atrial_pulse_width
            parameter.ventricular_pulse_width = ventricular_pulse_width
            parameter.atrial_sensitivity = atrial_sensitivity
            parameter.ventricular_sensitivity = ventricular_sensitivity
            parameter.vrp = vrp
            parameter.arp = arp
            parameter.pvarp = pvarp
            parameter.pvarp_ext = pvarp_ext
            parameter.hysteresis = hysteresis
            parameter.rate_smoothing = rate_smoothing
            parameter.atr_duration = atr_duration
            parameter.atr_fallback_mode = atr_fallback_mode
            parameter.atr_fallback_time = atr_fallback_time
            parameter.activity_threshold = activity_threshold
            parameter.reaction_time = reaction_time
            parameter.response_factor = response_factor
            parameter.recovery_time = recovery_time
        else:
            # Create new parameter record if one doesn't exist
            new_parameter = Parameters(
                user_id=current_user.id,
                lrl=lrl,
                url=url,
                max_sensor_rate=max_sensor_rate,
                fixed_av_delay=fixed_av_delay,
                dynamic_av_delay=dynamic_av_delay,
                sensed_av_delay_offset=sensed_av_delay_offset,
                atrial_amp=atrial_amp,
                ventricular_amp=ventricular_amp,
                atrial_pulse_width=atrial_pulse_width,
                ventricular_pulse_width=ventricular_pulse_width,
                atrial_sensitivity=atrial_sensitivity,
                ventricular_sensitivity=ventricular_sensitivity,
                vrp=vrp,
                arp=arp,
                pvarp=pvarp,
                pvarp_ext=pvarp_ext,
                hysteresis=hysteresis,
                rate_smoothing=rate_smoothing,
                atr_duration=atr_duration,
                atr_fallback_mode=atr_fallback_mode,
                atr_fallback_time=atr_fallback_time,
                activity_threshold=activity_threshold,
                reaction_time=reaction_time,
                response_factor=response_factor,
                recovery_time=recovery_time
            )
            db.session.add(new_parameter)

        # Commit the changes to the database
        db.session.commit()
        flash('Parameters updated successfully!', category='success')

    # Pass the parameter object to the template for displaying saved values
    return render_template("bradycardia_therapy.html", user=current_user, parameter=parameter)


@auth.route('/set-clock', methods=['GET', 'POST'])
@login_required
def set_clock():
    return render_template("set_clock.html", user=current_user)


@auth.route('/generate-report', methods=['GET', 'POST'])
@login_required
def generate_report():
    return render_template("generate_report.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # language = request.form.get('language')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)
