from flask import render_template, url_for, flash, redirect, request
from server import app, cur, bcrypt, login_manager, con
from forms import RegistrationForm, LoginForm, CommentForm, AddInfoForm, ReservationForm, ExperienceForm, UpdateForm, UpdateAcm, ComposerForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import date,datetime
from user import get_user

@login_manager.user_loader
def load_user(username):
	return get_user(username)

@app.route("/")
@app.route("/home")
def home():
	cur.execute("select count(username) from person")
	person = cur.fetchone()
	cur.execute("select count(user_id) from accompanist")
	acm = cur.fetchone()
	return render_template('home.html', person=person, acm= acm)
	
@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		sql="select username from person where username='{}'".format(form.username.data)
		cur.execute(sql)
		account = cur.fetchone()
		if account is None:
			sql="select username from person where mail='{}'".format(form.email.data)
			cur.execute(sql)
			account = cur.fetchone()
			if account is None:
				hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
				sql="insert into person (name,surname,username,password,mail,is_acm) values(%s,%s,%s,%s,%s,%s)"
				cur.execute(sql,(form.name.data, form.surname.data, form.username.data, hashed_password, form.email.data, bool(form.is_acm.data)))
				con.commit()
				if bool(form.is_acm.data) == True:
					sql ="select user_id from person where username = '{}'".format(form.username.data)
					cur.execute(sql)
					user_id = cur.fetchone()
					cur.execute("insert into accompanist (user_id) values(%s)",(user_id))
					cur.execute("insert into vote (user_id) values(%s)",(user_id))
					con.commit()
					user=get_user(form.username.data)
					login_user(user)
					flash('Your account has been created please add more information.')
					return redirect(url_for('add_info', username = form.username.data))
				flash('Your account has been created!')
				return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/add_info/<username>", methods=['GET', 'POST'])
@login_required
def add_info(username):
	sql="select user_id from person where username = '{}'".format(username)
	cur.execute(sql)
	user_info = cur.fetchone()

	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()
	form = AddInfoForm()

	if form.validate_on_submit():
		sql = "update accompanist set phone_num = '{}', city='{}', university = '{}', price = '{}' where user_id = {}".format(form.phone.data, form.city.data, form.university.data, form.price.data, user_info[0])
		cur.execute(sql)
		con.commit()
		if request.method == 'POST':
			selected = request.form.getlist('composer')
			for selection in selected:
				sql = "select composer_id from composer where surname = '%s'"%selection
				cur.execute(sql)
				comp_id =cur.fetchone()
				sql = "insert into acm_comp (acm_id, composer_id) values({},{})".format(user_info[0],comp_id[0])
				cur.execute(sql)
			con.commit()
			flash('Informations are added.')
			return redirect(url_for('home'))
	return render_template('addinfo.html', composers = composers, title = "Add Information", form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = get_user(form.username.data)
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			flash('Login Successful.')
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account/<username>")
@login_required
def account(username):
	sql = "select user_id,name,surname,username from person where username = '%s'" %username
	cur.execute(sql)
	user = cur.fetchone()
	sql3 = "select person.name, person.surname, person.username from acm_cust inner join person on person.user_id = acm_cust.acm_id where acm_cust.customer_id = {}".format(user[0])
	cur.execute(sql3)
	acms = cur.fetchall()
	return render_template('account.html', title='Account', user = user, acms = acms)

@app.route("/profile/<username>")
def profile(username):
	sql = "select user_id from person where username = '%s'" %username
	cur.execute(sql)
	user_id= cur.fetchone()
	if user_id is not None:
		info = """select person.name, person.surname, person.username, accompanist.phone_num, 
			person.mail, accompanist.university, accompanist.city, accompanist.price, vote.vote, vote.score 
			from person inner join accompanist on accompanist.user_id= person.user_id
			inner join vote on vote.user_id= person.user_id where person.user_id = {}""".format(user_id[0])
		cur.execute(info)
		user_info = cur.fetchone()

		repertoire_info = """select composer.surname from acm_comp, composer, accompanist
							where accompanist.user_id = {}  and  acm_comp.acm_id = accompanist.user_id and acm_comp.composer_id = composer.composer_id""".format(user_id[0])
		cur.execute(repertoire_info)
		repertoire = cur.fetchall()

		comment_info = """select person.name, person.surname, person.username, comments.com_content, comments.com_date 
						from comments inner join person on comments.customer_id = person.user_id
						where comments.acm_id = %s""" %user_id[0]
		cur.execute(comment_info)
		comments = cur.fetchall()

		experience_info = """select experience.exp_year, experience.city from experience inner join accompanist on experience.acm_id = accompanist.user_id
							where accompanist.user_id = {}""".format(user_id[0])
		cur.execute(experience_info)
		experiences = cur.fetchall()

		reservation_info = """select reservation.rsr_date, reservation.city, reservation.content from reservation inner join accompanist on reservation.acm_id = accompanist.user_id
							where accompanist.user_id = {}""".format(user_id[0])
		cur.execute(reservation_info)
		reservations = cur.fetchall()

		return render_template('profile.html', title='Profile', user = user_info, comments = comments, repertoire = repertoire, reservations = reservations, experiences = experiences)
	else:
		flash('No such accompanist account.')
		return redirect(url_for('home'))

@app.route("/list_profiles")
def list_profiles():
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score,person.user_id
			from person inner join accompanist on  accompanist.user_id = person.user_id
			inner join vote on vote.user_id = person.user_id 
			where person.is_acm=True order by person.name asc"""
	cur.execute(sql)
	profiles=cur.fetchall()
	repertoires=[]
	for profile in profiles:
		sql="select composer.surname from acm_comp inner join composer on acm_comp.composer_id=composer.composer_id where acm_comp.acm_id ={}".format(profile[7])
		cur.execute(sql)
		rep=cur.fetchall()
		repertoires.append(rep)
	cur.execute("select city from accompanist group by city order by city asc")
	cities = cur.fetchall()
	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles, cities = cities, composers = composers, repertoires=repertoires)

@app.route("/list_profiles/filter_by_city/<city_name>")
def filter_by_city(city_name):
	print(city_name)
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score,person.user_id
			from person, accompanist, vote
			where (person.is_acm=True and accompanist.user_id = person.user_id and vote.user_id = person.user_id and accompanist.city ='{}') order by person.name asc""" .format(city_name)
	cur.execute(sql)
	profiles=cur.fetchall()
	repertoires=[]
	for profile in profiles:
		sql="select composer.surname from acm_comp inner join composer on acm_comp.composer_id=composer.composer_id where acm_comp.acm_id ={}".format(profile[7])
		cur.execute(sql)
		rep=cur.fetchall()
		repertoires.append(rep)
	cur.execute("select city from accompanist group by city order by city asc")
	cities = cur.fetchall()
	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles, cities = cities, composers = composers, repertoires=repertoires)

@app.route("/list_profiles/filter_by_composer/<composer_surname>")
def filter_by_composer(composer_surname):
	sql = "select composer_id from composer where surname='%s'"%composer_surname
	cur.execute(sql)
	comp_id = cur.fetchone()
	sql = """SELECT m1.name, m1.surname, m1.username, m1.city, m1.price, m1.vote, m1.score,m1.user_id 
			FROM acm_comp INNER JOIN 
				(select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score, person.user_id, person.is_acm 
				from person inner join accompanist on accompanist.user_id = person.user_id
				inner join vote on vote.user_id = person.user_id) AS m1 ON m1.user_id = acm_comp.acm_id
			WHERE m1.is_acm=True AND acm_comp.composer_id = {} order by m1.name asc""".format(comp_id[0]) 
	cur.execute(sql)
	profiles=cur.fetchall()
	repertoires=[]
	for profile in profiles:
		sql="select composer.surname from acm_comp inner join composer on acm_comp.composer_id=composer.composer_id where acm_comp.acm_id ={}".format(profile[7])
		cur.execute(sql)
		rep=cur.fetchall()
		repertoires.append(rep)
	cur.execute("select city from accompanist group by city order by city asc")
	cities = cur.fetchall()
	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles, cities = cities, composers = composers, repertoires=repertoires)

@app.route("/list_profiles/filter_by_price")
def filter_by_price():
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score,person.user_id
			from person inner join accompanist on accompanist.user_id = person.user_id
			inner join vote on vote.user_id = person.user_id
			where person.is_acm=True order by accompanist.price"""
	cur.execute(sql)
	profiles=cur.fetchall()
	repertoires=[]
	for profile in profiles:
		sql="select composer.surname from acm_comp inner join composer on acm_comp.composer_id=composer.composer_id where acm_comp.acm_id ={}".format(profile[7])
		cur.execute(sql)
		rep=cur.fetchall()
		repertoires.append(rep)
	cur.execute("select city from accompanist group by city order by city asc")
	cities = cur.fetchall()
	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles, cities = cities, composers = composers, repertoires=repertoires)

@app.route("/profile/<username>/comment", methods=['GET', 'POST'])
@login_required
def new_comment(username):
	form=CommentForm()
	if form.validate_on_submit():
		sql ="insert into comments (acm_id,customer_id,com_content,com_date) values (%s,%s,%s,%s)"
		
		sql_2 = "select user_id from person where username = '%s'" %username
		cur.execute(sql_2)
		acm_id = cur.fetchone()
		
		sql_3 = "select user_id from person where username='%s'" %(current_user.username)
		cur.execute(sql_3)
		customer_id = cur.fetchone()
		
		com_content = form.content.data
		time = date.today().strftime("%Y/%m/%d")
		
		cur.execute(sql,(int(acm_id[0]),int(customer_id[0]),com_content,time))
		con.commit()
		flash("Comment added to accompanist.")
		return redirect(url_for('profile', title = "Profile", username = username))
	return render_template('comment.html', title='Comment', form=form)

@app.route("/profile/<username>/reservation", methods=['GET', 'POST'])
@login_required
def new_reservation(username):
	form=ReservationForm()
	if form.validate_on_submit():
		sql_2 = "select user_id from person where username = '%s'" %username
		cur.execute(sql_2)
		acm_id = cur.fetchone()

		sql = "insert into reservation (acm_id, rsr_date, city,content) values ({},'{}','{}', '{}')".format(acm_id[0],form.date.data,form.city.data, form.content.data)
		cur.execute(sql)
		con.commit()
		flash('Reservation is added to accompanist.')
		return redirect(url_for('profile', title = "Profile", username = username))
	return render_template('reservation.html', title='Reservation', form=form)

@app.route("/profile/<username>/experience", methods=['GET', 'POST'])
@login_required
def new_experience(username):
	form=ExperienceForm()
	if form.validate_on_submit():
		sql_2 = "select user_id from person where username = '%s'" %username
		cur.execute(sql_2)
		acm_id = cur.fetchone()

		sql = "insert into experience (acm_id, exp_year, city) values ({},'{}','{}')".format(acm_id[0],form.year.data,form.city.data)
		cur.execute(sql)
		con.commit()
		flash('Experience is added.')
		return redirect(url_for('profile', title = "Profile", username = username))
	return render_template('experience.html', title='Experience', form=form, min_year=1900, max_year=datetime.now().year)

@app.route("/profile/<username>/<int:like>")
@login_required
def like(username, like):
	sql = "select user_id from person where username = '%s'" %username
	cur.execute(sql)
	acm_id = cur.fetchone()
	
	sql3 = "select vote, score from vote where user_id = {}".format(acm_id[0])
	cur.execute(sql3)
	vote_info = cur.fetchone()

	new_vote = vote_info[0]+1
	if(vote_info[1] is None):
		new_score = like
	else:
		new_score = (vote_info[1]*vote_info[0] + like) / new_vote

	sql2 = "update vote set vote = {}, score = {} where user_id = {}".format(new_vote, new_score, acm_id[0])
	cur.execute(sql2)
	con.commit()
	return redirect(url_for('profile', title = "Profile", username = username))

@app.route("/addlist/<username>")
@login_required
def add_list(username):
	sql = "select user_id from person where username = '%s'" %username
	cur.execute(sql)
	acm_id = cur.fetchone()
	print(acm_id)

	sql2= "select is_acm , user_id from person where username = '%s'" %current_user.username
	cur.execute(sql2)
	is_acm = cur.fetchone()
	print(is_acm)

	sql3 = "select * from acm_cust where customer_id = {} and acm_id = {}".format(is_acm[1], acm_id[0])
	cur.execute(sql3)
	added = cur.fetchone()

	if(added is None):
		sql3 = "insert into acm_cust (acm_id,customer_id) values({},{})".format(acm_id[0], is_acm[1])
		cur.execute(sql3)
		con.commit()
		flash('Accompanist is added to your list.')
	
	else:
		flash('You have added this accompanist before.')
	
	return redirect(url_for('profile', title = "Profile", username = username))

@app.route("/update/<username>", methods=['GET', 'POST'])
@login_required
def update_account(username):
	sql="select user_id, name, surname, username, mail from person where username = '{}'".format(username)
	cur.execute(sql)
	info = cur.fetchone()
	form = UpdateForm()
	if form.validate_on_submit():
		sql = "update person set name = '{}', surname = '{}', username = '{}', mail = '{}' where user_id = {}".format(form.name.data, form.surname.data, form.username.data, form.mail.data, info[0])
		cur.execute(sql)
		con.commit()
		flash("Informations updated.")
		return redirect(url_for('account', username=username))
	elif request.method == 'GET':
		form.name.data = info[1]
		form.surname.data=info[2]
		form.username.data = info[3]
		form.mail.data = info[4]
	return render_template('update.html', title ="Update", form=form)

@app.route("/delete/<username>", methods=['POST'])
@login_required
def delete_acc(username):
	sql = "delete from person where username = '{}'".format(username)
	cur.execute(sql)
	con.commit()
	flash('Your account has been deleted')
	return redirect(url_for('home'))

@app.route("/update_acm/<username>", methods=['GET', 'POST'])
@login_required
def update_acm(username):
	sql="select user_id, name, surname, username, mail from person where username = '{}'".format(username)
	cur.execute(sql)
	info = cur.fetchone()
	
	sql = """select surname from composer left join 
				(select composer.composer_id from acm_comp 
				inner join composer on composer.composer_id = acm_comp.composer_id where acm_comp.acm_id = {}) 
				as m1 on composer.composer_id = m1.composer_id where m1.composer_id is NULL order by surname""".format(info[0])
	cur.execute(sql)
	composers = cur.fetchall()

	form = UpdateAcm()

	sql = "select phone_num, city, university, price from accompanist where user_id = {}".format(info[0])
	cur.execute(sql)
	infos = cur.fetchone()

	if form.validate_on_submit():
		sql = "update person set name = '{}', surname = '{}', username = '{}', mail = '{}' where user_id = {}".format(form.name.data, form.surname.data, form.username.data, form.mail.data, info[0])
		cur.execute(sql)
		con.commit()
		sql = "update accompanist set phone_num = '{}', city='{}', university = '{}', price = '{}' where user_id = {}".format(form.phone.data, form.city.data, form.university.data, form.price.data, info[0])
		cur.execute(sql)
		con.commit()
		if request.method == 'POST':
			selected = request.form.getlist('composer')
			for selection in selected:
				sql = "select composer_id from composer where surname = '%s'"%selection
				cur.execute(sql)
				comp_id =cur.fetchone()
				sql = "insert into acm_comp (acm_id, composer_id) values({},{})".format(info[0],comp_id[0])
				cur.execute(sql)
			con.commit()
			flash('Informations are added.')
			return redirect(url_for('home'))
	elif request.method =='GET':
		form.name.data=info[1]
		form.surname.data = info[2]
		form.username.data = info[3]
		form.mail.data = info[4]
		form.phone.data = infos[0]
		form.city.data = infos[1]
		form.university.data = infos[2]
		form.price.data = infos[3] 
	return render_template('update_acm.html', composers = composers, title = "Update Information", form = form)

@app.route("/add_comp", methods=['GET', 'POST'])
@login_required
def add_composer():
	form=ComposerForm()
	if form.validate_on_submit():
		sql = "select * from composer where name = '{}' and surname = '{}'".format(form.name.data,form.surname.data)
		cur.execute(sql)
		isin = cur.fetchone()
		if isin is None:
			sql ="insert into composer (name,surname) values (%s,%s)"
			cur.execute(sql,(form.name.data,form.surname.data))
			con.commit()
			flash("Composer is added")
			return redirect(url_for('home'))
		flash('This composer is already in database.')
	return render_template('add_comp.html', title='Composer', form=form)

@app.route("/delete_exp/<username>", methods=['GET','POST'])
@login_required
def delete_exp(username):
	sql ="select user_id from person where username='{}'".format(username)
	cur.execute(sql)
	user_id=cur.fetchone()
	form=ExperienceForm()
	if form.validate_on_submit():
		sql = "select * from experience where acm_id={} and city = '{}' and exp_year ={}".format(user_id[0],form.city.data,form.year.data)
		cur.execute(sql)
		isin = cur.fetchone()
		if isin is not None:
			sql = "delete from experience where acm_id={} and city = '{}' and exp_year ={}".format(user_id[0],form.city.data,form.year.data)
			cur.execute(sql)
			con.commit()
			flash('Your experience has been deleted.')
			return redirect(url_for('profile', title="Profile", username=username))
		flash('No such experience.')
	return render_template('experience.html', title='Experience', form=form, min_year=1900, max_year=datetime.now)

@app.route("/delete_rsr/<username>", methods=['GET','POST'])
@login_required
def delete_rsr(username):
	sql ="select user_id from person where username='{}'".format(username)
	cur.execute(sql)
	user_id=cur.fetchone()
	form=ReservationForm()
	if form.validate_on_submit():
		sql="select * from reservation where acm_id={} and city ='{}' and rsr_date ='{}'".format(user_id[0],form.city.data,form.date.data)
		cur.execute(sql)
		isin = cur.fetchone()
		if isin is not None:
			sql = "delete from reservation where acm_id={} and city = '{}' and rsr_date ='{}'".format(user_id[0],form.city.data,form.date.data)
			cur.execute(sql)
			con.commit()
			flash('Your reservation has been deleted.')
			return redirect(url_for('profile',username=username))
		flash('No such reservation.')
	return render_template('reservation.html', title='Reservation', form=form)

@app.route("/list_rsr/<username>/", methods=['GET','POST'])
@login_required
def list_rsr(username):
	sql ="select user_id from person where username='{}'".format(username)
	cur.execute(sql)
	user_id=cur.fetchone()
	sql = "select city,rsr_date,content from reservation where acm_id={}".format(user_id[0])
	cur.execute(sql)
	list_rsr = cur.fetchall()
	return render_template('list_rsr.html', list=list_rsr, user=username, title="List Reservation")

@app.route("/update_rsr/<username>/<city>/<date>", methods=['GET','POST'])
@login_required
def update_rsr(username,city,date):
	sql ="select user_id from person where username='{}'".format(username)
	cur.execute(sql)
	user_id=cur.fetchone()
	sql="select city,rsr_date,content,reservation_id from reservation where acm_id={} and city ='{}' and rsr_date ='{}'".format(user_id[0],city,date)
	cur.execute(sql)
	isin = cur.fetchone()
	form=ReservationForm()
	if isin is not None:
		if form.validate_on_submit():
			sql = "update reservation set city = '{}', rsr_date = '{}', content = '{}' where reservation_id = {} and acm_id={}".format(form.city.data, form.date.data, form.content.data, isin[3], user_id[0])
			cur.execute(sql)
			con.commit()
			flash('Reservation updated.')
			return redirect(url_for('profile',username=username))
		elif request.method == 'GET':
			form.city.data = isin[0]
			form.date.data=isin[1]
			form.content.data = isin[2]
			return render_template('update_rsr.html', title ="Update", form=form)
	flash('No such reservation.')
	return redirect(url_for('profile',username=username))








