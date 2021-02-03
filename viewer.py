from flask import Flask, request, Response, redirect, render_template
from flask_paginate import Pagination, get_page_args
from flaskext.markdown import Markdown
import requests
import issues
import datetime

app = Flask(__name__)

Markdown(app)

# reloads templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# makes a get request and saves json data to issues file
issues_data = requests.get("https://api.github.com/repos/walmartlabs/thorax/issues")
issues = issues_data.json()

# get issues from local python file
#this funcyion splits pages
def get_issues(offset=0, per_page=10):
    return issues[offset: offset + per_page]

@app.template_filter()
def format_time(value):
    time = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').strftime("%b %d %Y")
    return time

@app.route('/', methods=['POST', 'GET'])
def main_page():
    # get the current page number, issues per page, and current offset
    # pylint: disable=unbalanced-tuple-unpacking
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', offset="offset")

    #get issues from the current_page
    page_sequence_issues = get_issues(offset=offset, per_page=per_page)
    page_sequence = page_sequence(page=page, per_page=per_page, total=len(issues), css_framework="bootstrap4")

    return render_template("issue_browser.html", issues=page_sequence_issues, page_sequence=page_sequence)

@app.route('/issue_description')
def issue_description():
    # By the issue detail link it gets the issue id
    issue_id = request.args.get("id", None)

    # By looking it up in id by the list it isolates the issues
    issue = [issue for issue in issues if int(issue["id"]) == int(issue_id)][0]

    # comments in the issues
    comments = requests.get(issue["comments_url"]).json()

    #returns issue detail, issue and comments
    return render_template("issue_description.html", issue=issue, comments=comments)
