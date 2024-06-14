import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from resume_matcher.scripts.processor import Processor
from resume_matcher.scripts.get_score import get_score
from resume_matcher.scripts.utils import find_path, read_json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

cwd = find_path("Resume-Matcher")
PROCESSED_RESUMES_PATH = os.path.join(cwd, "Data", "Processed", "Resumes/")
PROCESSED_JOB_DESCRIPTIONS_PATH = os.path.join(cwd, "Data", "Processed", "JobDescription/")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return redirect(request.url)
    
    resume = request.files['resume']
    job_description = request.files['job_description']
    
    if resume.filename == '' or job_description.filename == '':
        return redirect(request.url)
    
    resume_filename = secure_filename(resume.filename)
    jd_filename = secure_filename(job_description.filename)
    
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
    jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
    
    resume.save(resume_path)
    job_description.save(jd_path)
    
    # Process files
    processor = Processor(resume_path, "resume")
    processor.process()
    
    processor = Processor(jd_path, "job_description")
    processor.process()
    
    # Get filenames
    processed_resume_filename = os.listdir(PROCESSED_RESUMES_PATH)[0]
    processed_jd_filename = os.listdir(PROCESSED_JOB_DESCRIPTIONS_PATH)[0]
    
    resume_dict = read_json(os.path.join(PROCESSED_RESUMES_PATH, processed_resume_filename))
    job_dict = read_json(os.path.join(PROCESSED_JOB_DESCRIPTIONS_PATH, processed_jd_filename))
    
    resume_keywords = resume_dict["extracted_keywords"]
    job_description_keywords = job_dict["extracted_keywords"]
    
    resume_string = " ".join(resume_keywords)
    jd_string = " ".join(job_description_keywords)
    
    final_result = get_score(resume_string, jd_string)
    scores = [r.score for r in final_result]
    
    return render_template('result.html', scores=scores)


if __name__ == '__main__':
    app.run(debug=True)
