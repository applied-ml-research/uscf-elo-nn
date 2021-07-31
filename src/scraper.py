import bs4
import requests

URL = 'http://www.uschess.org/datapage/event-search.php?name=&state=ANY&city=&date_from=&date_to=&order=D&minsize=50&affil=&timectl=&rsys=ANY&mode=Find'

def main():
  page = requests.get(URL)
  soup = bs4.BeautifulSoup(page.content, 'html.parser')

  def getTables(elem):
    return bs4.BeautifulSoup(requests.get(elem['href'] + '.0').content, 'html.parser').find_all('pre')

  tables = [table for tournaments in soup.find('tbody').find_all('a', href=True) for table in getTables(tournaments)]

  results = []
  for table in tables:
    table_tuple = tuple(table)
    data = {} 
    rank = 1
    for line in range(len(table_tuple)):
      string = table_tuple[line].string 
      if string == str(rank):
        data[rank] = [None, []]
        raw = table_tuple[line + 3]
        proc = raw.split('|')[2:]

        # scores
        for elem in proc:
          if elem[0] == 'W':
            pts = 1.0
          elif elem[0] == 'L':
            pts = 0.0
          elif elem[0] == 'D':
            pts = 0.5
          else:
            break
          versus = int(''.join([c for c in elem if c.isdigit()]))
          data[rank][1].append((versus, pts))

        # rating parsing
        ratings = {
          'start': '',
          'end': '',
          'provisional': '',
        }
        parse_on = 'start'
        index = 0
        rating_string = raw.split(':')[-1].split('|')[0].strip()
        while index < len(rating_string):
          char = rating_string[index]
          if char.isdigit():
            ratings[parse_on] += char
          elif char == 'P':
            if parse_on == 'end':
              index = len(rating_string)
            parse_on = 'provisional'
          else:
            parse_on = 'end'
            if ratings[parse_on] != '':
              index = len(rating_string)
          index += 1
        for key in ratings:
          if ratings[key] != '':
            ratings[key] = int(ratings[key])
          else:
            ratings[key] = None
        data[rank][0] = ratings

        rank += 1
    results.append(data)

  print(results)

if __name__ == '__main__':
  main()

