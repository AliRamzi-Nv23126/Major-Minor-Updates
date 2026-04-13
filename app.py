from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean, default=False)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    done = BooleanField('Done')
    submit = SubmitField('Submit')

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, done=form.done.data)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.done = form.done.data
        db.session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.done.data = task.done
    return render_template('edit.html', form=form)

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)