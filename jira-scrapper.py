from jira import JIRA

options = {'server': 'https://jira.nuxeo.com/'}

jira = JIRA(options)

issue = jira.issue('NXP-24421')

print(issue.fields.description)