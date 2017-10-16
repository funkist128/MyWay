#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3
import click
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash
import random, threading, webbrowser


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE   = os.path.join(app.root_path, 'MyWay.db'),
	SECRET_KEY = 'development key',
	USERNAME   = 'ann',
	PASSWORD   = '445513'

))

app.config.from_envvar('MYWAY_SETTINGS', silent = True)



# database stuff
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['account'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('Loggined')
			return redirect(url_for('index', join = 'true'))
	return render_template('login.html', error = error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out.')
	return redirect(url_for('login'))


@app.route('/index/<join>')
def index(join):
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if join == 'true':
			db = get_db()
			cur = db.execute('select * from customers where status="加入" order by id asc')
			customers = cur.fetchall()
			return render_template('index.html', customers = customers, join = 'true')
		else:
			db = get_db()
			cur = db.execute('select * from customers where status="未加入" order by id asc')
			customers = cur.fetchall()
			return render_template('index.html', customers = customers, join = 'false')
	

@app.route('/add', methods = ['GET', 'POST'])
def add():
	if not session.get('logged_in'):
		return render_template('login.html')

	if request.method == 'POST':
		print request.form
		db = get_db()
		db.execute('insert into customers (name, phone, status, type, abo_number, join_date, b_day, family,\
					occupation, rescreation, financial, achievement) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',\
					[request.form['name'], request.form['phone'], request.form['status'],\
					request.form['type'], request.form['abo_number'], request.form['join_date'], request.form['b_day'],\
					request.form['family'], request.form['occupation'], request.form['rescreation'],\
					request.form['financial'], request.form['achievement']])
		db.commit()
		flash('added new one')
		return redirect(url_for('index', join = 'true'))

	return render_template('add.html')

@app.route('/info/<cid>')
def info(cid):

	if not session.get('logged_in'):
		return render_template('login.html')

	queryForCustomer = 'select * from customers where id=%s' % cid
	queryForProgress = 'select * from customer_progress where cid=%s order by progress_date desc' % cid

	db = get_db()

	curForCustomer = db.execute(queryForCustomer)
	customer = curForCustomer.fetchall()

	curForProgress = db.execute(queryForProgress)
	progress = curForProgress.fetchall()

	return render_template('info.html', customer = customer, progress = progress)

@app.route('/delete/<cid>/<join>')
def delete(cid, join):
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	''' 
		delete customer and their progress
	'''
	query = 'delete from customers where id=%s' % cid
	queryForProgress = 'delete from customer_progress where cid=%s' % cid
	db.execute(query)
	db.execute(queryForProgress)
	db.commit()

	print "%s has been deleted." % cid

	return redirect(url_for("index", join = join))

@app.route('/newProgress/<cid>', methods = ['POST'])
def addProgress(cid):
	if not session.get('logged_in'):
		abort(401)

	db = get_db()
	db.execute("insert into customer_progress (cid, progress_date, progress_type, progress_info)\
				values (?, ?, ?, ?)", [cid, request.form['progress_date'], request.form['progress_type'],\
				request.form['progress_info']])
	db.commit()
	goesTo = "/info/%s" % cid
	return redirect(goesTo)


@app.route('/deleteProgress/<cid>/<pid>')
def delete_progress(cid, pid):
	if not session.get('logged_in'):
		abort(401)

	query = 'delete from customer_progress where id=%s' % pid
	db = get_db()
	db.execute(query)
	db.commit()
	print "%s's %s has been deleted." % (cid, pid)

	return redirect(url_for('info', cid = cid))

@app.route('/edit/<cid>', methods = ['GET', 'POST'])
def edit(cid):
	if not session.get('logged_in'):
		return render_template('login.html')

	if request.method == 'POST':
		db = get_db()
		db.execute('update customers set name=?, phone=?, status=?, type=?, abo_number=?, join_date=?\
						, b_day=?, family=?, occupation=?, rescreation=?, financial=?, achievement=?\
						where id=?', [request.form['name'], request.form['phone'], request.form['status'],\
						request.form['type'], request.form['abo_number'], request.form['join_date'], request.form['b_day'],\
						request.form['family'], request.form['occupation'], request.form['rescreation'],\
						request.form['financial'], request.form['achievement'], cid])
		db.commit()
		return redirect(url_for('info', cid = cid))
	else:
		db = get_db()
		cur = db.execute('select * from customers where id=?', [cid])
		customers = cur.fetchall()
		return render_template('edit.html', customers = customers)


if __name__ == '__main__':

	port = 5000 + random.randint(0, 999)
	url = "http://127.0.0.1:{0}/index/true".format(port)

	threading.Timer(1.25, lambda: webbrowser.open(url) ).start()

	app.run(port=port, debug=False)



