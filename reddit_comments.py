import praw
from praw.models import MoreComments
import psycopg2
import config

#Connecting to database
con = psycopg2.connect(
	user = config.dbusername(),
	password = config.dbpassword(),
	host = config.host(),
	port = config.port(),
	database = config.dbname()
	)

#Connecting to reddit
reddit = praw.Reddit(
	client_id=config.reclientid(),
	client_secret=config.reclientsecret(),
	password=config.repassword(),
	username=config.reusername(),
	user_agent=config.reagent()
)

#This list holds all the thread ID's to use for later
id_list = []

for submission in reddit.subreddit("stocks").top('year', limit=200):
	id_list.append(str(submission.id))

cur = con.cursor()

#Goes through each thread gets comments and commits them to a database.
for i in id_list:
	submission = reddit.submission(id=i)
	submission.comments.replace_more(limit=20)
	for comment in submission.comments.list():
		try:
			insert = "INSERT INTO stocks(comment, date, post_id) VALUES (%s, %s, %s)"
			cur.execute(insert, (comment.body, comment.created_utc, i))
			con.commit()
		except Exception as e:
			print(e)

con.close()

print("Closing database.")