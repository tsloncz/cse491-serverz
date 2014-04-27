import os
from flask import Flask, render_template,redirect, request,send_from_directory

uploadFolder = 'flaskUploads'
allowedExtensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = uploadFolder

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in allowedExtensions

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    file = request.files['file']
    print "trying to upload: ", file.filename
    if file and allowed_file(file.filename):
#filename = secure_filename(file.filename)
      filename = file.filename
      print "file: ", filename
      file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))
      print "file saved"
      return redirect(url_for('uploaded_file',filename='filename'))
  return '''
  <!doctype html>
  <title>Upload new File</title>
  <h1>Upload new File</h1>
  <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
      <input type=submit value=Upload>
   </form>
   '''

@app.route("/images")
def images():
  return render_template('index.html')

@app.route('/show/<filename>')
def uploaded_file(filename):
  print "In uploaded_file with: "
  filename = '../flaskUploads/' + filename
  return render_template('template.html', filename=filename)

@app.route('/flaskUploads/<filename>')
def send_file(filename):
  print "in send_file with: ",filename
  return send_from_directory(uploadFolder, filename)

if __name__ == "__main__":
  print "Serving from  http://arctic.cse.msu.edu:8080/"
  app.run('0.0.0.0', 8080)
