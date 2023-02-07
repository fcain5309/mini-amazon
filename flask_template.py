from flask import Flask, request, redirect, url_for
from flask import render_template
from database import db_session
from models import Car
import pdb


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return redirect(url_for('neoindex'))

@app.route('/neoindex', methods = ["GET","POST"])
def neoindex():
  if request.method == 'POST':


    return redirect(url_for('/search_name',namae = namae))


  return render_template('neoindex.html')




#worth noting when we're embedding python in flask we're using something called a
#jinja template https://jinja.palletsprojects.com/en/2.10.x/templates/
@app.route('/python')
def show_python():
  return render_template(
    'python.html',
    car_list=["Ford", "Jaguar", "Hyundai"],
    car_dictionary={"make": "Ford", "model": "Mustang", "year": "2019", "color":"red"}
  )

@app.route('/database')
def database():
  return render_template(
    'database.html',
    cars = Car.query.all()
  )

@app.route('/add_car')
def add_car():
  make = request.args.get("make")
  model = request.args.get("model")
  color = request.args.get("color")
  year = request.args.get("year")

  car = Car(make, model, color, year)
  db_session.add(car)
  db_session.commit()

  return redirect(url_for('database'))

@app.route('/search_name')
def search_name():
  namae = request.args.get("name")
  print("name: ",namae)
#  car = Car(make, model, color, year)
#  db_session.add(car)
#  db_session.commit()

  return redirect(url_for('database'))


@app.route('/style')
def style():
    return render_template('index_with_style.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()