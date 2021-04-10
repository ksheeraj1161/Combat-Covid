from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import smtplib
import ssl
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fpdf import FPDF
from datetime import datetime
from keras.preprocessing import image
from keras.models import load_model
import numpy as np
import openai
import speech_recognition as sr
import pyttsx3

# import json

# with open('/etc/config.json') as config_file:
#   config = json.load(config_file)


# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

# app.config.from_object(Config)
TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./static')
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

countries1 = ["India", "USA", "Canada", "Italy"]
countries2 = ["China", "UK", "Spain", "Germany"]
countries3 = ["France", "Turkey", "Iran", "Russia"]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/kandr/Desktop/Combat Covid/file.db'
db = SQLAlchemy(app)

saved = False
text = ''

def create_pdf(id, email, age, sex, result, report_type):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Times", "B", 24)
    pdf.cell(0, 20, "COV-AI-D Diagnostic Report", 0, 1, "C")
    pdf.set_font("Times", "", 16)
    pdf.cell(0, 10, "covaid.report@gmail.com", 0, 1, "C")
    pdf.line(20, 42, 210-20, 42)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "Report Date:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, "{}".format(datetime.now().date()), 0, 1)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "ID:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, id, 0, 1)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "Email:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, email, 0, 1)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "Age:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, age, 0, 1)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "Sex:")

    pdf.set_font("Times", "", 12)
    pdf.cell(0, 5, sex, 0, 1)

    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 5, "Final Result:")

    pdf.set_font("Times", "U", 12)
    pdf.cell(0, 5, "{}% chances of COVID-19 infection".format(result), 0, 1)

    pdf.set_font("Times", "B", 14)
    pdf.cell(100, 25, "What does this result mean for you?")
    pdf.cell(0, 5, "", 0, 1)

    pdf.set_font("Times", "", 12)

    if report_type != "technician":
        if result <= 0.5:
            text1 = "Since the chances of you having COVID-19 based on your clinical information are greater than 50%, we"
            text2 = "recommend that you immeditaely visit the nearest hospital and consult the physician."
            text3 = ""

        else:
            text1 = "Since the chances of you having COVID-19 based on your clinical information are less than 50%, we"
            text2 = "recommend that you quarantine for at least the next week and monitor any developments."
            text3 = "It is recommended that you fill this form again and get the diagnosis based on your new symptoms."

    else:
        if result <= 0.5:
            text1 = "Since the chances of the patient having COVID-19 based on the CT scan are greater than 50%, we"
            text2 = "recommend immediate consultation with a radiologist."
            text3 = ""

        else:
            text1 = "Since the chances of the patients having COVID-19 based on the CT scan are less than 50%, we"
            text2 = "recommend that they quarantine for at least the next week and monitor any developments."
            text3 = "It is recommended that they fill this form again and get the diagnosis based on their new symptoms."

    pdf.cell(0, 25, text1)
    pdf.cell(0, 5, "", 0, 1)
    pdf.cell(0, 25, text2) 
    pdf.cell(0, 5, "", 0, 1)
    pdf.cell(0, 5, "", 0, 1)
    pdf.cell(0, 25, text3)

    pdf.cell(0, 5, "", 0, 1)
    pdf.cell(0, 5, "", 0, 1)


    if report_type == "audio_patient":
        global text

        pdf.set_font("Times", "B", 14)
        pdf.cell(100, 25, "What audio did we receive? (Try again if most of the text is incorrect)")
        pdf.cell(0, 5, "", 0, 1)

        pdf.set_font("Times", "", 12)

        length = len(text)
        temp = 0
        for i in range(0, length, 92):
            if length < 92:
                pdf.cell(0, 25, text)
                pdf.cell(0, 5, "", 0, 1)
            else:
                temp += 92
                pdf.cell(0, 25, text[:temp])
                pdf.cell(0, 5, "", 0, 1)


    if report_type == "technician":
        pdf.image("temp.png", x=45, y=150, w=128, h=128)

        pdf.cell(0, 10, "", 0, 1)
        pdf.set_font("Times", "B", 12)
        pdf.cell(
            0, 25, "Preliminary AP scanogram of the chest was obtained. Contiguous axial scans of slice thickness 1 mm")

        pdf.cell(0, 5, "", 0, 1)
        pdf.cell(0, 25, "were taken from the root of thoracic inlet till the posterior costophrenic recesses, at interval of 10mm.")
        os.remove("temp.png")

    pdf.output("document.pdf")

def email_to_user(receiver_email):
    port = 465  # For SSL
    password = "Ksheeraj1"

    # Create a secure SSL context
    context = ssl.create_default_context()

    subject = "Here's your report from COV-AI-D, we hope this helps you :)"
    body = "Greetings,\nPlease find attached the report we created using our AI model based on your data input on www.covaid.tech\n\nWe hope this helps you and your patient.\nThank you,\nTeam COV-AI-D\nShubh & Arsh"
    sender_email = "covaid.report@gmail.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "document.pdf"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("covaid.report@gmail.com", password)
        server.sendmail(sender_email, receiver_email, text)
    
    os.remove("document.pdf")


def model_result(ct_scan_blob):
    model = load_model('my_model.h5')

    with open('temp.png', 'wb') as file:
        file.write(ct_scan_blob)

    test_image = image.load_img('temp.png', target_size=(64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    return model.predict(test_image)


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    elif s == "null":
        return None


class ClinicalData(db.Model):
    # Demographics
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    occupation = db.Column(db.String(200))
    city = db.Column(db.String(200))
    country = db.Column(db.String(200))
    people_in_household = db.Column(db.Integer)

    # Personal History
    disease_medication = db.Column(db.String(200))
    diet = db.Column(db.String(10))
    sleeping_pattern = db.Column(db.String(10))
    appetite = db.Column(db.String(10))
    bowel_bladder = db.Column(db.String(10))
    alcohol_intake = db.Column(db.String(20))
    smoke_intake = db.Column(db.String(20))
    nervous = db.Column(db.String(20))
    personal_problem = db.Column(db.String(20))
    stressed = db.Column(db.String(20))
    psychological_illness = db.Column(db.String(10))

    # Past History
    prev_hospitalizations = db.Column(db.String(500))
    prev_blood_transfusion = db.Column(db.String(10))

    # Family History
    diabetes = db.Column(db.Boolean)
    hypertension = db.Column(db.Boolean)
    thyroid = db.Column(db.Boolean)
    epilepsy = db.Column(db.Boolean)
    tuberculosis = db.Column(db.Boolean)
    asthma = db.Column(db.Boolean)
    family_history = db.Column(db.String(500))

    # for COVID
    COVID_form_fill_guy = db.Column(db.String(10))
    marital_history = db.Column(db.String(500))
    sound_breathing = db.Column(db.Boolean)
    difficulty_breathing = db.Column(db.Boolean)
    fever = db.Column(db.Boolean)
    chills = db.Column(db.Boolean)
    hoarseness = db.Column(db.Boolean)
    loss_of_smell_taste = db.Column(db.Boolean)
    headache = db.Column(db.Boolean)
    diarrhoea = db.Column(db.Boolean)
    cough = db.Column(db.Boolean)
    cold = db.Column(db.Boolean)
    chest_pain = db.Column(db.Boolean)
    muscle_ache = db.Column(db.Boolean)
    other_symptoms = db.Column(db.String(500))
    COVID_complaints = db.Column(db.String(500))
    COVID_duration_between_symptoms_and_hospital = db.Column(db.String(200))
    COVID_isolated = db.Column(db.String(10))
    protection = db.Column(db.String(500))
    shifts = db.Column(db.String(500))
    difficulties = db.Column(db.String(500))
    residing_place = db.Column(db.Boolean)
    recovered_description = db.Column(db.String(500))
    recovered_relapses = db.Column(db.String(500))
    recovered_meds = db.Column(db.String(500))

    ct_scan = db.Column(db.LargeBinary)

@app.route('/')
def landing_page():
    global saved
    if saved:
        saved = False
        return render_template('landing_page.html', saved=True)
    else:
        return render_template('landing_page.html', saved=False)


@app.route('/audio-form')
def audio_form():
    return render_template('audio_form.html')


@app.route('/audio-form-upload', methods=['POST'])
def audio_form_upload():
    global text
    r = sr.Recognizer()
    path_to_audio_file = "C:\\Users\\arsh\\Downloads\\audio.wav"
    with sr.AudioFile(path_to_audio_file) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        print(text, flush=True)

    os.remove(path_to_audio_file)
    openai.api_key = "sk-2jRMD9G0ojitxcVNfUCtBaE6OVcrju2WQ4Xxs43w"
    res = openai.Classification.create(
        search_model="ada",
        model="curie",
        examples=[
            ["Hello! I am a 23-year-old male I am 1.65 m tall and weigh 65 kg. Recently my sleeping pattern has been all over the place. I am also losing my appetite and have not been having proper bowel movements as of late. I  drink alcohol weekly and also use tobacco products every day. I have recently developed Headaches, difficulty in breathing, cough, cold, mild chills, Chest pain. I have also lost my sense of smell and taste.", "Positive"],
            ["Hello! I am a 23-year-old female. I am 1.6 m tall and weigh 62 kg. I  drink alcohol monthly and even use tobacco products occasionally. I have started to produce this random sound when I breathe. I also have diarrhea, fever. My voice is getting rough and I also have constant muscle ache.", "Positive"],
            ["Hello! I am a 26-year-old male. I am 1.75 m tall and weigh 82 kg. Recently my sleeping pattern has been all over the place. I am also losing my appetite and have not been having proper bowel movements as of late. I  do not drink alcohol and don't use tobacco products. I don't have any symptoms of covid.", "Negative"],
            ["Hello! I am a 21-year-old male. I am 1.8 m tall and weigh 80 kg. I have recently developed Headaches, difficulty in breathing, cough, cold, mild chills, Chest pain. I have also lost my sense of smell and taste.", "Positive"],
            ["Hello! I am a 24-year-old male. I am 1.6 m tall and weigh 58 kg. I  drink alcohol monthly and even use tobacco products occasionally. I have started to produce this random sound when I breathe. I also have diarrhea, fever. My voice is getting rough and I also have constant muscle ache.", "Positive"],
            ["Hello! I am a 22-year-old male. I am 1.65 m tall and weigh 70 kg. Recently my sleeping pattern has been all over the place. I am also losing my appetite and have not been having proper bowel movements as of late. I  drink alcohol weekly and also use tobacco products every day. I have recently developed Headaches, difficulty in breathing, cough, cold, mild chills, Chest pain. I have also lost my sense of smell and taste.", "Positive"],
            ["Hello! I am a 26-year-old male. I am 1.75 m tall and weigh 82 kg. Recently my sleeping pattern has been all over the place. I am also losing my appetite and have not been having proper bowel movements as of late. I  do not drink alcohol and don't use tobacco products. I don't have any symptoms of covid or hematuria (random bleeding).", "Negative"]
        ],
        query=text,
        labels=["Positive", "Negative"],
    )

    email_ = request.form.get('email')
    age_ = "NA"
    gender_ = "NA"

    if res.label == "Positive":
        result = 100
    else:
        result = 0

    create_pdf("2", email_, age_, gender_, result, report_type="audio_patient")
    email_to_user(email_)

    return redirect(url_for('landing_page'))


@app.route('/formimages')
def formimages():
    return render_template('form_images.html')


@app.route('/form')
def render_static():
    return render_template('form.html')


@app.route('/ctupload', methods=['POST'])
def ctupload():
    id_ = request.form.get('id')
    email_ = request.form.get('email')
    ct_scan_ = request.files['ct_scan']
    ct_scan_blob = ct_scan_.read()
    age_ = str(ClinicalData.query.filter(ClinicalData.id == id_).first().age)
    sex_ = ClinicalData.query.filter(ClinicalData.id == id_).first().gender

    num_rows_updated = ClinicalData.query.filter_by(
        id=id_).update(dict(ct_scan=ct_scan_blob))
    db.session.commit()

    result = float(model_result(ct_scan_blob))
    create_pdf(id_, email_, age_, sex_.title(), result * 100, "technician")
    email_to_user(email_)

    return redirect(url_for('landing_page'))


@app.route('/clinicalupload', methods=['POST'])
def clinicalupload():
    email_ = request.form.get('email')
    age_ = request.form.get('age')
    gender_ = request.form.get('gender')
    occupation_ = request.form.get('occupation')
    city_ = request.form['city']
    country_ = request.form['country']
    people_in_household_ = request.form['people_in_household']
    disease_medication_ = request.form['disease_medication']
    diet_ = request.form['diet']

    sleeping_pattern_ = request.form['sleeping_pattern']
    appetite_ = request.form['appetite']
    bowel_bladder_ = request.form['bowel_bladder']
    height_ = request.form['height']
    weight_ = request.form['weight']
    alcohol_intake_ = request.form['alcohol_intake']
    smoke_intake_ = request.form['smoke_intake']
    nervous_ = request.form['nervous']
    personal_problem_ = request.form['personal_problem']
    stressed_ = request.form['stressed']
    psychological_illness_ = request.form['psychological_illness']

    prev_hospitalizations_ = request.form['prev_hospitalizations']
    prev_blood_transfusion_ = request.form['prev_blood_transfusion']
    diabetes_ = str_to_bool(request.form['diabetes'])
    hypertension_ = str_to_bool(request.form['hypertension'])
    thyroid_ = str_to_bool(request.form['thyroid'])
    epilepsy_ = str_to_bool(request.form['epilepsy'])
    tuberculosis_ = str_to_bool(request.form['tuberculosis'])
    asthma_ = str_to_bool(request.form['asthma'])
    family_history_ = request.form['family_history']

    COVID_form_fill_guy_ = request.form['COVID_form_fill_guy']
    marital_history_ = request.form['marital_history']
    sound_breathing_ = str_to_bool(request.form['sound_breathing'])
    difficulty_breathing_ = str_to_bool(request.form['difficulty_breathing'])
    fever_ = str_to_bool(request.form['fever'])
    chills_ = str_to_bool(request.form['chills'])
    hoarseness_ = str_to_bool(request.form['hoarseness'])
    loss_of_smell_taste_ = str_to_bool(request.form['loss_of_smell_taste'])
    headache_ = str_to_bool(request.form['headache'])
    diarrhoea_ = str_to_bool(request.form['diarrhoea'])
    cough_ = str_to_bool(request.form['cough'])
    cold_ = str_to_bool(request.form['cold'])
    chest_pain_ = str_to_bool(request.form['chest_pain'])
    muscle_ache_ = str_to_bool(request.form['muscle_ache'])
    other_symptoms_ = request.form['other_symptoms']
    protection_ = request.form['protection']
    shifts_ = request.form['shifts']
    difficulties_ = request.form['difficulties']
    COVID_complaints_ = request.form['COVID_complaints']
    COVID_duration_between_symptoms_and_hospital_ = request.form[
        'COVID_duration_between_symptoms_and_hospital']
    COVID_isolated_ = request.form['COVID_isolated']
    residing_place_ = str_to_bool(request.form['residing_place'])
    recovered_description_ = str_to_bool(request.form['recovered_description'])
    recovered_relapses_ = str_to_bool(request.form['recovered_relapses'])
    recovered_meds_ = str_to_bool(request.form['recovered_meds'])

    obj = ClinicalData(email=email_,
                       age=age_,
                       gender=gender_,
                       occupation=occupation_,
                       city=city_,
                       country=country_,
                       people_in_household=people_in_household_,
                       disease_medication=disease_medication_,
                       diet=diet_,
                       sleeping_pattern=sleeping_pattern_,
                       appetite=appetite_,
                       bowel_bladder=bowel_bladder_,
                       height=height_,
                       weight=weight_,
                       alcohol_intake=alcohol_intake_,
                       smoke_intake=smoke_intake_,
                       nervous=nervous_,
                       personal_problem=personal_problem_,
                       stressed=stressed_,
                       psychological_illness=psychological_illness_,
                       prev_hospitalizations=prev_hospitalizations_,
                       prev_blood_transfusion=prev_blood_transfusion_,
                       diabetes=diabetes_,
                       hypertension=hypertension_,
                       thyroid=thyroid_,
                       epilepsy=epilepsy_,
                       tuberculosis=tuberculosis_,
                       asthma=asthma_,
                       family_history=family_history_,
                       COVID_form_fill_guy=COVID_form_fill_guy_,
                       marital_history=marital_history_,
                       sound_breathing=sound_breathing_,
                       difficulty_breathing=difficulty_breathing_,
                       fever=fever_,
                       chills=chills_,
                       hoarseness=hoarseness_,
                       loss_of_smell_taste=loss_of_smell_taste_,
                       headache=headache_,
                       diarrhoea=diarrhoea_,
                       cough=cough_,
                       cold=cold_,
                       chest_pain=chest_pain_,
                       muscle_ache=muscle_ache_,
                       other_symptoms=other_symptoms_,
                       COVID_complaints=COVID_complaints_,
                       COVID_duration_between_symptoms_and_hospital=COVID_duration_between_symptoms_and_hospital_,
                       COVID_isolated=COVID_isolated_,
                       protection=protection_,
                       shifts=shifts_,
                       difficulties=difficulties_,
                       residing_place=residing_place_,
                       recovered_description=recovered_description_,
                       recovered_relapses=recovered_relapses_,
                       recovered_meds=recovered_meds_
                       )

    db.session.add(obj)
    db.session.commit()
    global saved
    saved = True

    id_ = str(obj.id)
    create_pdf(id_, email_, age_, gender_.title(), 0.2, report_type="patient")
    email_to_user(email_)
    return redirect(url_for('landing_page'))


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, port=5000)
    