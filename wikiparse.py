import wikipediaapi
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import requests
import re

from razdel import sentenize


WIKI_AGENT = wikipediaapi.Wikipedia(
    user_agent='XIX (k.s.yarygin@gmail.com)',
    language='ru',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

def renorm(text):
    return re.sub(r'\s+', ' ', text)


def split_sentences_razdel(text):
    return [sentence.text for sentence in sentenize(text)]

def is_person(page):
    """
    Проверяет, является ли статья о человеке по категориям
    """
    person_categories = {'рождения', 'смерти', 'персоналии', 'люди'}

    # Проверяем категории страницы
    for category in page.categories.values():
        category_title = category.title.lower()
        if any(keyword in category_title for keyword in person_categories):
            return True

    return False


def find_context(text, target):
    # text =

    # Экранируем специальные символы для regex
    # escaped_link = re.escape(target_link)

    # Ищем все вхождения ссылки (как отдельное слово)
    # pattern = r'\b' + escaped_link + r'\b'

    return [
        sentence
        for sentence in split_sentences_razdel(text)
        if target in sentence
    ]


def get_wiki_markup_directly(page_title):
    """
    Получает сырую разметку напрямую через MediaWiki API
    """
    url = "https://ru.wikipedia.org/w/api.php"

    headers = {'User-Agent': 'XIX (k.s.yarygin@gmail.com)'}

    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': page_title,
        'rvprop': 'content',
        'format': 'json',
        'rvslots': 'main'
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()


    pages = data.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        if page_id != '-1':  # Страница существует
            revisions = page_data.get('revisions', [])
            if revisions:
                markup_text = revisions[0].get('slots', {}).get('main', {}).get('*', '')

    link_pattern = r'(\[\[([^\]]+?)(?:\|([^\]]+?))?\]\])'

    return [
        (article_part, renorm(display_part)) if display_part
        else (article_part, article_part)
        for full_match, article_part, display_part in re.findall(link_pattern, markup_text)
    ]


def check_exist(page):
    try:
        return page.exists()
    except:
        return False


if __name__ == '__main__':
    raw_names = pd.read_csv('graph_data/nodes.csv', sep = ';')['full_name'].tolist()
    for i, raw_name in list(enumerate(raw_names))[32:]:
        main_page = WIKI_AGENT.page(raw_name)
        try:
            main_page.fullurl
        except:
            continue
        print(i, main_page.title)
        person2mention = defaultdict(list)
        get_wiki_markup_directly(main_page.title)
        for article, text_part in tqdm(get_wiki_markup_directly(main_page.title)):
            link_page = WIKI_AGENT.page(article)
            if check_exist(link_page) and is_person(link_page):
                link_page.fullurl
                person2mention[link_page.title].append(text_part)
        output_records = []
        for link_title, text_parts in person2mention.items():
            context_list = [
                sentence
                for text_part in text_parts
                for sentence in find_context(main_page.text, text_part)
            ]
            context = renorm(' ... | ... '.join(context_list))
            if context:
                output_records.append((raw_name, main_page.title, link_title, len(context_list), context))
        df_output = pd.DataFrame.from_records(
            output_records,
            columns=['raw_name', 'main_title', 'link_title', 'n', 'context']
        )
        df_output.to_csv('wikilinks.csv', sep = ';', index=False, mode='a', header=False)
