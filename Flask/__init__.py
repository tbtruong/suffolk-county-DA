from flask import Flask, request, redirect, url_for, flash, render_template 
from pymongo import MongoClient


app = Flask(__name__) 


client = MongoClient("mongodb://127.0.0.1:27017")
db = client.COURT_CASES
cases = db.cases
