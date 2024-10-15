from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import smtplib


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Todo_Form(FlaskForm):
    time_created = StringField('Date', validators=[DataRequired()])
    task = StringField('Task', validators=[DataRequired()])
    due_date = StringField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

#CONFIGURE TABLE
class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time_created: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    due_date: Mapped[str] = mapped_column(String(250), nullable=False)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

@app.route("/")
def home():
    result = db.session.execute(db.select(Task).order_by(Task.id))
    tasks = result.scalars().all()
    return render_template("index.html", tasks=tasks, all_tasks=range(len(tasks)))

@app.route('/add', methods=["GET", "POST"])
def add_task():
    form = Todo_Form()
    if form.validate_on_submit():
        new_post = Task(
            time_created=form.time_created.data,
            task=form.task.data,
            due_date=form.due_date.data,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home') + '#to_do')
    return render_template("add.html", form=form)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    my_email = "your email"
    password = "password"
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('phone')
        message = request.form.get('message')

        # Sending email
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(
                from_addr=my_email,
                to_addrs="to address",
                msg=f"Subject: Contact from User\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Subject: {subject}\n"
                    f"Message: {message}"
            )
        return render_template("index.html")
    return render_template("index.html")

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)  # Assuming Task is your model
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')  # Flash a success message
    else:
        flash('Task not found!', 'error')  # Flash an error message
    return redirect(url_for('home') + '#to_do')  # Redirect to your task list page


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = Todo_Form(obj=task)
    if form.validate_on_submit():
        task.task = form.task.data
        task.time_created = form.time_created.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('home') + '#to_do')
    return render_template('edit_task.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

#________________________RUN THIS FIRST TIME TO FILL DB_________________#
# with app.app_context():
    #     db.create_all()
    #
    #     # Insert first time data
    #     new_task = Task(time_created="2023-10-15 12:00", task="Write tutorial", due_date="2023-10-20")
    #     db.session.add(new_task)
    #
    #     # Insert multiple entries
    #     task_list = [
    #         Task(time_created="2023-10-16 08:30", task="Review pull request", due_date="2023-10-18"),
    #         Task(time_created="2023-10-17 09:45", task="Team meeting", due_date="2023-10-19")
    #     ]
    #     db.session.add_all(task_list)
    #
    #     # Commit the session to write data to the database
    #     db.session.commit()
    #
    #     print("Database has been populated!")