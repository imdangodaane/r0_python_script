import sys
import bs4
import pprint

pp = pprint.PrettyPrinter(indent=4)

def get_file_name():
  try:
    return sys.argv[1]
  except IndexError:
    print('Please specify filename!')


def extract_name_id_aegis_type(data):
  type_ref = {
    'Weapon': 'IT_WEAPON'
  }
  subtype_ref = {
    'One-Handed Sword': 'W_1HSWORD',
    'Mace': 'W_MACE',
    'Staff': 'W_STAFF',
  }
  ii = {}
  ii['Name'] = data[0][0].replace('_', ' ')
  if '[' in ii['Name']:
    idx = ii['Name'].index('[')
    ii['Name'] = ii['Name'][:idx]
  data[1][0] = data[1][0].replace('\n', '')
  data[1][0] = data[1][0].replace('\t', '')
  data[1][0] = data[1][0].replace(' ', '')
  ii['Id'] = data[1][0].split('-')[0]
  ii['AegisName'] = data[1][0].split('-')[1]
  ii['RawType'] = data[2][0].split(' - ')[0]
  ii['Type'] = type_ref[data[2][0].split(' - ')[0]]
  ii['RawSubtype'] = data[2][0].split(' - ')[1]
  ii['Subtype'] = subtype_ref[data[2][0].split(' - ')[1]]
  pp.pprint(ii)
  return ii


def extract_w8_buy_sell_refinable_elocation(data):
  refinable_ref = {
    'Yes': True,
    'No': False,
  }
  loc_ref = {
    'Main Hand': 'EQP_WEAPON'
  }
  ii = {}
  ii['Weight'] = int(data[0][0]) * 10
  ii['Buy'] = data[1][0].split(' z')[0]
  ii['Sell'] = data[2][0].split(' z')[0]
  ii['Refinable'] = refinable_ref[data[3][0]]
  ii['Loc'] = loc_ref[data[4][0]]
  pp.pprint(ii)
  return ii


def extract_range_def_atk_matk_wlvl_slot(data):
  ii = {}
  ii['Range'] = data[0][0]
  ii['Def'] = data[1][0]
  ii['Atk'] = data[2][0]
  ii['Matk'] = data[3][0]
  ii['WeaponLv'] = data[4][0]
  ii['Slots'] = data[5][0]
  pp.pprint(ii)
  return ii


def extract_elvl_usage_trade_job_gender(data):
  gender_ref = {
    'Any': 2
  }
  ii = {}
  ii['EquipLv'] = data[0][0].split('\n')[0]
  usable_jobs = data[4][0].split(' / ')
  ii['Job'] = {}
  for job in usable_jobs:
    ii['Job'][job] = 'true'
  ii['Gender'] = gender_ref[data[5][0]]
  pp.pprint(ii)
  return ii


def extract_item_script(data):
  ii = {}
  script_list = data[1][0].replace('\n ', '\n')
  script_list = script_list.split('\n')
  ii['Script'] = script_list
  pp.pprint(ii)
  return ii


def print_item_db(data):
  print('{')
  print('  Id: {}'.format(data['Id']))
  print('  AegisName: {}'.format(data['AegisName']))
  print('  Name: {}'.format(data['Name']))
  print('  Type: {}'.format(data['Type']))
  print('  Buy: {}'.format(data['Buy']))
  print('  Weight: {}'.format(data['Weight']))
  print('  Atk: {}'.format(data['Atk']))
  print('  Range: {}'.format(data['Range']))
  print('  Slots: {}'.format(data['Slots']))
  print('  Job: {')
  for job in data['Job']:
    print('    {}: true'.format(job))
  print('  }')
  print('  Loc: {}'.format(data['Loc']))
  print('  WeaponLv: {}'.format(data['WeaponLv']))
  print('  EquipLv: {}'.format(data['EquipLv']))
  print('  Subtype: {}'.format(data['Subtype']))
  print('  Script": <"')
  for script in data['Script']:
    print('    {}'.format(script))
  print('  ">')
  print('},')


def print_lua_client(data):
  class_num_ref = {
    'One-Handed Sword': 2,
    'Mace': 62,
    'Staff': 10,
  }

  print('  [{}] = '.format(data['Id']), end='')
  print('{')
  print('    unidentifiedDisplayName = "Unidentified {}",'.format(data['RawType']))
  print('    unidentifiedResourceName = "",')
  print('    unidentifiedDescriptionName = { "Can be identified by using a ^990099Magnifier^000000." }')
  print('    identifiedDisplayName = "{}",'.format(data['Name']))
  print('    identifiedResourceName = "",')
  print('    identifiedDescriptionName = {')
  
  normal_desc = []
  desc_requirements = []

  for i in range(len(data['Description'])):
    if ':' in data['Description'][i]:
      normal_desc = data['Description'][:i]
      desc_requirements = data['Description'][i:]
      break

  for desc in normal_desc:
    print('      "{}",'.format(desc))

  print('      "________________________",')

  desc_requirements = list(filter(lambda x: x, desc_requirements))
  for desc in desc_requirements:
    if ":" in desc:
      print('      "^0000CC{}^000000'.format(desc), end=' ')
    else:
      if desc == desc_requirements[-1]:
        print('{}"'.format(desc))
      else:
        print('{}",'.format(desc))
  print('    },')

  print('    slotCount = {},'.format(data['Slots']))
  print('    ClassNum = {}'.format(class_num_ref[data['RawSubtype']]))
  print('  },')


def get_item_description(soup):
  raw_desc = soup.find('div', { 'class': 'media-body' })
  desc = raw_desc.findChildren(text=True)
  desc_list = []
  for row in desc:
    desc_list.append(row.strip())
  return desc_list


def bs4_parsing(filename):
  with open(filename, encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f, 'html.parser')
    tables = soup.findAll('table')
    ii = {}
    ii['Description'] = get_item_description(soup)
    for i, table in enumerate(tables):
      rows = table.findAll('tr')
      data = [[td.findChildren(text=True) for td in  tr.findAll('td')] for tr in rows]
      data = [[u"".join(d).strip() for d in l] for l in data]
      if i == 0:
        ii.update(extract_name_id_aegis_type(data))
      if i == 1:
        ii.update(extract_w8_buy_sell_refinable_elocation(data))
      if i == 2:
        ii.update(extract_range_def_atk_matk_wlvl_slot(data))
      if i == 3:
        ii.update(extract_elvl_usage_trade_job_gender(data))
      if i == 4:
        ii.update(extract_item_script(data))

    print_item_db(ii)
    print_lua_client(ii)


def main():
  filename = get_file_name()
  if not filename:
    return
  else:
    print('Filename: {}'.format(filename))

  bs4_parsing(filename)

if __name__ == '__main__':
  main()