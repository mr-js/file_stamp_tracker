import os
import pathlib
import hashlib
import json
import codecs
import datetime


def create_data_stamp(path = r'C:\Program Files\Huawei\PCManager'):
    data = {'control': {}, 'table' : {}}
    data['control']['path'] = path
    files = os.listdir(path)
    for file in files:
        filename = os.path.join(path, file)
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                hash = hashlib.md5(f.read()).hexdigest()
                data['table'][file] = hash
    data['control']['datestamp'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data['control']['names_checksum'] = hashlib.md5(''.join(file for file, md5 in data['table'].items()).encode('utf-8')).hexdigest()
    data['control']['md5_checksum'] = hashlib.md5(''.join(md5 for file, md5 in data['table'].items()).encode('utf-8')).hexdigest()
    with codecs.open(os.path.join('data', 'stamp_' + data['control']['datestamp'] + '.json'), 'w', 'utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def check_data_stamp(path = 'data'):
    filestamps = []
    files = os.listdir(path)
    for file in files:
        filename = os.path.join(path, file)
        if os.path.isfile(filename) and file.startswith('stamp_') and file.endswith('.json'):
            date = os.path.getctime(filename)
            filestamps.append((file, date))
    filestamps.sort(key = lambda x: x[1], reverse=True)
    if len(filestamps) < 2:
        return 'Not enough stamps'
    with codecs.open(os.path.join(path, filestamps[0][0]), 'r', 'utf-8') as f:
        data_new = json.load(f)
    with codecs.open(os.path.join(path, filestamps[1][0]), 'r', 'utf-8') as f:
        data_old = json.load(f)

    report = {'status': '', 'details': {}}
    if data_new['control']['md5_checksum'] == data_old['control']['md5_checksum']:
        report['status'] = 'No changes'
        return report
    elif data_new['control']['names_checksum'] == data_old['control']['names_checksum'] and data_new['control']['md5_checksum'] != data_old['control']['md5_checksum']:
        report['status'] = 'File list unchanged, but there are changes in files'
    else:
        report['status'] = 'Files added/removed'
    
    report['details'] = {'changed' : [], 'added' : [], 'removed' : []}

    for file in data_old['table']:
        if file not in data_new['table']:
            report['details']['removed'].append(file)
    for file in data_new['table']:
        if file not in data_old['table']:
            report['details']['added'].append(file)
    for file in data_new['table']:
        hash = data_new['table'][file]
        if file in data_old['table'] and hash != data_old['table'][file]:
            report['details']['changed'].append(file)            

    report['data_new_control'] = data_new['control']
    report['data_old_control'] = data_old['control']
    report['datestamp'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with codecs.open(os.path.join('data', 'report_' + report['datestamp'] + '.json'), 'w', 'utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    return report


# DEMO
# create_data_stamp()
report = check_data_stamp()
print(report)