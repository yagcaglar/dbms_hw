from flask import render_template, url_for, flash, redirect, request
from total import app, cur, bcrypt, login_manager, con
from total.forms import RegistrationForm, LoginForm, CommentForm, AddInfoForm,ReservationForm,ExperienceForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import date 
from total.user import get_user

@login_manager.user_loader
def load_user(username):
	return cur.execute("select user_id from person where username = '%s'" %username)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		sql="insert into person (name,surname,username,password,mail,is_acm) values(%s,%s,%s,%s,%s,%s)"
		cur.execute(sql,(form.name.data, form.surname.data, form.username.data, hashed_password, form.email.data, bool(form.is_acm.data)))
		con.commit()
		if bool(form.is_acm.data) == True:
			cur.execute("select user_id from person where username = '%s",(form.username.data))
			user_id = cur.fetchone()
			cur.execute("insert into accompanist (user_id) values(%d)",(user_id))
			cur.execute("insert into vote (user_id) values(%d)",(user_id))
			con.commit()
			flash('Your account has been created please add more information.')
			return redirect(url_for('add_info', username = form.username.data))
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/add_info/<username>", methods=['GET', 'POST'])
def add_info(username):
	sql="select user_id from person where username = '{}'".format(username)
	cur.execute(sql)
	user_id = cur.fetchone()
	print(user_id)
	cur.execute("select surname from composer group by surname")
	composers = cur.fetchall()
	form = AddInfoForm()
	info = "select phone_num, city, university, price from accompanist where user_id = {}".format(user_id[0])
	cur.execute(info)
	infos = cur.fetchone()
	if form.validate_on_submit():
		sql = "update accompanist set phone_num = '{}', city='{}', university = '{}', price = '{}' where user_id = {}".format(form.phone.data, form.city.data, form.university.data, form.price.data, user_id[0])
		cur.execute(sql)
		con.commit()
		if request.method == 'POST':
			selected = request.form.getlist('composer')
			for selection in selected:
				sql = "select composer_id from composer where surname = '%s'"%selection
				cur.execute(sql)
				comp_id =cur.fetchone()
				sql = "insert into acm_comp (acm_id, composer_id) values({},{})".format(user_id[0],comp_id[0])
				cur.execute(sql)
			con.commit()
			flash('Informations are added.')
			return redirect(url_for('home'))
	elif request.method =='GET':
		form.phone.data = infos[0]
		form.city.data = infos[1]
		form.university.data = infos[2]
		form.price.data = infos[3] 
	return render_template('addinfo.html', composers = composers, title = "Add Information", form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	#print(form.username)
	if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first()
		"""sql = "select * from person where username ='%s'" %form.username.data
		cur.execute(sql)
		user = cur.fetchone()"""
		user = get_user(form.username.data)
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			flash('Login Successful.')
			return render_template('home.html', title='Home')
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
	sql = "select * from person where username= '%s'" %username
	cur.execute(sql)
	user = cur.fetchone()
	#sql2 = "select "
	return render_template('account.html', title='Account', account = user)


#city composer price vote filtering
@app.route("/list_profiles")
def list_profiles():
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score
			from person, accompanist, vote
			where (person.is_acm=True and accompanist.user_id = person.user_id and vote.user_id = person.user_id) order by person.name asc"""
	cur.execute(sql)
	profiles=cur.fetchall()
	cur.execute("select city from accompanist group by city order by city asc")
	cities = cur.fetchall()
	cur.execute("select surname from composer group by surname order by surname asc")
	composers = cur.fetchall()	
	return render_template('list_profiles.html', title='Profiles', profiles=profiles, cities = cities, composers = composers)

@app.route("/list_profiles/filter_by_city/<city_name>")
def filter_by_city(city_name):
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score
			from person, accompanist, vote
			where (person.is_acm=True and accompanist.user_id = person.user_id and vote.user_id = person.user_id and accompanist.city ='{}')""" .format(city_name[0])
	print(sql)
	cur.execute(sql)
	profiles=cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles)

@app.route("/list_profiles/filter_by_composer/<composer_surname>")
def filter_by_composer(composer_surname):
	sql = "select composer_id from composer where surname='%s'"%composer_surname
	cur.execute(sql)
	comp_id = cur.fetchone()
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score 
			from person, accompanist , vote, acm_comp
			where (person.is_acm=True and accompanist.user_id = person.user_id and
					 vote.user_id = person.user_id and acm_comp.acm_id = accompanist.user_id and acm_comp.composer_id = {})""".format(comp_id[0]) 
	cur.execute(sql)
	profiles=cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles)

@app.route("/list_profiles/filter_by_price")
def filter_by_price():
	sql = """select person.name, person.surname, person.username, accompanist.city, accompanist.price, vote.vote, vote.score
			from person, accompanist, vote
			where (person.is_acm=True and accompanist.user_id = person.user_id and vote.user_id = person.user_id) 
			order by accompanist.price"""
	cur.execute(sql)
	profiles=cur.fetchall()
	return render_template('list_profiles.html', title='Profiles', profiles=profiles)

#select * from person right join accompanist on person.user_id = accompanist.user_id;	
#join kullanıp person tablosundan veriye eriş şu an null veriyor her şeye
#iletişim bilgileri, vote
#comment
#repertuvar
@app.route("/profile/<username>")
def profile(username):
	sql = "select user_id from person where username = '%s'" %username
	cur.execute(sql)
	user_id= cur.fetchone()
	if user_id is not None:
		info = """select person.name, person.surname, person.username, accompanist.phone_num, 
			accompanist.mail, accompanist.university, accompanist.city, accompanist.price, vote.vote, vote.score 
			from accompanist, vote, person 
			where accompanist.user_id = {} and person.user_id = {} and vote.user_id = {}""".format(user_id[0], user_id[0], user_id[0])
		cur.execute(info)
		user_info = cur.fetchone()

		repertoire_info = """select composer.surname from acm_comp, composer, accompanist
							where accompanist.user_id = {}  and  acm_comp.acm_id = accompanist.user_id""".format(user_id[0])
		cur.execute(repertoire_info)
		repertoire = cur.fetchall()

		comment_info = """select person.name, person.surname, person.username, comments.com_content, comments.com_date 
						from comments, person 
						where comments.acm_id = %s and comments.customer_id = person.user_id""" %user_id[0]
		cur.execute(comment_info)
		comments = cur.fetchall()

		experience_info = """select experience.exp_year, experience.city from experience, accompanist
							where accompanist.user_id = {} and experience.acm_id = accompanist.user_id""".format(user_id[0])
		cur.execute(experience_info)
		experiences = cur.fetchall()

		reservation_info = """select reservation.rsr_date, reservation.city from reservation, accompanist
							where accompanist.user_id = {} and reservation.acm_id = accompanist.user_id""".format(user_id[0])
		cur.execute(reservation_info)
		reservations = cur.fetchall()

		return render_template('profile.html', title='Profile', user = user_info, comments = comments, repertoire = repertoire, reservations = reservations, experiences = experiences)
	else:
		flash('No such accompanist account.')
		return render_template('home.html', title='Home')
	

@app.route("/profile/<username>/comment", methods=['GET', 'POST'])
def new_comment(username):
	form=CommentForm()
	if form.validate_on_submit():
		sql ="insert into comments (acm_id,customer_id,com_content,com_date) values (%s,%s,%s,%s)"
		
		sql_2 = "select user_id from person where username = '%s'" %username
		cur.execute(sql_2)
		acm_id = cur.fetchone()
		
		sql_3 = "select user_id from person where username='%s'" %(current_user.username if current_user.is_authenticated else 'yagcaglar')
		cur.execute(sql_3)
		customer_id = cur.fetchone()
		
		com_content = form.content.data
		time = date.today().strftime("%m/%d/%Y")
		
		cur.execute(sql,(int(acm_id[0]),int(customer_id[0]),com_content,time))
		con.commit()
		flash("Comment added to accompanist.")
		return redirect(url_for('profile', title = "Profile", username = username))
	return render_template('comment.html', title='Comment', form=form)

@app.route("/profile/<username>/reservation", methods=['GET', 'POST'])
def new_reservation(username):
	form=ReservationForm()
	if form.validate_on_submit():
		sql_2 = "select user_id from person where username = '%s'" %username
		cur.execute(sql_2)
		acm_id = cur.fetchone()

		sql = "insert into reservation (acm_id, rsr_date, city) values ({},'{}','{}')".format(acm_id[0],form.date.data,form.city.data)
		cur.execute(sql)
		con.commit()
		flash('Reservation is added to accompanist.')
		return redirect(url_for('profile', title = "Profile", username = username))
	return render_template('reservation.html', title='Reservation', form=form)

@app.route("/profile/<username>/experience", methods=['GET', 'POST'])
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
	return render_template('experience.html', title='Experience', form=form)











