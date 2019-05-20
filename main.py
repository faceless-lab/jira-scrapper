from jira import JIRA
import csv
import re
import time

from jira.exceptions import JIRAError

no_format = re.compile(r'{(code|noformat}).*?(code|noformat)}')
no_inline = re.compile(r'{{.*?}}')
no_xml = re.compile(r'<[^>]+>')
no_logs = re.compile(r'(\\d{4}-\\d{2}-\\d{2}) (\\d{2}:\\d{2}:\\d{2},\\d{3}) \\[(.*)\\] ([^ ]*) +([^ ]*) - (.*)$')
no_stacktrace = re.compile(r'(at)\ (\w+[a-z]\.\w+.*)|(Caused by:).*|(...)\ \d+\ (more)')
no_url = re.compile(r'http\S+')

timeout = 60


def sanitize(text: str):
    text = text.replace('\n', ' ').replace('\r', '')
    text = no_format.sub('', text)
    text = no_inline.sub('', text)
    text = no_stacktrace.sub('', text)
    text = no_xml.sub('', text)
    text = no_logs.sub('', text)
    text = no_url.sub('', text)
    return text


if __name__ == '__main__':
    client = JIRA(server='https://jira.nuxeo.com')

    all_fields = client.fields()
    custom_sp = [field['id'] for field in all_fields if field['name'].lower() == "story points"]

    if len(custom_sp) == 0:
        exit(1001)
    elif len(custom_sp) > 1:
        exit(2001)

    custom_sp = custom_sp[0]
    headers = ['project', 'description', 'points']
    with open("data/issues.csv", 'w+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, escapechar='\\', quotechar='"')
        writer.writerow(headers)

        counter = 0
        at_once = 100
        start = 0
        attempts = 3
        while True:
            issues = []
            try:
                issues = client.search_issues(
                    '"Story Points" != EMPTY AND "Story Points" != 0',
                    startAt=start, maxResults=at_once
                )
            except JIRAError as e:
                print('Cannot search issues: {}'.format(e.status_code))
                break

            if len(issues) == 0 and attempts == 0:
                break

            counter += len(issues)
            written = 0
            for issue in issues:
                if issue is None or issue.fields is None or issue.fields.description is None:
                    attempts -= 1
                    print('Jira is exhausted, give it some time to rest. Sleeping for {} seconds'.format(timeout))
                    time.sleep(timeout)
                    start += at_once / 2
                    break

                s = sanitize(issue.fields.description)
                # print('Sanitize {}'.format(s))
                desc = [issue.fields.summary]
                desc.extend(str(s).split(' '))
                desc_str = ' '.join(desc),

                records = [issue.fields.project.name, desc_str, str(getattr(issue.fields, custom_sp))]
                writer.writerow(records)
                written += 1

            start += at_once
            print('Still pulling some data. Written {} records'.format(start - at_once + written))

        print('Pulled {} issues'.format(counter))

    print('End of ScrappyJ')
