from jira import JIRA
import re

options = {'server': 'https://jira.nuxeo.com/'}

jira = JIRA(options)

issue = jira.issue('NXP-24421')

# her = jira.search_issues('"Story Points" is not EMPTY', maxResults=100)

# customfield_10492 - Story Points

# print(issue.fields.customfield_10492)

# print(issue.fields.project)

testStr = issue.fields.description
print(testStr)
print(re.sub('\{.+\}', '', testStr))
