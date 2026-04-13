from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    due_date = DateField('Due Date', format='%Y-%m-%d')
    status = SelectField('Status', choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('done', 'Done')], default='pending')
    submit = SubmitField('Submit')

@app.route('/')
def index():
    q = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    sort_by = request.args.get('sort', 'created_at')

    query = Task.query
    if q:
        query = query.filter(
            (Task.title.contains(q)) | (Task.description.contains(q))
        )
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)

    if sort_by == 'due_date':
        query = query.order_by(Task.due_date)
    elif sort_by == 'priority':
        # Simple sort: high > medium > low
        query = query.order_by(db.case(
            (Task.priority == 'high', 1),
            (Task.priority == 'medium', 2),
            (Task.priority == 'low', 3)
        ))
    else:
        query = query.order_by(Task.created_at.desc())

    tasks = query.all()
    return render_template('index.html', tasks=tasks, q=q, status_filter=status_filter, priority_filter=priority_filter, sort_by=sort_by)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            status=form.status.data
        )
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
        task.description = form.description.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.priority.data = task.priority
        form.due_date.data = task.due_date
        form.status.data = task.status
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