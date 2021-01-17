from server import cur,con

def create_db():
    sql1 = """CREATE DOMAIN SCORES AS FLOAT CHECK ((VALUE>=1.0) AND (VALUE<=5.0));
            CREATE TABLE PERSON(
                USER_ID SERIAL PRIMARY KEY,
                NAME VARCHAR(20) NOT NULL,
                SURNAME VARCHAR(20) NOT NULL,
                USERNAME VARCHAR(20) NOT NULL,
                PASSWORD VARCHAR(20) NOT NULL,
                IS_ACM BOOLEAN NOT NULL,
                MAIL VARCHAR(100) NOT NULL,
                UNIQUE(MAIL),
                UNIQUE (USERNAME)
            );

            CREATE TABLE ACCOMPANIST(
                USER_ID SERIAL PRIMARY KEY,
                PHONE_NUM VARCHAR(11),
                UNIVERSITY VARCHAR(80),
                CITY VARCHAR(20),
                PRICE INTEGER,
                FOREIGN KEY(USER_ID) REFERENCES PERSON(USER_ID) ON DELETE CASCADE
            );

            CREATE TABLE ACM_CUST(
                ACM_ID INTEGER,
                CUSTOMER_ID INTEGER,
                PRIMARY KEY(ACM_ID,CUSTOMER_ID),
                FOREIGN KEY(ACM_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE,
                FOREIGN KEY(CUSTOMER_ID) REFERENCES PERSON(USER_ID) ON DELETE CASCADE
            );

            CREATE TABLE COMPOSER(
                COMPOSER_ID SERIAL PRIMARY KEY,
                NAME VARCHAR(40) NOT NULL,
                SURNAME VARCHAR(20) NOT NULL
            );

            CREATE TABLE ACM_COMP(
                ACM_ID INTEGER,
                COMPOSER_ID INTEGER,
                PRIMARY KEY(ACM_ID,COMPOSER_ID),
                FOREIGN KEY(ACM_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE,
                FOREIGN KEY(COMPOSER_ID) REFERENCES COMPOSER(COMPOSER_ID) ON DELETE CASCADE
            );

            CREATE TABLE COMMENTS(
                COMMENT_ID SERIAL PRIMARY KEY,
                ACM_ID INTEGER,
                CUSTOMER_ID INTEGER,
                COM_CONTENT VARCHAR(100) NOT NULL,
                COM_DATE DATE,
                FOREIGN KEY(ACM_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE,
                FOREIGN KEY(CUSTOMER_ID) REFERENCES PERSON(USER_ID) ON DELETE CASCADE
            );

            CREATE TABLE EXPERIENCE(
                EXPERIENCE_ID SERIAL PRIMARY KEY,
                ACM_ID INTEGER,
                EXP_YEAR NUMERIC(4) NOT NULL,	
                CITY VARCHAR(20) NOT NULL,
                FOREIGN KEY(ACM_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE
            );

            CREATE TABLE RESERVATION(
                RESERVATION_ID SERIAL PRIMARY KEY,
                ACM_ID INTEGER,
                RSR_DATE DATE NOT NULL,	
                CITY VARCHAR(20) NOT NULL,
                FOREIGN KEY(ACM_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE
            );


            CREATE TABLE VOTE ( 
                USER_ID SERIAL PRIMARY KEY, 
                VOTE INTEGER DEFAULT 0, 
                SCORE SCORES, 
                FOREIGN KEY (USER_ID) REFERENCES ACCOMPANIST(USER_ID) ON DELETE CASCADE);"""
    cur.execute(sql1)
    con.commit()

    sql="""insert into composer (name, surname) values ('Ludwig van', 'Beethoven');
            insert into composer (name, surname) values ('Samuel', 'Barber');
            insert into composer (name, surname) values ('Charles de', 'Bériot');
            insert into composer (name, surname) values ('Johannes', 'Brahms');
            insert into composer (name, surname) values ('Max', 'Bruch');
            insert into composer (name, surname) values ('Antonín', 'Dvořák');
            insert into composer (name, surname) values ('Edward', 'Elgar');
            insert into composer (name, surname) values ('Georg Friedrich', 'Händel');
            insert into composer (name, surname) values ('Joseph', 'Haydn');
            insert into composer (name, surname) values ('Dmitri', 'Kabalevsky');
            insert into composer (name, surname) values ('Aram', 'Khachaturian');
            insert into composer (name, surname) values ('Fritz', 'Kreisler');
            insert into composer (name, surname) values ('Édouard', 'Lalo');
            insert into composer (name, surname) values ('Felix', 'Mendelssohn');
            insert into composer (name, surname) values ('Niccolò', 'Paganini');
            insert into composer (name, surname) values ('Ferdinand', 'Ries');
            insert into composer (name, surname) values ('Camille', 'Saint-Saëns');
            insert into composer (name, surname) values ('Robert', 'Schumann');
            insert into composer (name, surname) values ('Dmitri', 'Shostakovich');
            insert into composer (name, surname) values ('Jean', 'Sibelius');
            insert into composer (name, surname) values ('Pyotr Ilyich', 'Tchaikovsky');
            insert into composer (name, surname) values ('Henri', 'Vieuxtemps');
            insert into composer (name, surname) values ('Giovanni Battista', 'Viotti');
            insert into composer (name, surname) values ('Antonio', 'Vivaldi');
            insert into composer (name, surname) values ('Henryk', 'Wieniawski');
            insert into composer (name, surname) values ('Fritz', 'Kreisler');
            insert into composer (name, surname) values ('Georg Philipp', 'Telemann');
            insert into composer (name, surname) values ('Henri', 'Vieuxtemps');
            insert into composer (name, surname) values ('Claude', 'Debussy');
            insert into composer (name, surname) values ('Ernő', 'Dohnányi');
            insert into composer (name, surname) values ('George', 'Enescu');
            insert into composer (name, surname) values ('César', 'Franck');
            insert into composer (name, surname) values ('Maurice', 'Ravel');
            insert into composer (name, surname) values ('Franz', 'Schubert');
            insert into composer (name, surname) values ('Béla', 'Bartók');
            insert into composer (name, surname) values ('Muzio', 'Clementi');
            insert into composer (name, surname) values ('Frédéric', 'Chopin');
            insert into composer (name, surname) values ('Gabriel', 'Fauré');
            insert into composer (name, surname) values ('George', 'Gershwin');
            insert into composer (name, surname) values ('Edvard', 'Grieg');
            insert into composer (name, surname) values ('Joseph', 'Haydn');
            insert into composer (name, surname) values ('Paul', 'Hindemith');
            insert into composer (name, surname) values ('György', 'Ligeti');
            insert into composer (name, surname) values ('Olivier', 'Messiaen');
            insert into composer (name, surname) values ('Francis', 'Poulenc');
            insert into composer (name, surname) values ('Sergei', 'Prokofiev');
            insert into composer (name, surname) values ('Sergei', 'Rachmaninoff');"""
    cur.execute(sql)
    con.commit()
