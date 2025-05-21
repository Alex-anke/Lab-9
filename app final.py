from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///towns.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    town = db.Column(db.String(100), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            town = request.form['town'].strip().title()
            visit_date = datetime.strptime(request.form['visit_date'], '%Y-%m-%d').date()

            if len(town) < 2:
                raise ValueError("Слишком короткое название города")

            new_visit = Visit(town=town, visit_date=visit_date)
            db.session.add(new_visit)
            db.session.commit()
            flash('Город успешно добавлен!', 'success')

        except ValueError as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка сервера', 'danger')

        return redirect(url_for('index'))

    visits = Visit.query.order_by(Visit.visit_date.desc()).all()
    return render_template('index.html', visits=visits)


@app.route('/clear', methods=['POST'])
def clear():
    try:
        db.session.query(Visit).delete()
        db.session.commit()
        flash('Все записи удалены!', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при очистке', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)